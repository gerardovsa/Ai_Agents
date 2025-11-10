"""
Simple HTTP Server for Business AI Platform UI
Serves the frontend on port 8080 to avoid CORS issues

CRITICAL: UI MUST be served via HTTP server (not file://)
- Modules use fetch() for manifest.json loading
- Browsers block CORS on file:// protocol
- HTTP server enables proper module loading

Usage:
    python serve_ui.py

Then open: http://localhost:8080/business-ai-platform-v2.html
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
    
    def log_message(self, format, *args):
        # Custom logging format
        if args[1] == '200':
            status_icon = '✅'
        elif args[1].startswith('3'):
            status_icon = '↩️'
        elif args[1].startswith('4'):
            status_icon = '⚠️'
        else:
            status_icon = '❌'
        
        print(f"{status_icon} {args[0]} - {args[1]} - {args[2] if len(args) > 2 else ''}")

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    Business AI Platform UI Server                          ║
╚════════════════════════════════════════════════════════════════════════════╝

📂 Serving UI files from: {DIRECTORY}

🌐 Main UI: http://localhost:{PORT}/business-ai-platform-v2.html
🔧 Flask Backend: http://localhost:5001 (must be running separately)

╔════════════════════════════════════════════════════════════════════════════╗
║ IMPORTANT: Module Loading Requires HTTP Server                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║ ❌ Opening HTML directly (file://) → CORS blocked                         ║
║ ✅ Using HTTP server (http://localhost:8080/) → Modules load correctly    ║
╚════════════════════════════════════════════════════════════════════════════╝

Press Ctrl+C to stop server...
""")
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ UI Server stopped gracefully")
        sys.exit(0)
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"\n❌ ERROR: Port {PORT} is already in use!")
            print(f"   Try: netstat -ano | findstr :{PORT}")
            print(f"   Then: taskkill /PID <PID> /F")
        else:
            print(f"\n❌ ERROR: {e}")
        sys.exit(1)
