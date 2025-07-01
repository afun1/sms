#!/usr/bin/env python3
"""
Supabase Contacts API Server
Handles CSV import and contact management using Supabase database
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import traceback
from supabase import create_client, Client

# Configuration
PORT = 3000
SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q'

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseContactsAPI(BaseHTTPRequestHandler):
    
    def _send_cors_headers(self):
        """Add CORS headers for local development"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        response_json = json.dumps(data, indent=2, default=str)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error(self, message, status_code=400):
        """Send error response"""
        self._send_json_response({
            'error': True,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, status_code)
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/contacts':
            self._handle_get_contacts(parsed_path.query)
        elif path == '/api/health':
            self._handle_health_check()
        else:
            self._send_error('Endpoint not found', 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/contacts/import':
            self._handle_import_contacts()
        elif path == '/api/contacts':
            self._handle_create_contact()
        else:
            self._send_error('Endpoint not found', 404)
    
    def _handle_health_check(self):
        """Health check endpoint"""
        try:
            # Test Supabase connection
            result = supabase.table('contacts').select('count', count='exact').execute()
            contact_count = result.count if hasattr(result, 'count') else 0
            
            self._send_json_response({
                'status': 'healthy',
                'service': 'supabase-contacts-api',
                'timestamp': datetime.now().isoformat(),
                'database': 'supabase-connected',
                'contact_count': contact_count
            })
        except Exception as e:
            self._send_error(f'Database connection failed: {str(e)}', 500)
    
    def _handle_get_contacts(self, query_string):
        """Get contacts with optional filtering and pagination"""
        try:
            query_params = parse_qs(query_string) if query_string else {}
            
            # Get pagination parameters
            page = int(query_params.get('page', [1])[0])
            per_page = int(query_params.get('per_page', [100])[0])
            offset = (page - 1) * per_page
            
            # Get search parameter
            search = query_params.get('search', [''])[0]
            
            # Build Supabase query
            query = supabase.table('contacts').select('*')
            
            if search:
                # Search across multiple fields
                query = query.or_(f'first_name.ilike.%{search}%,last_name.ilike.%{search}%,email.ilike.%{search}%,phone.ilike.%{search}%,sponsor.ilike.%{search}%')
            
            # Get total count
            count_result = supabase.table('contacts').select('*', count='exact').execute()
            total_count = count_result.count if hasattr(count_result, 'count') else 0
            
            # Get paginated results
            result = query.order('created_at', desc=True).range(offset, offset + per_page - 1).execute()
            
            contacts = result.data if result.data else []
            
            self._send_json_response({
                'contacts': contacts,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'pages': (total_count + per_page - 1) // per_page if total_count > 0 else 1
                },
                'search': search
            })
            
        except Exception as e:
            print(f"Error in get_contacts: {e}")
            print(traceback.format_exc())
            self._send_error(f'Error retrieving contacts: {str(e)}', 500)
    
    def _handle_import_contacts(self):
        """Handle CSV import of contacts to Supabase"""
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            import_data = json.loads(post_data.decode('utf-8'))
            contacts_data = import_data.get('contacts', [])
            
            if not contacts_data:
                self._send_error('No contacts data provided')
                return
            
            imported_count = 0
            errors = []
            
            for i, contact_data in enumerate(contacts_data):
                try:
                    # Log the incoming data for debugging
                    print(f"Processing row {i + 1}: {list(contact_data.keys())}")
                    
                    # Prepare insert data for Supabase
                    insert_data = {
                        'sponsor': contact_data.get('sponsor', ''),
                        'sponsor_first': contact_data.get('sponsor_first', ''),
                        'sponsor_last': contact_data.get('sponsor_last', ''),
                        'user_id': contact_data.get('user_id', ''),
                        'first_name': contact_data.get('first_name', ''),
                        'last_name': contact_data.get('last_name', ''),
                        'email': contact_data.get('email', ''),
                        'email_valid': self._convert_to_bool(contact_data.get('email_valid')),
                        'phone': contact_data.get('phone', ''),
                        'address': contact_data.get('address', ''),
                        'city': contact_data.get('city', ''),
                        'state': contact_data.get('state', ''),
                        'zip': contact_data.get('zip', ''),
                        'status': contact_data.get('status', ''),
                        'rating': contact_data.get('rating', ''),
                        'ip_address': contact_data.get('ip_address', ''),
                        'date_created': contact_data.get('date_created', ''),
                        'timezone': contact_data.get('timezone', ''),
                        'cell': self._convert_to_bool(contact_data.get('cell')),
                        'carrier': contact_data.get('carrier', ''),
                        'landline': self._convert_to_bool(contact_data.get('landline')),
                        'voip': self._convert_to_bool(contact_data.get('voip')),
                        'other_phone': self._convert_to_bool(contact_data.get('other_phone')),
                        'foreign_number': self._convert_to_bool(contact_data.get('foreign_number')),
                        'country': contact_data.get('country', 'US')
                    }
                    
                    # Convert empty strings to None for nullable fields
                    for key, value in insert_data.items():
                        if value == '':
                            insert_data[key] = None
                    
                    # Log the processed data
                    non_null_fields = {k: v for k, v in insert_data.items() if v is not None}
                    print(f"Row {i + 1} mapped fields: {list(non_null_fields.keys())}")
                    
                    # Insert contact into Supabase
                    result = supabase.table('contacts').insert(insert_data).execute()
                    
                    if result.data:
                        imported_count += 1
                        print(f"✅ Row {i + 1} imported successfully")
                    else:
                        errors.append(f'Row {i + 1}: Failed to insert - no data returned')
                        print(f"❌ Row {i + 1}: Failed to insert - no data returned")
                    
                except Exception as row_error:
                    errors.append(f'Row {i + 1}: {str(row_error)}')
                    print(f"Error importing row {i + 1}: {row_error}")
            
            response_data = {
                'success': True,
                'imported': imported_count,
                'total_submitted': len(contacts_data),
                'errors': errors
            }
            
            if errors:
                response_data['message'] = f'Imported {imported_count} contacts with {len(errors)} errors'
            else:
                response_data['message'] = f'Successfully imported {imported_count} contacts'
            
            self._send_json_response(response_data)
            
        except Exception as e:
            print(f"Error in import_contacts: {e}")
            print(traceback.format_exc())
            self._send_error(f'Error importing contacts: {str(e)}', 500)
    
    def _convert_to_bool(self, value):
        """Convert various values to boolean for database storage"""
        if value is None or value == '':
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ('true', '1', 'yes', 'y', 'on'):
                return True
            elif value in ('false', '0', 'no', 'n', 'off'):
                return False
        return None
    
    def _handle_create_contact(self):
        """Handle creating a single contact"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            contact_data = json.loads(post_data.decode('utf-8'))
            
            # Insert single contact into Supabase
            result = supabase.table('contacts').insert(contact_data).execute()
            
            if result.data:
                self._send_json_response({
                    'success': True,
                    'message': 'Contact created successfully',
                    'contact': result.data[0]
                })
            else:
                self._send_error('Failed to create contact')
            
        except Exception as e:
            print(f"Error creating contact: {e}")
            self._send_error(f'Error creating contact: {str(e)}', 500)

def main():
    """Start the Supabase API server"""
    # Change to the directory containing the script
    os.chdir(Path(__file__).parent)
    
    # Test Supabase connection
    try:
        result = supabase.table('contacts').select('count', count='exact').execute()
        print(f"✅ Supabase connected successfully")
        print(f"📊 Current contacts in database: {result.count if hasattr(result, 'count') else 'unknown'}")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return
    
    # Start server
    server = HTTPServer(('localhost', PORT), SupabaseContactsAPI)
    print(f"🚀 Supabase Contacts API server running at http://localhost:{PORT}")
    print(f"📊 Health check: http://localhost:{PORT}/api/health")
    print(f"📋 Contacts endpoint: http://localhost:{PORT}/api/contacts")
    print(f"📤 Import endpoint: http://localhost:{PORT}/api/contacts/import")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
