#!/usr/bin/env python3
"""
API Server for handling contact import and management
Supports CSV import, contact CRUD operations, and data validation
"""

import os
import json
import csv
import io
import uuid
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3
import traceback

# Configuration
PORT = 3000
DB_FILE = 'contacts.db'

class ContactsAPI(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
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
    
    def _get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    
    def _init_database(self):
        """Initialize the database with the contacts table"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        # Create contacts table (SQLite version of the PostgreSQL schema)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                
                -- Sponsor information
                sponsor TEXT,
                sponsor_first TEXT,
                sponsor_last TEXT,
                
                -- User and contact details
                user_id TEXT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                email_valid INTEGER DEFAULT NULL,
                phone TEXT,
                
                -- Address information
                address TEXT,
                city TEXT,
                state TEXT,
                zip TEXT,
                
                -- Status and rating
                status TEXT,
                rating TEXT,
                
                -- Technical details
                ip_address TEXT,
                date_created TEXT DEFAULT CURRENT_TIMESTAMP,
                timezone TEXT,
                
                -- Phone type information
                cell INTEGER DEFAULT NULL,
                carrier TEXT,
                landline INTEGER DEFAULT NULL,
                voip INTEGER DEFAULT NULL,
                other_phone INTEGER DEFAULT NULL,
                foreign_number INTEGER DEFAULT NULL,
                country TEXT DEFAULT 'US',
                
                -- Metadata
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(first_name, last_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_sponsor ON contacts(sponsor)')
        
        conn.commit()
        conn.close()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Serve static files
        if path.startswith('/static/'):
            self._serve_static_file(path[8:])  # Remove '/static/' prefix
        # Serve HTML files
        elif path == '/' or path == '/contacts':
            self._serve_html_file('contacts_new.html')
        elif path == '/contacts_new.html':
            self._serve_html_file('contacts_new.html')
        elif path == '/index.html':
            self._serve_html_file('index.html')
        # API endpoints
        elif path == '/api/contacts':
            self._handle_get_contacts(parsed_path.query)
        elif path == '/api/health':
            self._handle_health_check()
        else:
            self._send_error('Endpoint not found', 404)
    
    def _serve_static_file(self, filename):
        """Serve static files (CSS, JS, images)"""
        try:
            static_path = Path(__file__).parent / 'static' / filename
            if static_path.exists() and static_path.is_file():
                # Determine content type
                content_type = 'text/plain'
                if filename.endswith('.css'):
                    content_type = 'text/css'
                elif filename.endswith('.js'):
                    content_type = 'application/javascript'
                elif filename.endswith('.png'):
                    content_type = 'image/png'
                elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif filename.endswith('.gif'):
                    content_type = 'image/gif'
                elif filename.endswith('.svg'):
                    content_type = 'image/svg+xml'
                
                # Read file
                if content_type.startswith('image/'):
                    with open(static_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    with open(static_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
            else:
                self._send_error(f'Static file not found: {filename}', 404)
        except Exception as e:
            self._send_error(f'Error serving static file: {str(e)}', 500)
    
    def _serve_html_file(self, filename):
        """Serve HTML files"""
        try:
            file_path = Path(__file__).parent / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self._send_error(f'File not found: {filename}', 404)
        except Exception as e:
            self._send_error(f'Error serving file: {str(e)}', 500)
    
    def do_PUT(self):
        """Handle PUT requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith('/api/contacts/'):
            contact_id = path.split('/')[-1]
            self._handle_update_contact(contact_id)
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
        self._send_json_response({
            'status': 'healthy',
            'service': 'contacts-api',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    
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
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Build query with search
            base_query = 'FROM contacts'
            where_clause = ''
            params = []
            
            if search:
                where_clause = '''WHERE 
                    first_name LIKE ? OR 
                    last_name LIKE ? OR 
                    email LIKE ? OR 
                    phone LIKE ? OR
                    sponsor LIKE ?'''
                search_param = f'%{search}%'
                params = [search_param] * 5
            
            # Get total count
            count_query = f'SELECT COUNT(*) {base_query} {where_clause}'
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Get contacts with pagination
            contacts_query = f'''
                SELECT * {base_query} {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            '''
            cursor.execute(contacts_query, params + [per_page, offset])
            
            contacts = []
            for row in cursor.fetchall():
                contact = dict(row)
                contacts.append(contact)
            
            conn.close()
            
            self._send_json_response({
                'contacts': contacts,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'pages': (total_count + per_page - 1) // per_page
                },
                'search': search
            })
            
        except Exception as e:
            print(f"Error in get_contacts: {e}")
            print(traceback.format_exc())
            self._send_error(f'Error retrieving contacts: {str(e)}', 500)
    
    def _handle_import_contacts(self):
        """Handle CSV import of contacts"""
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
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            imported_count = 0
            errors = []
            
            for i, contact_data in enumerate(contacts_data):
                try:
                    # Generate UUID for new contact
                    contact_id = str(uuid.uuid4())
                    
                    # Prepare insert data with validation
                    insert_data = {
                        'id': contact_id,
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
                        'country': contact_data.get('country', 'US'),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Convert empty strings to None for nullable fields
                    for key, value in insert_data.items():
                        if value == '':
                            insert_data[key] = None
                    
                    # Insert contact
                    columns = ', '.join(insert_data.keys())
                    placeholders = ', '.join(['?' for _ in insert_data])
                    query = f'INSERT INTO contacts ({columns}) VALUES ({placeholders})'
                    
                    cursor.execute(query, list(insert_data.values()))
                    imported_count += 1
                    
                except Exception as row_error:
                    errors.append(f'Row {i + 1}: {str(row_error)}')
                    print(f"Error importing row {i + 1}: {row_error}")
            
            conn.commit()
            conn.close()
            
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
            return int(value)
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ('true', '1', 'yes', 'y', 'on'):
                return 1
            elif value in ('false', '0', 'no', 'n', 'off'):
                return 0
        return None
    
    def _handle_create_contact(self):
        """Handle creating a single contact"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            contact_data = json.loads(post_data.decode('utf-8'))
            
            # Implementation for single contact creation
            # Similar to import but for single contact
            self._send_json_response({'message': 'Single contact creation not implemented yet'})
            
        except Exception as e:
            self._send_error(f'Error creating contact: {str(e)}', 500)
    
    def _handle_update_contact(self, contact_id):
        """Handle updating a single contact field"""
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            update_data = json.loads(post_data.decode('utf-8'))
            
            if not update_data:
                self._send_error('No update data provided')
                return
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Build update query
            set_clauses = []
            values = []
            
            for field, value in update_data.items():
                # Validate field name to prevent SQL injection
                allowed_fields = [
                    'sponsor', 'sponsor_first', 'sponsor_last', 'user_id', 'first_name', 'last_name',
                    'email', 'email_valid', 'phone', 'address', 'city', 'state', 'zip', 'status',
                    'rating', 'ip_address', 'date_created', 'timezone', 'cell', 'carrier',
                    'landline', 'voip', 'other_phone', 'foreign_number', 'country'
                ]
                
                if field in allowed_fields:
                    set_clauses.append(f'{field} = ?')
                    values.append(value)
            
            if not set_clauses:
                self._send_error('No valid fields to update')
                return
            
            # Add updated_at timestamp
            set_clauses.append('updated_at = ?')
            values.append(datetime.now().isoformat())
            
            # Execute update
            query = f"UPDATE contacts SET {', '.join(set_clauses)} WHERE id = ?"
            values.append(contact_id)
            
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                self._send_error('Contact not found', 404)
                return
            
            conn.commit()
            conn.close()
            
            self._send_json_response({
                'success': True,
                'message': 'Contact updated successfully',
                'updated_fields': list(update_data.keys())
            })
            
        except Exception as e:
            print(f"Error in update_contact: {e}")
            print(traceback.format_exc())
            self._send_error(f'Error updating contact: {str(e)}', 500)

def main():
    """Start the API server"""
    # Change to the directory containing the script
    os.chdir(Path(__file__).parent)
    
    # Initialize database
    try:
        # Create a temporary instance just to initialize the database
        temp_db = ContactsAPI
        temp_db._init_database = lambda self: init_database()
        init_database()
        print(f"✅ Database initialized at {DB_FILE}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return
    
    # Start server
    server = HTTPServer(('localhost', PORT), ContactsAPI)
    print(f"🚀 Contacts API server running at http://localhost:{PORT}")
    print(f"📊 Health check: http://localhost:{PORT}/api/health")
    print(f"📋 Contacts endpoint: http://localhost:{PORT}/api/contacts")
    print(f"📤 Import endpoint: http://localhost:{PORT}/api/contacts/import")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")

def init_database():
    """Initialize the database with the contacts table (standalone function)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create contacts table (SQLite version of the PostgreSQL schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            
            -- Sponsor information
            sponsor TEXT,
            sponsor_first TEXT,
            sponsor_last TEXT,
            
            -- User and contact details
            user_id TEXT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            email_valid INTEGER DEFAULT NULL,
            phone TEXT,
            
            -- Address information
            address TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            
            -- Status and rating
            status TEXT,
            rating TEXT,
            
            -- Technical details
            ip_address TEXT,
            date_created TEXT DEFAULT CURRENT_TIMESTAMP,
            timezone TEXT,
            
            -- Phone type information
            cell INTEGER DEFAULT NULL,
            carrier TEXT,
            landline INTEGER DEFAULT NULL,
            voip INTEGER DEFAULT NULL,
            other_phone INTEGER DEFAULT NULL,
            foreign_number INTEGER DEFAULT NULL,
            country TEXT DEFAULT 'US',
            
            -- Metadata
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(first_name, last_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_sponsor ON contacts(sponsor)')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
