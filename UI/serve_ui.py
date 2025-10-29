"""
Simple HTTP Server for Business AI Platform UI
Serves the frontend on port 8080
"""

import http.server
import socketserver
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for API requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"""
================================================================================
🌐 Business AI Platform UI Server
================================================================================
✅ Serving UI files from: {DIRECTORY}
🌐 Access at: http://localhost:{PORT}/business-ai-platform-v2.html
🔧 Flask Backend: http://localhost:5001
================================================================================
""")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ UI Server stopped")
            sys.exit(0)
