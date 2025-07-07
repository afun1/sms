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

# Store for SMS delivery reports (in production, use a database)
delivery_reports = {}

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
            'POST /api/webhook/clicksend': 'ClickSend delivery reports webhook',
            'GET /api/delivery-reports': 'Get SMS delivery reports',
            'DELETE /api/delivery-reports': 'Clear delivery reports',
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

@app.route('/list.html')
def list_page():
    """Serve the list builder page (fallback to index.html if missing)"""
    try:
        with open('list.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback: serve index.html if list.html does not exist
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "List page not found", 404

@app.route('/assets.html')
def serve_assets():
    """Serve the assets page from the root directory"""
    try:
        with open('assets.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Assets page not found", 404

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

@app.route('/static/<path:filename>')
def static_files(filename):
    # Always serve .js files with correct MIME type
    if filename.endswith('.js'):
        return send_from_directory('static', filename, mimetype='application/javascript')
    return send_from_directory('static', filename)

# ...rest of your API and HTML routes remain unchanged...

@app.route('/index.html')
def home_page():
    """Serve the main home page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Home page not found", 404

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
def dashboard():
    """Serve the user dashboard page"""
    try:
        with open('dashboard.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard page not found", 404

@app.route('/webhook_test.html')
def webhook_test():
    """Serve the webhook test page"""
    try:
        with open('webhook_test.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Webhook test page not found", 404

@app.route('/api/webhook/clicksend', methods=['POST'])
def clicksend_webhook():
    """
    ClickSend webhook endpoint to receive delivery reports
    ClickSend sends POST requests to this endpoint with delivery status updates
    """
    try:
        # Get the JSON payload from ClickSend
        data = request.get_json()
        
        logger.info(f"ClickSend webhook received: {data}")
        
        # Validate the webhook data
        if not data:
            logger.error("No data received from ClickSend webhook")
            return jsonify({"error": "No data received"}), 400
        
        # Extract delivery report information
        # ClickSend webhook format includes: message_id, status, timestamp, etc.
        message_id = data.get('message_id')
        status = data.get('status')
        timestamp = data.get('timestamp')
        phone_number = data.get('to')
        error_code = data.get('error_code')
        error_text = data.get('error_text')
        
        # Store the delivery report
        if message_id:
            delivery_reports[message_id] = {
                'message_id': message_id,
                'status': status,
                'timestamp': timestamp,
                'phone_number': phone_number,
                'error_code': error_code,
                'error_text': error_text,
                'received_at': datetime.now().isoformat()
            }
            
            logger.info(f"Delivery report stored for message {message_id}: {status}")
        
        # Return success response to ClickSend
        return jsonify({
            "success": True,
            "message": "Delivery report received and processed",
            "message_id": message_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing ClickSend webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/delivery-reports', methods=['GET'])
def get_delivery_reports():
    """
    Get all delivery reports
    """
    try:
        # Get message_id query parameter to filter by specific message
        message_id = request.args.get('message_id')
        
        if message_id:
            # Return specific delivery report
            report = delivery_reports.get(message_id)
            if report:
                return jsonify({"success": True, "report": report})
            else:
                return jsonify({"success": False, "message": "Report not found"}), 404
        else:
            # Return all delivery reports as a list (easier for dashboard)
            reports_list = []
            for msg_id, report in delivery_reports.items():
                # Add provider information and format for dashboard
                report_copy = report.copy()
                # Determine provider from the original report or default to ClickSend
                report_copy['provider'] = report_copy.get('provider', 'ClickSend')
                report_copy['to'] = report_copy.get('phone_number', 'Unknown')
                report_copy['error_message'] = report_copy.get('error_text', '')
                reports_list.append(report_copy)
            
            # Add sample data if no reports exist (for testing)
            if not reports_list:
                from datetime import timedelta
                
                # Generate sample data for the past few days with all 7 providers
                base_date = datetime.now()
                sample_reports = []
                
                # Day 1 - Today
                sample_reports.extend([
                    {
                        'message_id': 'msg_today_001',
                        'status': 'Delivered',
                        'timestamp': base_date.isoformat(),
                        'to': '+1234567890',
                        'provider': 'ClickSend',
                        'error_message': '',
                        'received_at': base_date.isoformat()
                    },
                    {
                        'message_id': 'msg_today_002',
                        'status': 'Delivered',
                        'timestamp': base_date.isoformat(),
                        'to': '+1234567891',
                        'provider': 'ClickSend',
                        'error_message': '',
                        'received_at': base_date.isoformat()
                    },
                    {
                        'message_id': 'msg_today_003',
                        'status': 'Failed',
                        'timestamp': base_date.isoformat(),
                        'to': '+1234567892',
                        'provider': 'ClickSend',
                        'error_message': 'Invalid phone number',
                        'received_at': base_date.isoformat()
                    },
                    {
                        'message_id': 'msg_today_004',
                        'status': 'Delivered',
                        'timestamp': base_date.isoformat(),
                        'to': '+1234567893',
                        'provider': 'BulkSMS',
                        'error_message': '',
                        'received_at': base_date.isoformat()
                    },
                    {
                        'message_id': 'msg_today_005',
                        'status': 'Delivered',
                        'timestamp': base_date.isoformat(),
                        'to': '+1234567894',
                        'provider': 'Infobip',
                        'error_message': '',
                        'received_at': base_date.isoformat()
                    },
                    {
                        'message_id': 'msg_today_006',
                        'status': 'Delivered',
                        'timestamp': base_date.isoformat(),
                        'to': '+1234567895',
                        'provider': 'MessageBird',
                        'error_message': '',
                        'received_at': base_date.isoformat()
                    },
                    {
                        'message_id': 'msg_today_007',
                        'status': 'Pending',
                        'timestamp': base_date.isoformat(),
                        'to': '+1234567896',
                        'provider': 'Sinch',
                        'error_message': '',
                        'received_at': base_date.isoformat()
                    }
                ])
                
                # Day 2 - Yesterday
                yesterday = base_date - timedelta(days=1)
                sample_reports.extend([
                    {
                        'message_id': 'msg_yesterday_001',
                        'status': 'Delivered',
                        'timestamp': yesterday.isoformat(),
                        'to': '+1234567897',
                        'provider': 'ClickSend',
                        'error_message': '',
                        'received_at': yesterday.isoformat()
                    },
                    {
                        'message_id': 'msg_yesterday_002',
                        'status': 'Delivered',
                        'timestamp': yesterday.isoformat(),
                        'to': '+1234567898',
                        'provider': 'ClickSend',
                        'error_message': '',
                        'received_at': yesterday.isoformat()
                    },
                    {
                        'message_id': 'msg_yesterday_003',
                        'status': 'Delivered',
                        'timestamp': yesterday.isoformat(),
                        'to': '+1234567899',
                        'provider': 'BulkSMS',
                        'error_message': '',
                        'received_at': yesterday.isoformat()
                    },
                    {
                        'message_id': 'msg_yesterday_004',
                        'status': 'Failed',
                        'timestamp': yesterday.isoformat(),
                        'to': '+1234567800',
                        'provider': 'BulkSMS',
                        'error_message': 'Network timeout',
                        'received_at': yesterday.isoformat()
                    },
                    {
                        'message_id': 'msg_yesterday_005',
                        'status': 'Delivered',
                        'timestamp': yesterday.isoformat(),
                        'to': '+1234567801',
                        'provider': 'MessageBird',
                        'error_message': '',
                        'received_at': yesterday.isoformat()
                    },
                    {
                        'message_id': 'msg_yesterday_006',
                        'status': 'Delivered',
                        'timestamp': yesterday.isoformat(),
                        'to': '+1234567802',
                        'provider': 'TextMagic',
                        'error_message': '',
                        'received_at': yesterday.isoformat()
                    },
                    {
                        'message_id': 'msg_yesterday_007',
                        'status': 'Delivered',
                        'timestamp': yesterday.isoformat(),
                        'to': '+1234567803',
                        'provider': 'Plivo',
                        'error_message': '',
                        'received_at': yesterday.isoformat()
                    }
                ])
                
                # Day 3 - Two days ago
                two_days_ago = base_date - timedelta(days=2)
                sample_reports.extend([
                    {
                        'message_id': 'msg_2days_001',
                        'status': 'Delivered',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567804',
                        'provider': 'ClickSend',
                        'error_message': '',
                        'received_at': two_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_2days_002',
                        'status': 'Delivered',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567805',
                        'provider': 'Infobip',
                        'error_message': '',
                        'received_at': two_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_2days_003',
                        'status': 'Delivered',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567806',
                        'provider': 'Infobip',
                        'error_message': '',
                        'received_at': two_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_2days_004',
                        'status': 'Failed',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567807',
                        'provider': 'Sinch',
                        'error_message': 'Carrier blocked',
                        'received_at': two_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_2days_005',
                        'status': 'Delivered',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567808',
                        'provider': 'Sinch',
                        'error_message': '',
                        'received_at': two_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_2days_006',
                        'status': 'Delivered',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567809',
                        'provider': 'TextMagic',
                        'error_message': '',
                        'received_at': two_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_2days_007',
                        'status': 'Failed',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567810',
                        'provider': 'TextMagic',
                        'error_message': 'Invalid destination',
                        'received_at': two_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_2days_008',
                        'status': 'Delivered',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567811',
                        'provider': 'Plivo',
                        'error_message': '',
                        'received_at': two_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_2days_009',
                        'status': 'Delivered',
                        'timestamp': two_days_ago.isoformat(),
                        'to': '+1234567812',
                        'provider': 'Plivo',
                        'error_message': '',
                        'received_at': two_days_ago.isoformat()
                    }
                ])
                
                # Day 4 - Three days ago (add more variety)
                three_days_ago = base_date - timedelta(days=3)
                sample_reports.extend([
                    {
                        'message_id': 'msg_3days_001',
                        'status': 'Delivered',
                        'timestamp': three_days_ago.isoformat(),
                        'to': '+1234567813',
                        'provider': 'Infobip',
                        'error_message': '',
                        'received_at': three_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_3days_002',
                        'status': 'Delivered',
                        'timestamp': three_days_ago.isoformat(),
                        'to': '+1234567814',
                        'provider': 'TextMagic',
                        'error_message': '',
                        'received_at': three_days_ago.isoformat()
                    },
                    {
                        'message_id': 'msg_3days_003',
                        'status': 'Failed',
                        'timestamp': three_days_ago.isoformat(),
                        'to': '+1234567815',
                        'provider': 'Plivo',
                        'error_message': 'Rate limit exceeded',
                        'received_at': three_days_ago.isoformat()
                    }
                ])
                
                reports_list = sample_reports
            
            # Sort by timestamp (newest first)
            reports_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return jsonify(reports_list)
            
    except Exception as e:
        logger.error(f"Error retrieving delivery reports: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/delivery-reports', methods=['DELETE'])
def clear_delivery_reports():
    """
    Clear all delivery reports (for testing/maintenance)
    """
    try:
        global delivery_reports
        delivery_reports.clear()
        return jsonify({"success": True, "message": "All delivery reports cleared"})
    except Exception as e:
        logger.error(f"Error clearing delivery reports: {e}")
        return jsonify({"error": "Internal server error"}), 500

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
    print("   GET  /list.html - List Builder Page (fallbacks to Home if missing)")
    print("   GET  /delivery_reports.html - Delivery Reports Page")
    print("   GET  /webhook_test.html - Webhook Test Tool")
    print("   GET  /webhook_test.html - Webhook Test Page")
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
    print("   POST /api/webhook/clicksend - ClickSend delivery reports webhook")
    print("   GET  /api/delivery-reports - Get SMS delivery reports")
    print("   DELETE /api/delivery-reports - Clear delivery reports")
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
    print("📖 Access platform at: http://localhost:3000/")
    print("� Login required - Demo Credentials:")
    print("   User: demo / password")
    print("   Admin: admin / admin123")
    print("📋 Flow: Login → Home Page → Features")
    print()
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=3000,
        debug=True
    )