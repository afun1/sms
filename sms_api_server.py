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
    print("   GET  /list.html - List Builder Page (fallbacks to Home if missing)")
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