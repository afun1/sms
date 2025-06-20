"""
Flask API Server for SMS Integration with GoHighLevel
Provides webhook endpoints that GHL workflows can call to send SMS messages
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv
from twilio.rest import Client
import re
import json
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
import tempfile
import hashlib
import secrets
from functools import wraps
from multi_provider_sms import MultiProviderSMSManager
from slybroadcast_rvm import SlybroadcastRVM
from simpletalk_ai import SimpleTalkAI
from multi_provider_email import MultiProviderEmailManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure upload folder for static files (logos, etc.)
UPLOAD_FOLDER = 'static'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico'}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Multi-Provider SMS Manager
sms_manager = MultiProviderSMSManager()

# Initialize RVM Manager
rvm_manager = SlybroadcastRVM()

# Initialize Twilio client (backup)
try:
    twilio_client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    logger.info("Twilio client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Twilio client: {e}")
    twilio_client = None

# Initialize SimpleTalk.ai
ai_manager = SimpleTalkAI()

# Initialize Multi-Provider Email Manager
email_manager = MultiProviderEmailManager()

class SMSHandler:
    @staticmethod
    def validate_phone_number(phone):
        """Validate phone number format"""
        clean_phone = re.sub(r'[^\d+]', '', str(phone))
        pattern = r'^\+\d{10,15}$'
        return bool(re.match(pattern, clean_phone))
    
    @staticmethod
    def send_single_sms(phone, message, sender_phone=None):
        """Send a single SMS message using multi-provider system"""
        if not SMSHandler.validate_phone_number(phone):
            return False, f"Invalid phone number format: {phone}"
        
        try:
            # Use multi-provider system
            success, result = sms_manager.send_sms(phone, message)
            return success, result
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {e}")
            return False, str(e)
    
    @staticmethod
    def send_bulk_sms(contacts, default_message, delay=2):
        """Send bulk SMS messages"""
        results = []
        
        for contact in contacts:
            phone = contact.get('phone_number') or contact.get('phone')
            name = contact.get('name', 'Friend')
            custom_message = contact.get('message', '')
            
            # Use custom message if provided, otherwise use default
            message = custom_message if custom_message else default_message
            
            # Replace placeholders
            message = message.replace('{name}', name)
            message = message.replace('{phone}', phone)
            
            # Send SMS
            success, result = SMSHandler.send_single_sms(phone, message)
            
            results.append({
                'phone': phone,
                'name': name,
                'success': success,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"SMS to {phone}: {'✓' if success else '✗'} {result}")
        
        return results

# Simple user database (in production, use a real database)
USERS_DB = {
    'demo': {
        'password': hashlib.sha256('password'.encode()).hexdigest(),
        'role': 'user',
        'username': 'demo'
    },
    'admin': {
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'username': 'admin'
    }
}

# Active sessions (in production, use Redis or database)
ACTIVE_SESSIONS = {}

def generate_token():
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def verify_token(token):
    """Verify if a token is valid and return user info"""
    return ACTIVE_SESSIONS.get(token)

def require_auth(role=None):
    """Decorator to require authentication for routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_info = verify_token(token)
            if not user_info:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            if role and user_info['role'] != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            request.current_user = user_info
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# API Routes

