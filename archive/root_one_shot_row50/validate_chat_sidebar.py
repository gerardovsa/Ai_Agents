"""
CHAT SIDEBAR VALIDATION SCRIPT
Validates Python backend dependencies and database schema
"""

import sys
import os

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

print("=" * 60)
print("CHAT SIDEBAR BACKEND VALIDATION")
print("=" * 60)
print()

# ==================== IMPORT CHECKS ====================

print("1. Checking Python Dependencies...")

required_imports = {
    'flask': 'Flask',
    'flask_socketio': 'Flask-SocketIO',
    'psycopg2': 'PostgreSQL Driver',
    'redis': 'Redis (optional)'
}

missing = []
for module, name in required_imports.items():
    try:
        __import__(module)
        print(f"  ✓ {name}: Available")
    except ImportError:
        print(f"  ✗ {name}: MISSING")
        missing.append(name)

if missing:
    print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
    print("Install with: pip install flask flask-socketio psycopg2-binary redis")
else:
    print("\n✓ All required dependencies available")

# ==================== MESSAGE SERVICE CHECK ====================

print("\n2. Checking Message Service...")

try:
    from message_service import MessageService
    print("  ✓ MessageService class: Found")
    
    # Check methods
    methods = [
        'save_message',
        'mark_delivered',
        'mark_read',
        'get_message_history',
        'get_user_conversations',
        'mark_conversation_read',
        'get_message',
        'delete_message'
    ]
    
    for method in methods:
        exists = hasattr(MessageService, method)
        status = '✓' if exists else '✗'
        print(f"  {status} MessageService.{method}: {'Defined' if exists else 'MISSING'}")
        
except ImportError as e:
    print(f"  ✗ MessageService: NOT FOUND - {e}")
    print("  ℹ Create message_service.py with MessageService class")

# ==================== FLASK APP CHECK ====================

print("\n3. Checking Flask App...")

try:
    from flask_app import app, socketio
    print("  ✓ Flask app: Loaded")
    print("  ✓ SocketIO: Loaded")
    
    # Check if message service is initialized
    if hasattr(app, 'message_service'):
        print("  ✓ message_service: Initialized in app")
    else:
        print("  ⚠ message_service: Not attached to app")
    
except ImportError as e:
    print(f"  ✗ Flask app: Cannot import - {e}")

# ==================== API ROUTES CHECK ====================

print("\n4. Checking Required API Routes...")

required_routes = [
    ('/api/messages/conversations', ['GET']),
    ('/api/messages/history', ['GET']),
    ('/api/messages/mark-read', ['POST']),
    ('/api/messages/<message_id>', ['DELETE']),
    ('/api/user/avatar/<user_id>', ['GET'])
]

try:
    from flask_app import app
    
    existing_routes = {}
    for rule in app.url_map.iter_rules():
        existing_routes[rule.rule] = list(rule.methods - {'HEAD', 'OPTIONS'})
    
    for route, methods in required_routes:
        # For routes with parameters, check if pattern exists
        route_pattern = route.replace('<message_id>', '<.*>').replace('<user_id>', '<.*>')
        found = False
        
        for existing_route in existing_routes.keys():
            if route in existing_route or existing_route in route:
                found = True
                break
        
        status = '✓' if found else '✗'
        print(f"  {status} {route} {methods}: {'Found' if found else 'MISSING'}")
        
except Exception as e:
    print(f"  ⚠ Cannot check routes: {e}")

# ==================== WEBSOCKET EVENTS CHECK ====================

print("\n5. Checking WebSocket Event Handlers...")

required_events = [
    'voice_call_offer',
    'voice_call_answer',
    'voice_call_ice_candidate',
    'voice_call_ended',
    'send_direct_message',
    'broadcast_message',
    'typing_start',
    'typing_stop',
    'mark_message_read'
]

try:
    from flask_app import socketio
    
    # Get registered event handlers
    if hasattr(socketio, 'handlers'):
        handlers = socketio.handlers
        print(f"  ℹ Total handlers registered: {len(handlers)}")
    else:
        print("  ⚠ Cannot inspect SocketIO handlers")
    
    # Check if events are likely registered (by checking if decorator was used)
    print("  ℹ Expected events (check flask_app.py manually):")
    for event in required_events:
        print(f"    • {event}")
        
except Exception as e:
    print(f"  ⚠ Cannot check SocketIO events: {e}")

# ==================== DATABASE SCHEMA CHECK ====================

print("\n6. Checking Database Schema...")

try:
    import psycopg2
    from config import DATABASE_CONFIG
    
    # Connect to database
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor()
    
    # Check messages table
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'messages'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    
    if columns:
        print("  ✓ messages table: Found")
        required_columns = [
            'message_id',
            'from_user_id',
            'to_user_id',
            'message',
            'timestamp',
            'delivered_to',
            'read_by',
            'is_broadcast'
        ]
        
        existing_columns = [col[0] for col in columns]
        
        for col in required_columns:
            exists = col in existing_columns
            status = '✓' if exists else '✗'
            print(f"  {status} Column '{col}': {'Found' if exists else 'MISSING'}")
    else:
        print("  ✗ messages table: NOT FOUND")
        print("  ℹ Run database migration to create table")
    
    cur.close()
    conn.close()
    
except ImportError:
    print("  ⚠ psycopg2 not available - cannot check database")
except Exception as e:
    print(f"  ⚠ Database check failed: {e}")

# ==================== FILE CHECKS ====================

print("\n7. Checking Required Files...")

required_files = [
    ('UI/shared/js/chat-sidebar.js', 'Chat Sidebar JavaScript'),
    ('UI/shared/css/chat-sidebar.css', 'Chat Sidebar CSS'),
    ('UI/shared/js/synergy-realtime.js', 'Synergy Realtime'),
    ('AI_infrastructure/message_service.py', 'Message Service (backend)')
]

for filepath, description in required_files:
    full_path = os.path.join(os.path.dirname(__file__), filepath)
    exists = os.path.exists(full_path)
    status = '✓' if exists else '✗'
    print(f"  {status} {description}: {'Found' if exists else 'MISSING'}")
    
    if exists:
        try:
            size = os.path.getsize(full_path)
            print(f"      Size: {size:,} bytes")
        except Exception as e:
            print(f"      Error getting stats: {e}")

# ==================== SYNTAX VALIDATION ====================

print("\n8. Python Syntax Validation...")

python_files = [
    'AI_infrastructure/message_service.py'
]

for filepath in python_files:
    full_path = os.path.join(os.path.dirname(__file__), filepath)
    
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, filepath, 'exec')
            print(f"  ✓ {filepath}: Valid syntax")
        except SyntaxError as e:
            print(f"  ✗ {filepath}: SYNTAX ERROR - {e}")
    else:
        print(f"  ⚠ {filepath}: File not found")

# ==================== SUMMARY ====================

print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

if not missing:
    print("✓ Python Dependencies: All available")
else:
    print(f"✗ Python Dependencies: {len(missing)} missing")

print("\n✓ Backend validation complete!")
print("\nNext steps:")
print("  1. Fix any missing dependencies/files")
print("  2. Add missing API routes to flask_app.py")
print("  3. Add WebSocket event handlers")
print("  4. Run smoke test in browser: Chat_SIDEBAR_SMOKE_TEST.js")
print("  5. Test multi-session with multiple browsers/devices")

print("\n" + "=" * 60)
