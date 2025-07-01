#!/usr/bin/env python3
"""
Improved HTTP server with better error handling and chunked transfer
"""

import http.server
import socketserver
import os
import threading
import json
from pathlib import Path
from urllib.parse import urlparse
from supabase import create_client, Client

# Change to the directory containing the HTML files
os.chdir(Path(__file__).parent)

PORT = 3000

# Supabase configuration
SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q'

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class ImprovedHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def do_GET(self):
        """Handle GET requests, including API endpoints"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/contacts':
            self._handle_contacts_api()
        else:
            # Handle static files
            super().do_GET()

    def _handle_contacts_api(self):
        """Handle the contacts API endpoint"""
        try:
            # Fetch contacts from Supabase
            response = supabase.table('contacts').select('*').execute()
            
            # Prepare response data
            contacts_data = {
                'success': True,
                'contacts': response.data,
                'count': len(response.data)
            }
            
            # Send JSON response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            json_response = json.dumps(contacts_data, default=str)
            self.wfile.write(json_response.encode('utf-8'))
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(e),
                'contacts': []
            }
            
            json_response = json.dumps(error_response)
            self.wfile.write(json_response.encode('utf-8'))

    def end_headers(self):
        # Add minimal CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def copyfile(self, source, outputfile):
        """Copy data with better error handling"""
        try:
            # Use smaller chunks for better responsiveness
            while True:
                buf = source.read(8192)  # 8KB chunks instead of default 64KB
                if not buf:
                    break
                outputfile.write(buf)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # Handle client disconnects gracefully
            pass
        except Exception as e:
            print(f"Error serving file: {e}")

    def log_message(self, format, *args):
        """Reduce logging to essential errors only"""
        if "404" in str(args) or "500" in str(args):
            super().log_message(format, *args)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    try:
        with ThreadedTCPServer(("", PORT), ImprovedHandler) as httpd:
            print(f"🚀 Improved Server running at http://localhost:{PORT}")
            print(f"📝 SMS Editor: http://localhost:{PORT}/sms_editor.html")
            print(f"📊 Assets: http://localhost:{PORT}/assets.html")
            print(f"🏠 Dashboard: http://localhost:{PORT}/dashboard.html")
            print("\nPress Ctrl+C to stop the server")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
