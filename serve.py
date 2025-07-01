#!/usr/bin/env python3
"""
Simple HTTP server to serve the account analysis page
Run this script and go to http://localhost:3000
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Change to the directory containing the HTML files
os.chdir(Path(__file__).parent)

PORT = 3002

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}")
        print(f"📊 Account Analysis: http://localhost:{PORT}/complete_account_analysis.html")
        print(f"🔄 Account Switcher: http://localhost:{PORT}/simple_account_switcher.html")
        print(f"👑 Admin Panel: http://localhost:{PORT}/admin.html")
        print(f"🏠 Dashboard: http://localhost:{PORT}/dashboard.html")
        print("\nPress Ctrl+C to stop the server")
        
        # Automatically open the analysis page
        webbrowser.open(f"http://localhost:{PORT}/complete_account_analysis.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
