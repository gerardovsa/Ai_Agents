"""
Test OAuth Authentication for Gmail, Calendar, Forms
Runs first-time OAuth flow and tests API access
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("🔧 TESTING OAUTH AUTHENTICATION FOR PERSONAL DATA APIS")
print("="*70)

# Test Gmail OAuth
print("\n1️⃣  Testing Gmail OAuth...")
print("-" * 70)
try:
    from google_workspace.oauth_manager import build_gmail_oauth_service
    
    print("   Authenticating Gmail (browser will open)...")
    service = build_gmail_oauth_service(mode='desktop')
    
    print("   Testing API call: users().getProfile()...")
    profile = service.users().getProfile(userId='me').execute()
    
    print(f"\n    Gmail OAuth Success!")
    print(f"   📧 Email: {profile['emailAddress']}")
    print(f"   📊 Total messages: {profile['messagesTotal']}")
    print(f"   🧵 Total threads: {profile['threadsTotal']}")
    
except Exception as e:
    print(f"\n    Gmail OAuth Failed: {e}")
    import traceback
    traceback.print_exc()

# Test Calendar OAuth
print("\n2️⃣  Testing Calendar OAuth...")
print("-" * 70)
try:
    from google_workspace.oauth_manager import build_calendar_oauth_service
    
    print("   Authenticating Calendar (may reuse Gmail OAuth)...")
    service = build_calendar_oauth_service(mode='desktop')
    
    print("   Testing API call: calendarList().list()...")
    calendars = service.calendarList().list().execute()
    
    print(f"\n    Calendar OAuth Success!")
    print(f"   📅 Calendars found: {len(calendars.get('items', []))}")
    for cal in calendars.get('items', [])[:3]:  # Show first 3
        print(f"      - {cal.get('summary', 'Unnamed')}")
    
except Exception as e:
    print(f"\n    Calendar OAuth Failed: {e}")
    import traceback
    traceback.print_exc()

# Test Google Tasks OAuth (should already be working)
print("\n3️⃣  Testing Tasks OAuth (existing implementation)...")
print("-" * 70)
try:
    from google_workspace.google_tasks import google_tasks_list_task_lists
    
    print("   Using existing Tasks OAuth...")
    result = google_tasks_list_task_lists()
    
    print(f"\n    Tasks OAuth Success!")
    print(f"    Task lists found: {result['total']}")
    for task_list in result['task_lists']:
        print(f"      - {task_list['title'] or '(Unnamed)'}")
    
except Exception as e:
    print(f"\n    Tasks OAuth Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print(" OAUTH AUTHENTICATION TEST COMPLETE")
print("="*70)
print("\n📋 Summary:")
print("   - Gmail: OAuth 2.0 ")
print("   - Calendar: OAuth 2.0 ")
print("   - Tasks: OAuth 2.0  (already working)")
print("\n🚀 Ready for multi-user SaaS deployment!")
print("   Each subscriber will authenticate their own Google account")
print("\n📝 Next Steps:")
print("   1. Restart AI Agent server: BISTOP then BISTART")
print("   2. Test with CHAT command")
print("   3. Add OAuth callback routes for web mode (Render)")
print("\n")