@app.route('/', methods=['GET'])
def home():
    """Landing page - serve login page for HTML requests, JSON for API clients"""
    
    # Check if request wants HTML (from browser) or JSON (from API client)
    if 'text/html' in request.headers.get('Accept', ''):
        # Serve the login page as the landing page
        try:
            with open('login.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to JSON if HTML file not found
            pass
    
    # Return JSON for API clients
    return jsonify({
        'service': 'Sparky Messaging API',
        'version': '1.0.0',
        'description': 'Multi-Channel Marketing Powerhouse: SMS + Email + RVM + AI-Powered Content Generation',
        'channels': ['SMS', 'Email', 'RVM', 'AI Content'],
        'providers': {
            'SMS': ['Twilio', 'ClickSend', 'TextBelt'],
            'Email': ['Gmail', 'SendGrid', 'Mailgun', 'Amazon SES', 'ClickSend'],
            'RVM': ['Slybroadcast'],
            'AI': ['SimpleTalk.ai']
        },
        'endpoints': {
            'POST /api/sms/send': 'Send single SMS',
            'POST /api/sms/bulk': 'Send bulk SMS from contact list',
            'POST /api/sms/csv': 'Send bulk SMS from CSV data',
            'POST /api/rvm/send': 'Send single RVM',
            'POST /api/rvm/bulk': 'Send bulk RVM campaigns',
            'POST /api/multi/send': 'Send SMS + RVM simultaneously',
            'GET /api/usage': 'Get SMS usage statistics',
            'GET /api/capacity': 'Get remaining daily capacity',
            'GET /api/health': 'Health check',
            'GET /api/webhook/ghl': 'GHL webhook documentation',
            'POST /api/login': 'User login',
            'POST /api/logout': 'User logout',
            'GET /api/admin': 'Admin dashboard (protected)'
        },
        'status': 'active',
        'providers_configured': len([p for p in sms_manager.providers if p.enabled]),
        'rvm_configured': rvm_manager.is_configured()
    })

# Routes for serving editor pages
@app.route('/sms_editor.html')
def sms_editor():
    """Serve SMS Editor page"""
    try:
        with open('sms_editor.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "SMS Editor page not found", 404

@app.route('/email_editor.html')
def email_editor():
    """Serve Email Editor page"""
    try:
        with open('email_editor.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Email Editor page not found", 404

@app.route('/rvm_editor.html')
def rvm_editor():
    """Serve RVM Editor page"""
    try:
        with open('rvm_editor.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "RVM Editor page not found", 404

@app.route('/ai_editor.html')
def ai_editor():
    """Serve AI Editor page"""
    try:
        with open('ai_editor.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "AI Editor page not found", 404

@app.route('/campaign_builder.html')
def campaign_builder():
    """Serve Campaign Builder page"""
    try:
        with open('campaign_builder.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Campaign Builder page not found", 404

@app.route('/simple_nav_test.html')
def simple_nav_test():
    """Serve Simple Global Navigation Test page"""
    try:
        with open('simple_nav_test.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Simple Nav Test page not found", 404

@app.route('/test_navigation.html')
def test_navigation():
    """Serve Global Navigation Test page"""
    try:
        with open('test_navigation.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Navigation Test page not found", 404

@app.route('/api/usage', methods=['GET'])
def get_usage_stats():
    """Get SMS usage statistics"""
    try:
        report = sms_manager.get_usage_report()
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/capacity', methods=['GET'])
def get_capacity():
    """Get remaining daily capacity"""
    try:
        total_capacity, available_providers = sms_manager.get_available_capacity()
        
        response = {
            'total_remaining_capacity': total_capacity,
            'available_providers': available_providers,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error getting capacity: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'twilio_configured': twilio_client is not None
    })

@app.route('/api/sms/send', methods=['POST'])
def send_single_sms():
    """
    Send a single SMS message
    Expected JSON payload:
    {
        "phone": "+1234567890",
        "message": "Your message here",
        "name": "John Doe" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        phone = data.get('phone')
        message = data.get('message')
        name = data.get('name', 'Friend')
        
        if not phone or not message:
            return jsonify({'error': 'Phone and message are required'}), 400
        
        # Replace placeholders
        message = message.replace('{name}', name)
        
        success, result = SMSHandler.send_single_sms(phone, message)
        
        response = {
            'success': success,
            'message': result,
            'phone': phone,
            'timestamp': datetime.now().isoformat()
        }        
        return jsonify(response), 200 if success else 400
        
    except Exception as e:
        logger.error(f"Error in send_single_sms: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rvm/send', methods=['POST'])
def send_single_rvm():
    """
    Send a single RVM message
    Expected JSON payload:
    {
        "phone": "+1234567890",
        "message": "Your voice message here",
        "name": "John Doe" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        phone = data.get('phone')
        message = data.get('message')
        name = data.get('name', 'Friend')
        
        if not phone or not message:
            return jsonify({'error': 'Phone and message are required'}), 400
        
        if not rvm_manager.is_configured():
            return jsonify({'error': 'RVM service not configured'}), 400
        
        # Replace placeholders
        message = message.replace('{name}', name)
        
        success, result = rvm_manager.send_text_to_speech_rvm(phone, message)
        
        response = {
            'success': success,
            'message': result,
            'phone': phone,
            'type': 'rvm',
            'cost': 0.09 if success else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200 if success else 400
        
    except Exception as e:
        logger.error(f"Error in send_single_rvm: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/bulk', methods=['POST'])
def send_bulk_sms():
    """
    Send bulk SMS messages
    Expected JSON payload:
    {
        "contacts": [
            {"phone": "+1234567890", "name": "John", "message": "Custom message"},
            {"phone": "+1987654321", "name": "Jane"}
        ],
        "default_message": "Hello {name}, this is a message for you!",
        "delay": 2
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        contacts = data.get('contacts', [])
        default_message = data.get('default_message', 'Hello {name}!')
        delay = data.get('delay', 2)
        
        if not contacts:
            return jsonify({'error': 'No contacts provided'}), 400
        
        results = SMSHandler.send_bulk_sms(contacts, default_message, delay)
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        response = {
            'success': True,
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in send_bulk_sms: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/csv', methods=['POST'])
def send_from_csv():
    """
    Send SMS messages from CSV data
    Expected JSON payload:
    {
        "csv_data": "phone_number,name,message\n+1234567890,John,Hello John\n+1987654321,Jane,",
        "default_message": "Hello {name}!",
        "delay": 2
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        csv_data = data.get('csv_data')
        default_message = data.get('default_message', 'Hello {name}!')
        delay = data.get('delay', 2)
        
        if not csv_data:
            return jsonify({'error': 'No CSV data provided'}), 400
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write(csv_data)
            temp_file_path = temp_file.name
        
        try:
            # Read CSV data
            df = pd.read_csv(temp_file_path)
            
            # Convert to contacts list
            contacts = []
            for _, row in df.iterrows():
                contact = {
                    'phone': row.get('phone_number', ''),
                    'name': row.get('name', 'Friend'),
                    'message': row.get('message', '')
                }
                contacts.append(contact)
            
            # Send messages
            results = SMSHandler.send_bulk_sms(contacts, default_message, delay)
            
            # Summary
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful
            
            response = {
                'success': True,
                'summary': {
                    'total': len(results),
                    'successful': successful,
                    'failed': failed
                },
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(response), 200
            
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error in send_from_csv: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/ghl', methods=['GET', 'POST'])
def ghl_webhook():
    """
    GoHighLevel webhook endpoint
    Handles incoming webhook data from GHL workflows
    """
    if request.method == 'GET':
        return jsonify({
            'endpoint': '/api/webhook/ghl',
            'methods': ['POST'],
            'description': 'GoHighLevel webhook for SMS sending',
            'expected_payload': {
                'contact': {
                    'phone': '+1234567890',
                    'firstName': 'John',
                    'lastName': 'Doe',
                    'email': 'john@example.com'
                },
                'message': 'Your message here with {firstName} placeholder',
                'customFields': {},
                'trigger': 'workflow_name'
            },
            'response': {
                'success': True,
                'message': 'SMS sent successfully',
                'sms_id': 'twilio_message_sid'
            }
        })
    
    try:
        data = request.get_json()
        logger.info(f"GHL webhook received: {json.dumps(data, indent=2)}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract contact information (GHL format)
        contact = data.get('contact', {})
        phone = contact.get('phone') or contact.get('phone_number')
        first_name = contact.get('firstName', '')
        last_name = contact.get('lastName', '')
        full_name = f"{first_name} {last_name}".strip() or 'Friend'
        
        # Extract message
        message = data.get('message', 'Hello {firstName}!')
          # Replace GHL placeholders
        message = message.replace('{firstName}', first_name)
        message = message.replace('{lastName}', last_name)
        message = message.replace('{fullName}', full_name)
        message = message.replace('{name}', full_name)
        
        if not phone:
            return jsonify({'error': 'No phone number provided'}), 400
        
        # Send SMS
        success, result, cost, provider = sms_manager.send_sms(phone, message)
        
        response = {
            'success': success,
            'message': result,
            'contact': {
                'phone': phone,
                'name': full_name
            },
            'sms_content': message,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200 if success else 400
        
    except Exception as e:
        logger.error(f"Error in GHL webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/test', methods=['POST'])
def test_webhook():
    """Test webhook endpoint for debugging"""
    try:
        data = request.get_json()
        headers = dict(request.headers)
        
        logger.info(f"Test webhook - Headers: {json.dumps(headers, indent=2)}")
        logger.info(f"Test webhook - Data: {json.dumps(data, indent=2)}")
        
        return jsonify({
            'success': True,
            'message': 'Webhook test successful',
            'received_data': data,
            'received_headers': headers,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/multi/send', methods=['POST'])
def send_multi_channel():
    """
    Send both SMS and RVM to a phone number
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data is required'}), 400
        
        phone_number = data.get('phone_number')
        sms_message = data.get('sms_message')
        rvm_message = data.get('rvm_message')
        send_sms = data.get('send_sms', True)
        send_rvm = data.get('send_rvm', True)
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        results = {
            'phone_number': phone_number,
            'sms_result': None,
            'rvm_result': None,
            'total_cost': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send SMS if requested
        if send_sms and sms_message:
            try:
                success, result, cost, provider = sms_manager.send_sms(phone_number, sms_message)
                results['sms_result'] = {
                    'success': success,
                    'result': result,
                    'cost': cost,
                    'provider': provider
                }
                results['total_cost'] += cost
            except Exception as e:
                results['sms_result'] = {
                    'success': False,
                    'result': f'SMS error: {str(e)}',
                    'cost': 0,
                    'provider': None
                }
        
        # Send RVM if requested
        if send_rvm and rvm_message:
            try:
                success, result = rvm_manager.send_text_to_speech_rvm(
                    phone_number, 
                    rvm_message,
                    title="Multi-Channel Campaign"
                )
                rvm_cost = 0.09 if success else 0  # Slybroadcast cost
                results['rvm_result'] = {
                    'success': success,
                    'result': result,
                    'cost': rvm_cost
                }
                results['total_cost'] += rvm_cost
            except Exception as e:
                results['rvm_result'] = {
                    'success': False,
                    'result': f'RVM error: {str(e)}',
                    'cost': 0
                }
        
        # Determine overall success
        sms_success = results['sms_result']['success'] if results['sms_result'] else True
        rvm_success = results['rvm_result']['success'] if results['rvm_result'] else True
        overall_success = sms_success and rvm_success
        
        status_code = 200 if overall_success else 400
        
        logger.info(f"Multi-channel sent to {phone_number}: SMS={sms_success}, RVM={rvm_success}")
        
        return jsonify(results), status_code
        
    except Exception as e:
        logger.error(f"Error in multi-channel send: {e}")
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/static/<filename>')
def static_files(filename):
    """Serve static files (logos, images, etc.)"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/upload/logo', methods=['POST'])
def upload_logo():
    """Upload custom logo for Sparky Messaging"""
    try:
        if 'logo' not in request.files:
            return jsonify({'error': 'No logo file provided'}), 400
        
        file = request.files['logo']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save as logo.png (or keep original extension)
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"logo.{file_extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Remove old logo files
            for ext in ALLOWED_EXTENSIONS:
                old_file = os.path.join(app.config['UPLOAD_FOLDER'], f"logo.{ext}")
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            file.save(filepath)
            
            logger.info(f"Logo uploaded successfully: {filename}")
            
            return jsonify({
                'success': True,
                'message': 'Logo uploaded successfully',
                'filename': filename,
                'url': f'/static/{filename}'
            }), 200
        else:
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, GIF, SVG, or ICO'}), 400
            
    except Exception as e:
        logger.error(f"Error uploading logo: {e}")
        return jsonify({'error': str(e)}), 500

# SimpleTalk.ai API Endpoints
@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Check SimpleTalk.ai configuration status"""
    try:
        is_configured = ai_manager.is_configured()
        return jsonify({
            'configured': is_configured,
            'message': 'SimpleTalk.ai ready' if is_configured else 'SimpleTalk.ai not configured - check API key'
        }), 200
    except Exception as e:
        logger.error(f"Error checking AI status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/generate/sms', methods=['POST'])
def ai_generate_sms():
    """Generate optimized SMS message using SimpleTalk.ai"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        context = data.get('context', '')
        contact_info = data.get('contact_info', {})
        tone = data.get('tone', 'friendly')
        max_length = data.get('max_length', 160)
        
        if not context:
            return jsonify({'error': 'Context is required'}), 400
        
        success, message = ai_manager.generate_sms_message(
            context=context,
            contact_info=contact_info,
            tone=tone,
            max_length=max_length
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'length': len(message),
                'tone': tone,
                'context': context
            }), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"Error generating SMS: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/generate/rvm', methods=['POST'])
def ai_generate_rvm():
    """Generate RVM script using SimpleTalk.ai"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        context = data.get('context', '')
        contact_info = data.get('contact_info', {})
        tone = data.get('tone', 'conversational')
        duration = data.get('duration', '30 seconds')
        
        if not context:
            return jsonify({'error': 'Context is required'}), 400
        
        success, script = ai_manager.generate_rvm_script(
            context=context,
            contact_info=contact_info,
            tone=tone,
            duration=duration
        )
        
        if success:
            return jsonify({
                'success': True,
                'script': script,
                'length': len(script),
                'tone': tone,
                'duration': duration,
                'context': context
            }), 200
        else:
            return jsonify({'error': script}), 400
            
    except Exception as e:
        logger.error(f"Error generating RVM script: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/conversation-flow', methods=['POST'])
def ai_create_conversation_flow():
    """Create multi-step conversation flow using SimpleTalk.ai"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        campaign_goal = data.get('campaign_goal', '')
        audience_info = data.get('audience_info', '')
        num_steps = data.get('num_steps', 3)
        
        if not campaign_goal:
            return jsonify({'error': 'Campaign goal is required'}), 400
        
        if not audience_info:
            return jsonify({'error': 'Audience information is required'}), 400
        
        success, flow = ai_manager.create_conversation_flow(
            campaign_goal=campaign_goal,
            audience_info=audience_info,
            num_steps=num_steps
        )
        
        if success:
            return jsonify({
                'success': True,
                'flow': flow,
                'campaign_goal': campaign_goal,
                'audience_info': audience_info
            }), 200
        else:
            return jsonify({'error': flow}), 400
            
    except Exception as e:
        logger.error(f"Error creating conversation flow: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/optimize', methods=['POST'])
def ai_optimize_message():
    """Optimize existing message using SimpleTalk.ai"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        original_message = data.get('original_message', '')
        optimization_goal = data.get('optimization_goal', 'engagement')
        
        if not original_message:
            return jsonify({'error': 'Original message is required'}), 400
        
        success, optimized_message, improvements = ai_manager.optimize_message(
            original_message=original_message,
            optimization_goal=optimization_goal
        )
        
        if success:
            return jsonify({
                'success': True,
                'original_message': original_message,
                'optimized_message': optimized_message,
                'improvements': improvements,
                'optimization_goal': optimization_goal
            }), 200
        else:
            return jsonify({'error': optimized_message}), 400
            
    except Exception as e:
        logger.error(f"Error optimizing message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/usage', methods=['GET'])
def ai_get_usage():
    """Get SimpleTalk.ai account usage information"""
    try:
        success, usage_data = ai_manager.get_account_usage()
        
        if success:
            return jsonify({
                'success': True,
                'usage': usage_data
            }), 200
        else:
            return jsonify({'error': usage_data}), 400
            
    except Exception as e:
        logger.error(f"Error getting AI usage: {e}")
        return jsonify({'error': str(e)}), 500

# Email API Endpoints
@app.route('/api/email/send', methods=['POST'])
def send_email():
    """Send single email via best available provider"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Required fields
        required_fields = ['to_email', 'subject', 'content']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Optional fields
        from_name = data.get('from_name', 'Sparky Messaging')
        content_type = data.get('content_type', 'html')
        attachments = data.get('attachments', [])
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['to_email']):
            return jsonify({'error': 'Invalid email address format'}), 400
        
        # Send email
        result = email_manager.send_email(
            to_email=data['to_email'],
            subject=data['subject'],
            content=data['content'],
            from_name=from_name,
            content_type=content_type,
            attachments=attachments
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully',
                'provider': result.get('provider'),
                'cost': result.get('cost'),
                'message_id': result.get('message_id')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error'),
                'provider': result.get('provider')
            }), 500
            
    except Exception as e:
        logger.error(f"Email send error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/email/bulk', methods=['POST'])
def send_bulk_email():
    """Send bulk emails to multiple recipients"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Required fields
        required_fields = ['recipients', 'subject', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if not isinstance(data['recipients'], list) or len(data['recipients']) == 0:
            return jsonify({'error': 'Recipients must be a non-empty list'}), 400
        
        # Optional fields
        from_name = data.get('from_name', 'Sparky Messaging')
        content_type = data.get('content_type', 'html')
        
        # Validate email formats
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_emails = [email for email in data['recipients'] if not re.match(email_pattern, email)]
        
        if invalid_emails:
            return jsonify({
                'error': f'Invalid email addresses: {", ".join(invalid_emails[:5])}'
            }), 400
        
        # Send bulk emails
        result = email_manager.send_bulk_email(
            recipients=data['recipients'],
            subject=data['subject'],
            content=data['content'],
            from_name=from_name,
            content_type=content_type
        )
        
        return jsonify({
            'success': True,
            'message': f'Bulk email completed',
            'total_sent': result['total_sent'],
            'total_failed': result['total_failed'],
            'total_cost': result['total_cost'],
            'provider_usage': result['provider_usage'],
            'failed_emails': result['failed_emails'][:10],  # Limit failed email list
            'success_rate': round((result['total_sent'] / len(data['recipients'])) * 100, 2) if data['recipients'] else 0
        })
        
    except Exception as e:
        logger.error(f"Bulk email error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/email/capacity', methods=['GET'])
def email_capacity():
    """Get remaining email capacity across all providers"""
    try:
        capacity = email_manager.get_capacity()
        return jsonify(capacity)
    except Exception as e:
        logger.error(f"Email capacity error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/usage', methods=['GET'])
def email_usage():
    """Get email usage statistics"""
    try:
        stats = email_manager.get_usage_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Email usage error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/cost-estimate', methods=['POST'])
def email_cost_estimate():
    """Get cost estimate for sending emails"""
    try:
        data = request.get_json()
        
        if not data or 'email_count' not in data:
            return jsonify({'error': 'Missing email_count in request'}), 400
        
        email_count = data['email_count']
        
        if not isinstance(email_count, int) or email_count <= 0:
            return jsonify({'error': 'email_count must be a positive integer'}), 400
        
        estimate = email_manager.get_cost_estimate(email_count)
        return jsonify(estimate)
        
    except Exception as e:
        logger.error(f"Email cost estimate error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/multi/email-sms', methods=['POST'])
def send_email_sms_combo():
    """Send both email and SMS to the same contact"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Required fields
        required_fields = ['contact', 'email_subject', 'email_content', 'sms_message']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        contact = data['contact']
        if 'email' not in contact or 'phone' not in contact:
            return jsonify({'error': 'Contact must have both email and phone'}), 400
        
        # Optional fields
        from_name = data.get('from_name', 'Sparky Messaging')
        email_type = data.get('email_content_type', 'html')
        delay_minutes = data.get('delay_minutes', 0)
        
        results = {
            'email': None,
            'sms': None,
            'total_cost': 0
        }
        
        # Send email first
        email_result = email_manager.send_email(
            to_email=contact['email'],
            subject=data['email_subject'],
            content=data['email_content'],
            from_name=from_name,
            content_type=email_type
        )
        
        results['email'] = {
            'success': email_result['success'],
            'provider': email_result.get('provider'),
            'cost': email_result.get('cost', 0),
            'error': email_result.get('error') if not email_result['success'] else None
        }
        
        if email_result['success']:
            results['total_cost'] += email_result.get('cost', 0)
        
        # Handle delay if specified
        if delay_minutes > 0:
            import time
            time.sleep(delay_minutes * 60)
        
        # Send SMS
        sms_result = sms_manager.send_sms(
            phone_number=contact['phone'],
            message=data['sms_message']
        )
        
        results['sms'] = {
            'success': sms_result['success'],
            'provider': sms_result.get('provider'),
            'cost': sms_result.get('cost', 0),
            'error': sms_result.get('error') if not sms_result['success'] else None
        }
        
        if sms_result['success']:
            results['total_cost'] += sms_result.get('cost', 0)
          # Overall success if at least one succeeds
        overall_success = email_result['success'] or sms_result['success']
        
        return jsonify({
            'success': overall_success,
            'message': 'Multi-channel message completed',
            'results': results,
            'channels_sent': sum([1 for r in [results['email'], results['sms']] if r['success']])
        })
        
    except Exception as e:
        logger.error(f"Email+SMS combo error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/index.html')
def home_page():
    """Serve the main home page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Home page not found", 404

# Authentication Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '').lower()
        password = data.get('password', '')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Check if user exists
        user = USERS_DB.get(username)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user['password']:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check role matches
        if role != user['role']:
            return jsonify({'error': f'User is not authorized for {role} role'}), 403
        
        # Generate session token
        token = generate_token()
        ACTIVE_SESSIONS[token] = {
            'username': user['username'],
            'role': user['role'],
            'login_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        logger.info(f"User {username} logged in as {role}")
        
        return jsonify({
            'success': True,
            'token': token,
            'username': user['username'],
            'role': user['role'],
            'message': f'Welcome back, {user["username"]}!'
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token and token in ACTIVE_SESSIONS:
            username = ACTIVE_SESSIONS[token]['username']
            del ACTIVE_SESSIONS[token]
            logger.info(f"User {username} logged out")
            return jsonify({'success': True, 'message': 'Logged out successfully'})
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/verify', methods=['GET'])
def verify_auth():
    """Verify authentication token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'authenticated': False}), 401
        
        user_info = verify_token(token)
        if not user_info:
            return jsonify({'authenticated': False}), 401
        
        # Update last activity
        ACTIVE_SESSIONS[token]['last_activity'] = datetime.now().isoformat()
        
        return jsonify({
            'authenticated': True,
            'username': user_info['username'],
            'role': user_info['role']
        })
    except Exception as e:
        logger.error(f"Auth verification error: {e}")
        return jsonify({'authenticated': False}), 500

@app.route('/api/admin/stats', methods=['GET'])
@require_auth(role='admin')
def admin_stats():
    """Get admin dashboard statistics"""
    try:
        return jsonify({
            'total_users': len(USERS_DB),
            'active_sessions': len(ACTIVE_SESSIONS),
            'sms_providers': len([p for p in sms_manager.providers if p.enabled]),
            'email_providers': email_manager.get_provider_count(),
            'ai_enabled': ai_manager.is_configured(),
            'rvm_enabled': rvm_manager.is_configured(),
            'system_status': 'operational'
        })
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500

# Routes for HTML pages
@app.route('/login.html')
def login_page():
    """Serve the login page"""
    try:
        with open('login.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Login page not found", 404

@app.route('/admin.html')
def admin_page():
    """Serve the admin dashboard page"""
    try:
        with open('admin.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Admin page not found", 404

@app.route('/dashboard.html')
def dashboard_page():
    """Serve the user dashboard page"""
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard page not found", 404

if __name__ == '__main__':
    print("Starting Sparky Messaging API Server")
    print("=" * 60)
    print(f"📱 Twilio configured: {twilio_client is not None}")
    print(f"🤖 SimpleTalk.ai configured: {ai_manager.is_configured()}")
    print("🌐 Main Pages:")
    print("   GET  / - Sparky Messaging Home Page")
    print("   GET  /login.html - Login Page") 
    print("   GET  /admin.html - Admin Dashboard")
    print("   GET  /dashboard.html - User Dashboard")
    print("🔐 Authentication Endpoints:")
    print("   POST /api/auth/login - User login")
    print("   POST /api/auth/logout - User logout")
    print("   GET  /api/auth/verify - Verify token")
    print("   GET  /api/admin/stats - Admin statistics")
    print("📱 SMS Endpoints:")
    print("   POST /api/sms/send - Send single SMS")
    print("   POST /api/sms/bulk - Send bulk SMS")
    print("   POST /api/rvm/send - Send ringless voicemail")
    print("   POST /api/multi/send - Send SMS + RVM combo")
    print("   POST /api/webhook/ghl - GHL webhook")
    print("📧 Email Endpoints:")
    print("   POST /api/email/send - Send single email")
    print("   POST /api/email/bulk - Send bulk emails")
    print("   GET  /api/email/capacity - Get email capacity")
    print("   GET  /api/email/usage - Get email usage stats")
    print("   POST /api/email/cost-estimate - Get email cost estimate")
    print("   POST /api/multi/email-sms - Send email + SMS combo")
    print("🤖 AI Endpoints:")
    print("   GET  /api/ai/status - Check AI configuration")
    print("   POST /api/ai/generate/sms - Generate SMS with AI")
    print("   POST /api/ai/generate/rvm - Generate RVM script with AI")
    print("   POST /api/ai/conversation-flow - Create conversation flow")
    print("   POST /api/ai/optimize - Optimize existing message")
    print("   GET  /api/ai/usage - Get AI usage stats")
    print("=" * 60)
    print("📖 Access platform at: http://localhost:5000/")
    print("� Login required - Demo Credentials:")
    print("   User: demo / password")
    print("   Admin: admin / admin123")
    print("📋 Flow: Login → Home Page → Features")
    print()
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
