"""
Flask API Server for Bulk SMS Operations
Provides REST endpoints for CSV upload, bulk sending, and status tracking
"""

from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import os
import uuid
import json
import asyncio
from datetime import datetime
import threading
import time
from bulk_sms_system import BulkSMSSystem, SMSProvider
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory storage for demo (use Redis/database in production)
upload_sessions = {}
sending_jobs = {}

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """API documentation page"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Bulk SMS API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .method { color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold; }
        .get { background: #28a745; }
        .post { background: #007bff; }
        .delete { background: #dc3545; }
        code { background: #e9ecef; padding: 2px 4px; border-radius: 3px; }
        .example { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>🚀 Bulk SMS API Server</h1>
    <p>RESTful API for bulk SMS operations with CSV import and multiple providers</p>
    
    <h2>📡 Available Endpoints</h2>
    
    <div class="endpoint">
        <h3><span class="method post">POST</span> /api/upload-csv</h3>
        <p>Upload a CSV file with contacts for bulk SMS</p>
        <div class="example">
            <strong>curl example:</strong><br>
            <code>curl -X POST -F "file=@contacts.csv" http://localhost:5000/api/upload-csv</code>
        </div>
        <p><strong>CSV Format:</strong> phone_number (required), name, email, message, first_name, last_name</p>
    </div>
    
    <div class="endpoint">
        <h3><span class="method post">POST</span> /api/send-bulk</h3>
        <p>Send bulk SMS to uploaded contacts</p>
        <div class="example">
            <strong>Request body:</strong><br>
            <code>{
  "session_id": "uuid-from-upload",
  "message": "Hi {name}, this is your message!",
  "provider": "clicksend",
  "from": "YourBusiness",
  "delay": 1.0
}</code>
        </div>
    </div>
    
    <div class="endpoint">
        <h3><span class="method get">GET</span> /api/job-status/&lt;job_id&gt;</h3>
        <p>Check the status of a bulk SMS job</p>
        <div class="example">
            <strong>curl example:</strong><br>
            <code>curl http://localhost:5000/api/job-status/your-job-id</code>
        </div>
    </div>
    
    <div class="endpoint">
        <h3><span class="method get">GET</span> /api/results/&lt;job_id&gt;</h3>
        <p>Download CSV results of a completed bulk SMS job</p>
    </div>
    
    <div class="endpoint">
        <h3><span class="method get">GET</span> /api/providers</h3>
        <p>List available SMS providers</p>
    </div>
    
    <div class="endpoint">
        <h3><span class="method post">POST</span> /api/webhook/ghl</h3>
        <p>GoHighLevel webhook endpoint for integration</p>
        <div class="example">
            <strong>GHL webhook payload:</strong><br>
            <code>{
  "contact": {
    "phone": "+1234567890",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
  },
  "message": "Hi {firstName}, your appointment is confirmed!",
  "provider": "clicksend"
}</code>
        </div>
    </div>
    
    <h2>🔧 Supported Providers</h2>
    <ul>
        <li><strong>ClickSend</strong> - No A2P registration required</li>
        <li><strong>Twilio</strong> - Industry leader (A2P required)</li>
        <li><strong>Plivo</strong> - Cost-effective option</li>
        <li><strong>TextMagic</strong> - Business-friendly</li>
        <li><strong>BulkSMS</strong> - Global coverage</li>
        <li><strong>MessageBird</strong> - Developer-friendly</li>
    </ul>
    
    <h2>⚙️ Environment Variables</h2>
    <p>Set these environment variables for provider authentication:</p>
    <ul>
        <li><code>CLICKSEND_USERNAME</code> and <code>CLICKSEND_API_KEY</code></li>
        <li><code>TWILIO_ACCOUNT_SID</code>, <code>TWILIO_AUTH_TOKEN</code>, <code>TWILIO_PHONE_NUMBER</code></li>
        <li>Additional provider credentials as needed</li>
    </ul>
    
    <p><em>Server running on port 5000 - Ready for bulk SMS operations! 🚀</em></p>
</body>
</html>
    ''')

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Upload CSV file with contacts"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = f"{session_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Load and validate CSV
        system = BulkSMSSystem()
        contacts = system.load_contacts_from_csv(filepath)
        
        # Store session data
        upload_sessions[session_id] = {
            'filename': filename,
            'filepath': filepath,
            'contact_count': len(contacts),
            'contacts': contacts,
            'uploaded_at': datetime.now().isoformat(),
            'sample_contacts': contacts[:3] if contacts else []  # First 3 for preview
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'contact_count': len(contacts),
            'sample_contacts': contacts[:3] if contacts else [],
            'message': f'Successfully uploaded {len(contacts)} contacts'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-bulk', methods=['POST'])
def send_bulk():
    """Start bulk SMS sending job"""
    data = request.get_json()
    
    # Validate input
    required_fields = ['session_id', 'message', 'provider']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
    
    session_id = data['session_id']
    if session_id not in upload_sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    # Validate provider
    provider_name = data['provider'].lower()
    try:
        provider = SMSProvider(provider_name)
    except ValueError:
        available_providers = [p.value for p in SMSProvider]
        return jsonify({'error': f'Invalid provider. Available: {available_providers}'}), 400
    
    # Create job
    job_id = str(uuid.uuid4())
    
    job_data = {
        'job_id': job_id,
        'session_id': session_id,
        'status': 'queued',
        'message': data['message'],
        'provider': provider_name,
        'from': data.get('from', 'SMS'),
        'delay': data.get('delay', 1.0),
        'created_at': datetime.now().isoformat(),
        'contact_count': upload_sessions[session_id]['contact_count'],
        'sent_count': 0,
        'success_count': 0,
        'failed_count': 0,
        'results': [],
        'error': None
    }
    
    sending_jobs[job_id] = job_data
    
    # Start sending in background thread
    thread = threading.Thread(target=process_bulk_job, args=(job_id,))
    thread.start()
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'status': 'queued',
        'message': f'Bulk SMS job started for {job_data["contact_count"]} contacts'
    })

def process_bulk_job(job_id):
    """Process bulk SMS job in background"""
    try:
        job_data = sending_jobs[job_id]
        session_data = upload_sessions[job_data['session_id']]
        
        # Update status
        job_data['status'] = 'processing'
        job_data['started_at'] = datetime.now().isoformat()
        
        # Initialize SMS system
        system = BulkSMSSystem()
        
        # Prepare messages
        messages = system.prepare_messages(
            session_data['contacts'],
            job_data['message'],
            job_data['from']
        )
        
        # Send messages
        provider = SMSProvider(job_data['provider'])
        results = system.send_bulk_sync(messages, provider, job_data['delay'])
        
        # Update job with results
        job_data['status'] = 'completed'
        job_data['completed_at'] = datetime.now().isoformat()
        job_data['results'] = [
            {
                'success': r.success,
                'message_id': r.message_id,
                'error': r.error,
                'cost': r.cost,
                'provider': r.provider
            } for r in results
        ]
        
        # Calculate summary
        summary = system.get_summary()
        job_data.update(summary)
        
        # Export results to file
        results_filename = f"results_{job_id}.csv"
        results_filepath = os.path.join(RESULTS_FOLDER, results_filename)
        system.export_results(results_filepath)
        job_data['results_file'] = results_filepath
        
        logging.info(f"Job {job_id} completed: {summary}")
        
    except Exception as e:
        job_data['status'] = 'failed'
        job_data['error'] = str(e)
        job_data['failed_at'] = datetime.now().isoformat()
        logging.error(f"Job {job_id} failed: {str(e)}")

@app.route('/api/job-status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status and progress"""
    if job_id not in sending_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job_data = sending_jobs[job_id].copy()
    
    # Don't send full results in status (too large)
    if 'results' in job_data:
        job_data['results_available'] = len(job_data['results'])
        del job_data['results']
    
    return jsonify(job_data)

