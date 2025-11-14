"""
Create a temporary Flask endpoint to download the database from Render

USAGE:
1. Run this script locally: python scripts/deployment/create_db_download_endpoint.py
2. It will start a local server on port 8888
3. Use ngrok or expose to internet: ngrok http 8888
4. Copy the ngrok URL
5. In Render Shell: wget YOUR_NGROK_URL/download-db -O /data/ai_infrastructure.db

SECURITY: Includes auth token, only works for 1 hour
"""

from flask import Flask, send_file, request, abort
from pathlib import Path
import secrets
import time

app = Flask(__name__)

# Generate one-time token
AUTH_TOKEN = secrets.token_urlsafe(32)
TOKEN_EXPIRES = time.time() + 3600  # 1 hour
DOWNLOADED = False

# Database path
root_dir = Path(__file__).parent.parent.parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

@app.route('/download-db')
def download_db():
    global DOWNLOADED
    
    # Check token
    token = request.args.get('token')
    if token != AUTH_TOKEN:
        abort(403, 'Invalid token')
    
    # Check expiry
    if time.time() > TOKEN_EXPIRES:
        abort(410, 'Token expired')
    
    # Only allow one download
    if DOWNLOADED:
        abort(410, 'Already downloaded')
    
    DOWNLOADED = True
    return send_file(db_path, as_attachment=True, download_name='ai_infrastructure.db')

@app.route('/health')
def health():
    return {
        'status': 'ready',
        'db_size_mb': round(db_path.stat().st_size / (1024 * 1024), 2),
        'expires_in': max(0, int(TOKEN_EXPIRES - time.time())),
        'downloaded': DOWNLOADED
    }

if __name__ == '__main__':
    print("=" * 70)
    print("DATABASE DOWNLOAD SERVER")
    print("=" * 70)
    print()
    print(f"Database: {db_path}")
    print(f"Size: {db_path.stat().st_size / (1024 * 1024):.2f} MB")
    print()
    print("Starting server on http://localhost:8888")
    print()
    print("NEXT STEPS:")
    print("1. Expose to internet with ngrok:")
    print("   ngrok http 8888")
    print()
    print("2. Copy the ngrok URL (https://xxxx.ngrok.io)")
    print()
    print("3. In Render Shell, run:")
    print(f"   wget 'YOUR_NGROK_URL/download-db?token={AUTH_TOKEN}' -O /data/ai_infrastructure.db")
    print()
    print("4. Verify:")
    print("   sqlite3 /data/ai_infrastructure.db 'SELECT COUNT(*) FROM users'")
    print()
    print(f"Auth token: {AUTH_TOKEN}")
    print(f"Expires in: 1 hour")
    print()
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=8888, debug=False)
