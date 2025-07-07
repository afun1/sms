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

# Initialize delivery reports database
def init_delivery_reports_db():
    """Initialize the delivery reports database table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create delivery_reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_reports (
            id TEXT PRIMARY KEY,
            message_id TEXT,
            phone_number TEXT,
            status TEXT,
            timestamp TEXT,
            error_code TEXT,
            error_text TEXT,
            provider TEXT,
            received_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Delivery reports database initialized")

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
        """Initialize the database with users and contacts tables"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        # Create users table for role-based access
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                email TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                role TEXT CHECK(role IN ('user', 'manager', 'supervisor', 'admin')) DEFAULT 'user',
                manager_id TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (manager_id) REFERENCES users (id)
            )
        ''')
        
        # Create contacts table (SQLite version of the PostgreSQL schema)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                
                -- Assignment information
                assigned_to TEXT,
                
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
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (assigned_to) REFERENCES users (id)
            )
        ''')
        
        # Create indexes for users table
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_manager ON users(manager_id)')
        
        # Create indexes for contacts table
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_assigned_to ON contacts(assigned_to)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(first_name, last_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_sponsor ON contacts(sponsor)')
        
        conn.commit()
        
        # Create default admin user if none exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            admin_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO users (id, email, first_name, last_name, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, 'admin@sparky.com', 'Admin', 'User', 'admin', 1))
            conn.commit()
            print(f"✅ Created default admin user: admin@sparky.com")
        
        # Check if manager user exists (the one used by frontend)
        cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', ('user-manager-example-com',))
        manager_count = cursor.fetchone()[0]
        
        if manager_count == 0:
            cursor.execute('''
                INSERT INTO users (id, email, first_name, last_name, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('user-manager-example-com', 'john+3@tpnlife.com', 'John', 'Manager', 'manager', 1))
            conn.commit()
            print(f"✅ Created manager user: user-manager-example-com")
        
        # Debug: Show all users
        cursor.execute('SELECT id, email, role FROM users')
        users = cursor.fetchall()
        print(f"[DEBUG] Users in database:")
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Role: {user[2]}")
        
        conn.close()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        print(f"[DEBUG] GET request: {self.path}")
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Serve static files
        if path.startswith('/static/'):
            self._serve_static_file(path[8:])  # Remove '/static/' prefix
        # Serve HTML files
        elif path == '/':
            self._serve_html_file('index.html')
        elif path == '/contacts' or path == '/list':
            self._serve_html_file('list.html')
        elif path == '/list.html':
            self._serve_html_file('list.html')
        elif path == '/index.html':
            self._serve_html_file('index.html')
        elif path == '/login.html' or path == '/login':
            self._serve_html_file('login.html')
        elif path == '/ai_editor.html':
            self._serve_html_file('ai_editor.html')
        elif path == '/sms_editor.html':
            self._serve_html_file('sms_editor.html')
        elif path == '/rvm_editor.html':
            self._serve_html_file('rvm_editor.html')
        elif path == '/email_editor.html':
            self._serve_html_file('email_editor.html')
        elif path == '/campaign_builder.html':
            self._serve_html_file('campaign_builder.html')
        elif path == '/assets.html':
            self._serve_html_file('assets.html')
        elif path == '/admin.html':
            self._serve_html_file('admin.html')
        # API endpoints
        elif path == '/api/contacts':
            print(f"[DEBUG] GET /api/contacts - query: {parsed_path.query}")
            self._handle_get_contacts(parsed_path.query)
        elif path == '/api/users':
            self._handle_get_users(parsed_path.query)
        elif path == '/api/health':
            self._handle_health_check()
        elif path == '/api/delivery-reports':
            self._handle_get_delivery_reports()
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
        elif path == '/api/delivery-reports':
            self._handle_delivery_reports()
        elif path == '/api/webhook/clicksend':
            self._handle_clicksend_webhook()
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
        """Get contacts with role-based filtering, pagination, and search"""
        print(f"[DEBUG] _handle_get_contacts called with query: {query_string}")
        import sys
        sys.stdout.flush()
        try:
            query_params = parse_qs(query_string) if query_string else {}
            
            # Get pagination parameters
            page = int(query_params.get('page', [1])[0])
            per_page = int(query_params.get('per_page', [100])[0])
            offset = (page - 1) * per_page
            
            # Get search parameter
            search = query_params.get('search', [''])[0]
            
            # Get current user info for role-based filtering
            current_user_id = query_params.get('current_user_id', [None])[0]
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Initialize params list
            params = []
            
            # Get user role and build role-based access control
            user_role = 'user'  # Default role
            print(f"[DEBUG] Looking up user: {current_user_id}")
            if current_user_id:
                cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
                user_result = cursor.fetchone()
                print(f"[DEBUG] User lookup result: {user_result}")
                if user_result:
                    user_role = user_result['role']
                    print(f"[DEBUG] Found user role: {user_role}")
                else:
                    print(f"[DEBUG] User not found, using default role: {user_role}")
            else:
                print(f"[DEBUG] No current_user_id provided, using default role: {user_role}")
            
            # Build base query with role-based filtering
            # TEMPORARY: Disable all filtering for debugging
            base_query = 'FROM contacts c LEFT JOIN users u ON c.assigned_to = u.id'
            role_conditions = []
            
            where_conditions = role_conditions.copy()
            
            # Add search conditions
            if search:
                search_conditions = '''(
                    c.first_name LIKE ? OR 
                    c.last_name LIKE ? OR 
                    c.email LIKE ? OR 
                    c.phone LIKE ? OR
                    c.sponsor LIKE ?
                )'''
                where_conditions.append(search_conditions)
                search_param = f'%{search}%'
                params.extend([search_param] * 5)
            
            # Combine WHERE conditions
            where_clause = ''
            if where_conditions:
                where_clause = 'WHERE ' + ' AND '.join(where_conditions)
            
            # Get total count
            count_query = f'SELECT COUNT(*) {base_query} {where_clause}'
            print(f"[DEBUG] User role: {user_role}")
            print(f"[DEBUG] Count query: {count_query}")
            print(f"[DEBUG] Query params: {params}")
            import sys
            sys.stdout.flush()
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            print(f"[DEBUG] Total count result: {total_count}")
            sys.stdout.flush()
            
            # Get contacts with pagination
            contacts_query = f'''
                SELECT c.*, 
                       u.first_name as assigned_first_name, 
                       u.last_name as assigned_last_name,
                       u.email as assigned_email
                {base_query} 
                {where_clause}
                ORDER BY c.created_at DESC
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
                'search': search,
                'user_role': user_role,
                'filtered_by_role': current_user_id is not None
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
                        'assigned_to': contact_data.get('assigned_to', ''),
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
                    'assigned_to', 'sponsor', 'sponsor_first', 'sponsor_last', 'user_id', 'first_name', 'last_name',
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
    
    def _handle_get_users(self, query_string):
        """Get users with role-based filtering - MODIFIED: Now shows all users to everyone"""
        try:
            query_params = parse_qs(query_string) if query_string else {}
            
            # Get current user info from session/headers (simplified for demo)
            current_user_id = query_params.get('current_user_id', [None])[0]
            
            # BYPASS: Don't require authentication - let everyone see admin view
            # if not current_user_id:
            #     self._send_error('User authentication required', 401)
            #     return
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Get current user's role if provided, otherwise default to admin view
            current_role = 'admin'  # Default to admin view for everyone
            if current_user_id:
                cursor.execute('SELECT role, manager_id FROM users WHERE id = ?', (current_user_id,))
                current_user = cursor.fetchone()
                if current_user:
                    current_role = current_user['role']
            
            # MODIFIED: Always show admin view (all users) regardless of actual role
            users_query = '''
                SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.is_active,
                       m.first_name as manager_first_name, m.last_name as manager_last_name
                FROM users u
                LEFT JOIN users m ON u.manager_id = m.id
                WHERE u.is_active = 1
                ORDER BY u.role, u.first_name, u.last_name
            '''
            cursor.execute(users_query)
            
            users = []
            for row in cursor.fetchall():
                user = dict(row)
                users.append(user)
            
            conn.close()
            
            self._send_json_response({
                'users': users,
                'current_user_role': 'admin',  # Always report admin role
                'total': len(users)
            })
            
        except Exception as e:
            print(f"Error in get_users: {e}")
            print(traceback.format_exc())
            self._send_error(f'Error retrieving users: {str(e)}', 500)
    
    def _handle_delivery_reports(self):
        """Handle incoming delivery reports from the SMS provider"""
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            report_data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['id', 'message_id', 'phone_number', 'status', 'timestamp']
            for field in required_fields:
                if field not in report_data:
                    self._send_error(f'Missing required field: {field}', 400)
                    return
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Insert or update delivery report
            report_id = report_data['id']
            cursor.execute('''
                INSERT INTO delivery_reports (id, message_id, phone_number, status, timestamp, error_code, error_text, provider)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    timestamp = excluded.timestamp,
                    error_code = excluded.error_code,
                    error_text = excluded.error_text,
                    provider = excluded.provider,
                    received_at = CURRENT_TIMESTAMP
            ''', (
                report_id,
                report_data.get('message_id'),
                report_data.get('phone_number'),
                report_data.get('status'),
                report_data.get('timestamp'),
                report_data.get('error_code'),
                report_data.get('error_text'),
                report_data.get('provider')
            ))
            
            conn.commit()
            conn.close()
            
            self._send_json_response({'success': True, 'message': 'Delivery report processed'})
            
        except Exception as e:
            print(f"Error in delivery report handling: {e}")
            print(traceback.format_exc())
            self._send_error(f'Error processing delivery report: {str(e)}', 500)
    
    def _handle_get_delivery_reports(self):
        """Handle GET /api/delivery-reports - Return all delivery reports"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, message_id, phone_number, status, timestamp, 
                       error_code, error_text, provider, received_at
                FROM delivery_reports
                ORDER BY received_at DESC
            ''')
            
            reports = cursor.fetchall()
            conn.close()
            
            # Convert to dict format
            report_dict = {}
            for report in reports:
                report_dict[report[0]] = {
                    'id': report[0],
                    'message_id': report[1],
                    'phone_number': report[2],
                    'status': report[3],
                    'timestamp': report[4],
                    'error_code': report[5],
                    'error_text': report[6],
                    'provider': report[7],
                    'received_at': report[8]
                }
            
            self._send_json_response({
                'success': True,
                'reports': report_dict,
                'count': len(reports)
            })
            
        except Exception as e:
            print(f"[ERROR] Error fetching delivery reports: {e}")
            self._send_error(f'Error fetching delivery reports: {str(e)}', 500)
    
    def _handle_clicksend_webhook(self):
        """Handle POST /api/webhook/clicksend - ClickSend delivery report webhook"""
        try:
            # Get the content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read the request body
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                webhook_data = json.loads(post_data.decode('utf-8'))
            else:
                webhook_data = {}
            
            print(f"[DEBUG] ClickSend webhook received: {webhook_data}")
            
            # Process the webhook data
            if 'messages' in webhook_data:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                
                for message in webhook_data['messages']:
                    # Extract message details
                    message_id = message.get('message_id')
                    phone_number = message.get('to', message.get('phone_number'))
                    status = message.get('status')
                    timestamp = message.get('date', datetime.now().isoformat())
                    error_code = message.get('error_code')
                    error_text = message.get('error_text')
                    
                    # Insert or update delivery report
                    cursor.execute('''
                        INSERT OR REPLACE INTO delivery_reports 
                        (id, message_id, phone_number, status, timestamp, error_code, error_text, provider, received_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        message_id or str(uuid.uuid4()),
                        message_id,
                        phone_number,
                        status,
                        timestamp,
                        error_code,
                        error_text,
                        'clicksend',
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                conn.close()
                
                print(f"[DEBUG] Processed {len(webhook_data['messages'])} delivery reports")
            
            # Send success response
            self._send_json_response({
                'success': True,
                'message': 'Webhook processed successfully'
            })
            
        except Exception as e:
            print(f"[ERROR] Error processing ClickSend webhook: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            self._send_error(f'Error processing webhook: {str(e)}', 500)

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
    
    # Initialize delivery reports database
    try:
        init_delivery_reports_db()
        
        # Add some sample delivery reports for testing
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if sample data already exists
        cursor.execute('SELECT COUNT(*) FROM delivery_reports')
        report_count = cursor.fetchone()[0]
        
        if report_count == 0:
            # Add sample delivery reports
            sample_reports = [
                {
                    'id': 'msg-001',
                    'message_id': 'CS-MSG-001',
                    'phone_number': '+1234567890',
                    'status': 'Delivered',
                    'timestamp': '2025-07-06T10:30:00Z',
                    'error_code': None,
                    'error_text': None,
                    'provider': 'clicksend'
                },
                {
                    'id': 'msg-002',
                    'message_id': 'CS-MSG-002',
                    'phone_number': '+1234567891',
                    'status': 'Failed',
                    'timestamp': '2025-07-06T10:31:00Z',
                    'error_code': '400',
                    'error_text': 'Invalid phone number',
                    'provider': 'clicksend'
                },
                {
                    'id': 'msg-003',
                    'message_id': 'CS-MSG-003',
                    'phone_number': '+1234567892',
                    'status': 'Delivered',
                    'timestamp': '2025-07-06T10:32:00Z',
                    'error_code': None,
                    'error_text': None,
                    'provider': 'clicksend'
                },
                {
                    'id': 'msg-004',
                    'message_id': 'CS-MSG-004',
                    'phone_number': '+1234567893',
                    'status': 'Failed',
                    'timestamp': '2025-07-06T10:33:00Z',
                    'error_code': '500',
                    'error_text': 'Carrier rejected',
                    'provider': 'clicksend'
                },
                {
                    'id': 'msg-005',
                    'message_id': 'CS-MSG-005',
                    'phone_number': '+1234567894',
                    'status': 'Delivered',
                    'timestamp': '2025-07-06T10:34:00Z',
                    'error_code': None,
                    'error_text': None,
                    'provider': 'clicksend'
                }
            ]
            
            for report in sample_reports:
                cursor.execute('''
                    INSERT INTO delivery_reports 
                    (id, message_id, phone_number, status, timestamp, error_code, error_text, provider, received_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    report['id'],
                    report['message_id'],
                    report['phone_number'],
                    report['status'],
                    report['timestamp'],
                    report['error_code'],
                    report['error_text'],
                    report['provider'],
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            print(f"✅ Added {len(sample_reports)} sample delivery reports")
        
        conn.close()
        
    except Exception as e:
        print(f"Error initializing delivery reports database: {e}")
        return
    
    # Start server
    server = HTTPServer(('localhost', PORT), ContactsAPI)
    print(f"🚀 Contacts API server running at http://localhost:{PORT}")
    print(f"📊 Health check: http://localhost:{PORT}/api/health")
    print(f"📋 Contacts endpoint: http://localhost:{PORT}/api/contacts")
    print(f"📤 Import endpoint: http://localhost:{PORT}/api/contacts/import")
    print(f"📦 Delivery reports endpoint: http://localhost:{PORT}/api/delivery-reports")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()
    except Exception as e:
        print(f"Error initializing delivery reports database: {e}")
        return
    
    # Start server
    server = HTTPServer(('localhost', PORT), ContactsAPI)
    print(f"🚀 Contacts API server running at http://localhost:{PORT}")
    print(f"📊 Health check: http://localhost:{PORT}/api/health")
    print(f"📋 Contacts endpoint: http://localhost:{PORT}/api/contacts")
    print(f"📤 Import endpoint: http://localhost:{PORT}/api/contacts/import")
    print(f"📦 Delivery reports endpoint: http://localhost:{PORT}/api/delivery-reports")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")

def init_database():
    """Initialize the database with users and contacts tables (standalone function)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table for role-based access
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            email TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            role TEXT CHECK(role IN ('user', 'manager', 'supervisor', 'admin')) DEFAULT 'user',
            manager_id TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES users (id)
        )
    ''')
    
    # Create contacts table (SQLite version of the PostgreSQL schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            
            -- Assignment information
            assigned_to TEXT,
            
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
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for users table
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_manager ON users(manager_id)')
    
    # Create indexes for contacts table
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_assigned_to ON contacts(assigned_to)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(first_name, last_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_sponsor ON contacts(sponsor)')
    
    conn.commit()
    
    # Create default admin user if none exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        admin_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO users (id, email, first_name, last_name, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (admin_id, 'admin@sparky.com', 'Admin', 'User', 'admin', 1))
        conn.commit()
        print(f"✅ Created default admin user: admin@sparky.com")
    
    # Check if manager user exists (the one used by frontend)
    cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', ('user-manager-example-com',))
    manager_count = cursor.fetchone()[0]
    
    if manager_count == 0:
        cursor.execute('''
            INSERT INTO users (id, email, first_name, last_name, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('user-manager-example-com', 'john+3@tpnlife.com', 'John', 'Manager', 'manager', 1))
        conn.commit()
        print(f"✅ Created manager user: user-manager-example-com")
    
    # Debug: Show all users
    cursor.execute('SELECT id, email, role FROM users')
    users = cursor.fetchall()
    print(f"[DEBUG] Users in database:")
    for user in users:
        print(f"  ID: {user[0]}, Email: {user[1]}, Role: {user[2]}")
    
    conn.close()

if __name__ == "__main__":
    main()