@app.route('/api/results/<job_id>', methods=['GET'])
def download_results(job_id):
    """Download CSV results"""
    if job_id not in sending_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job_data = sending_jobs[job_id]
    
    if job_data['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    if 'results_file' not in job_data or not os.path.exists(job_data['results_file']):
        return jsonify({'error': 'Results file not found'}), 404
    
    return send_file(
        job_data['results_file'],
        as_attachment=True,
        download_name=f"sms_results_{job_id}.csv"
    )

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """List available SMS providers"""
    providers = [
        {
            'name': 'ClickSend',
            'id': 'clicksend',
            'description': 'Multi-channel messaging platform - No A2P required',
            'pricing': '$0.0174-0.0243 per SMS',
            'features': ['No daily limits', 'Global coverage', 'Instant setup']
        },
        {
            'name': 'Twilio',
            'id': 'twilio',
            'description': 'Industry-leading CPaaS platform - A2P required',
            'pricing': '$0.0075 per SMS (US)',
            'features': ['Premium reliability', 'Advanced features', 'Enterprise grade']
        },
        {
            'name': 'Plivo',
            'id': 'plivo',
            'description': 'Cost-effective messaging APIs',
            'pricing': '$0.0025-0.0055 per SMS',
            'features': ['Competitive pricing', 'Good delivery rates', 'Simple API']
        },
        {
            'name': 'TextMagic',
            'id': 'textmagic',
            'description': 'Business text messaging - No A2P required',
            'pricing': '$0.032-0.04 per SMS',
            'features': ['SMB friendly', 'Easy interface', 'Two-way messaging']
        },
        {
            'name': 'BulkSMS',
            'id': 'bulksms',
            'description': 'Global SMS messaging - No A2P required',
            'pricing': '$0.02-0.05 per SMS',
            'features': ['Global coverage', 'Direct networks', 'Reliable delivery']
        },
        {
            'name': 'MessageBird',
            'id': 'messagebird',
            'description': 'Cloud communications platform',
            'pricing': '$0.025-0.06 per SMS',
            'features': ['Developer friendly', 'Global reach', 'Omnichannel']
        }
    ]
    
    return jsonify({'providers': providers})

@app.route('/api/webhook/ghl', methods=['POST'])
def ghl_webhook():
    """GoHighLevel webhook endpoint"""
    try:
        data = request.get_json()
        
        # Extract contact information
        contact = data.get('contact', {})
        phone = contact.get('phone', '')
        first_name = contact.get('firstName', '')
        last_name = contact.get('lastName', '')
        email = contact.get('email', '')
        
        # Extract message and provider
        message = data.get('message', '')
        provider = data.get('provider', 'clicksend')
        from_number = data.get('from', 'GHL')
        
        if not phone or not message:
            return jsonify({'error': 'Phone number and message are required'}), 400
        
        # Create single contact for sending
        contacts = [{
            'phone_number': phone,
            'first_name': first_name,
            'last_name': last_name,
            'name': f"{first_name} {last_name}".strip() or 'Friend',
            'email': email
        }]
        
        # Initialize SMS system
        system = BulkSMSSystem()
        
        # Prepare message
        messages = system.prepare_messages(contacts, message, from_number)
        
        if not messages:
            return jsonify({'error': 'Failed to prepare message'}), 400
        
        # Send message
        try:
            provider_enum = SMSProvider(provider.lower())
        except ValueError:
            return jsonify({'error': f'Invalid provider: {provider}'}), 400
        
        results = system.send_bulk_sync(messages, provider_enum, delay=0)
        
        if results and results[0].success:
            return jsonify({
                'success': True,
                'message_id': results[0].message_id,
                'cost': results[0].cost,
                'provider': results[0].provider
            })
        else:
            error = results[0].error if results else 'Unknown error'
            return jsonify({'success': False, 'error': error}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'bulk_sms': 'active',
            'csv_upload': 'active',
            'webhooks': 'active'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Bulk SMS API Server...")
    print("📡 Available at: http://localhost:5000")
    print("📋 API docs at: http://localhost:5000")
    print("🔧 Upload CSV: POST /api/upload-csv")
    print("📤 Send Bulk: POST /api/send-bulk")
    print("📊 Job Status: GET /api/job-status/<job_id>")
    print("🌐 GHL Webhook: POST /api/webhook/ghl")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
