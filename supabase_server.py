#!/usr/bin/env python3
"""
Simple Flask server with Supabase integration for contacts
"""

from flask import Flask, jsonifydef contacts_list():
    """Serve the contact list page"""
    return send_from_directory('.', 'list.html')end_from_directory, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# Supabase configuration
SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q'

@app.route('/api/contacts')
def get_contacts():
    """Fetch contacts from Supabase using REST API"""
    try:
        # Use Supabase REST API directly
        url = f"{SUPABASE_URL}/rest/v1/contacts"
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            contacts = response.json()
            return jsonify({
                'success': True,
                'contacts': contacts,
                'count': len(contacts)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Supabase API error: {response.status_code}',
                'contacts': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'contacts': []
        }), 500

@app.route('/api/assign', methods=['POST'])
def assign_contacts():
    """Assign selected contacts to a user/agent"""
    try:
        data = request.json
        contact_ids = data.get('contact_ids', [])
        assign_to = data.get('assign_to', '')
        
        if not contact_ids or not assign_to:
            return jsonify({
                'success': False,
                'error': 'Contact IDs and assignment target are required'
            }), 400
        
        # For now, just return success (can be enhanced to update Supabase later)
        return jsonify({
            'success': True,
            'message': f'Successfully assigned {len(contact_ids)} contacts to {assign_to}',
            'assigned_count': len(contact_ids)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users')
def get_users():
    """Get all users for assignment dropdown"""
    try:
        # Use Supabase REST API to get users
        url = f"{SUPABASE_URL}/rest/v1/profiles"
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            # Sort users alphabetically by name
            sorted_users = sorted(users, key=lambda x: (x.get('first_name', '') + ' ' + x.get('last_name', '')).strip())
            
            return jsonify({
                'success': True,
                'users': sorted_users,
                'count': len(sorted_users)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Supabase API error: {response.status_code}',
                'users': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'users': []
        }), 500

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/list.html')
@app.route('/contacts')
@app.route('/list')
def contacts_list():
    """Serve the contact list page"""
    return send_from_directory('.', 'list.html')

if __name__ == '__main__':
    print("🚀 Supabase Server running at http://localhost:3000")
    print("📋 Contacts List: http://localhost:3000/list.html")
    print("📊 Assets: http://localhost:3000/assets.html")
    print("🏠 Dashboard: http://localhost:3000/dashboard.html")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=3000, debug=True)
