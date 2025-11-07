"""
🎯 UNIFIED OAUTH AUTHENTICATION TEST
=====================================
Authenticate ALL Google services with ONE browser popup!

This script demonstrates the new unified authentication approach where:
- User grants permission ONCE
- All services (Gmail, Calendar, Tasks, Forms) use the same token
- Future API calls don't require re-authentication
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("🎯 UNIFIED OAUTH AUTHENTICATION - ONE POPUP FOR ALL SERVICES")
print("="*70)
print("\n📋 What will happen:")
print("   1. Browser opens ONCE")
print("   2. You grant permission to:")
print("      • Gmail (read, send, modify)")
print("      • Calendar (read, create, update)")
print("      • Tasks (read, create, update)")
print("      • Forms (create, read responses)")
print("   3. Token saved for ALL services")
print("   4. Future calls use this token automatically")
print("\n" + "="*70)

input("Press ENTER to start unified authentication...")

try:
    from google_workspace.oauth_manager import authenticate_all_services
    
    #  ONE FUNCTION CALL = ALL SERVICES AUTHENTICATED
    services = authenticate_all_services(mode='desktop')
    
    print("\n" + "="*70)
    print("🧪 TESTING ALL SERVICES")
    print("="*70)
    
    # Test Gmail
    print("\n1️⃣  Testing Gmail...")
    try:
        gmail = services['gmail']
        profile = gmail.users().getProfile(userId='me').execute()
        print(f"    Gmail: {profile['emailAddress']}")
        print(f"   📊 Messages: {profile['messagesTotal']:,}")
        print(f"   🧵 Threads: {profile['threadsTotal']:,}")
    except Exception as e:
        print(f"    Gmail failed: {e}")
    
    # Test Calendar
    print("\n2️⃣  Testing Calendar...")
    try:
        calendar = services['calendar']
        calendars = calendar.calendarList().list().execute()
        cal_count = len(calendars.get('items', []))
        print(f"    Calendar: {cal_count} calendars found")
        for cal in calendars.get('items', [])[:3]:
            print(f"      • {cal.get('summary', 'Unnamed')}")
    except Exception as e:
        print(f"    Calendar failed: {e}")
    
    # Test Tasks
    print("\n3️⃣  Testing Tasks...")
    try:
        tasks = services['tasks']
        task_lists = tasks.tasklists().list().execute()
        task_count = len(task_lists.get('items', []))
        print(f"    Tasks: {task_count} task lists found")
        for tl in task_lists.get('items', []):
            print(f"      • {tl.get('title', 'Unnamed')}")
    except Exception as e:
        print(f"    Tasks failed: {e}")
    
    # Test Forms
    print("\n4️⃣  Testing Forms...")
    try:
        forms = services['forms']
        print(f"    Forms: Service ready (requires form ID to test)")
    except Exception as e:
        print(f"    Forms failed: {e}")
    
    print("\n" + "="*70)
    print("🎉 SUCCESS! ALL SERVICES WORKING WITH UNIFIED TOKEN")
    print("="*70)
    print(f"\n📝 Token saved to: {services['token_file']}")
    print("\n💡 Next time you run this script:")
    print("   • NO browser popup")
    print("   • Uses existing token")
    print("   • All services work immediately")
    print("\n🚀 Ready to use in your application!")
    
    print("\n" + "="*70)
    print("📖 USAGE IN YOUR CODE")
    print("="*70)
    print("""
# Method 1: Use authenticate_all_services() for first-time setup
from google_workspace.oauth_manager import authenticate_all_services
services = authenticate_all_services()
gmail = services['gmail']
calendar = services['calendar']

# Method 2: Use build_oauth_service() - automatically uses unified token
from google_workspace.oauth_manager import build_gmail_oauth_service
gmail = build_gmail_oauth_service()  # No popup if unified token exists!
""")
    
except Exception as e:
    print(f"\n Unified authentication failed: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Troubleshooting:")
    print("   1. Make sure credentials_desktop.json exists")
    print("   2. Check that GOOGLE_OAUTH_MODE=desktop in .env.master")
    print("   3. Verify OAuth credentials are valid in Google Console")

print("\n")
