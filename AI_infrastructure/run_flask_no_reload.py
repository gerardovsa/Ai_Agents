"""
Run Flask without auto-reloader to avoid Windows startup issues
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import app
from flask_app import app, socketio

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 STARTING FLASK APP (NO AUTO-RELOAD)")
    print("=" * 80)
    print("📡 Port: 4000")
    print("🔧 Debug: True")
    print("🔄 Auto-reload: DISABLED (prevents Windows hang)")
    print("=" * 80)
    print("\n🌐 Access at: http://localhost:4000")
    print("🏥 Health check: http://localhost:4000/health")
    print("\n")
    
    # Run without reloader
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False  # DISABLED to prevent Windows hang
    )
