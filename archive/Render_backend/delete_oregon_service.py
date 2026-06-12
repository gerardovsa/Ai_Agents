"""
Delete Old Oregon AI Agents Service
=====================================

This script safely deletes the old Oregon-based AI Agents service after
you've verified the new Singapore Docker deployment is working.

OLD SERVICE TO DELETE:
- Service ID: srv-d40tai15pdvs73ddh4m0
- Name: ai-agents-backend
- Region: Oregon (wrong for Australia)
- Env: Python (should be Docker)
- URL: https://ai-agents-backend-2oi8.onrender.com

⚠️  IMPORTANT: Only run this AFTER:
1. New Singapore service is deployed and tested
2. OAuth redirect URLs are updated to new service
3. All users are redirected to new URL
4. You've confirmed new service works correctly

This action is IRREVERSIBLE!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from render_api_client import RenderAPIClient


def delete_oregon_service():
    """Delete the old Oregon AI Agents service"""
    
    OLD_SERVICE_ID = "srv-d40tai15pdvs73ddh4m0"
    OLD_SERVICE_NAME = "ai-agents-backend"
    OLD_SERVICE_URL = "https://ai-agents-backend-2oi8.onrender.com"
    
    print("\n" + "="*80)
    print("  DELETE OLD OREGON SERVICE")
    print("="*80)
    
    print(f"\n⚠️  WARNING: You are about to DELETE the following service:")
    print(f"\n  Service ID:   {OLD_SERVICE_ID}")
    print(f"  Service Name: {OLD_SERVICE_NAME}")
    print(f"  Service URL:  {OLD_SERVICE_URL}")
    print(f"  Region:       Oregon")
    print(f"  Environment:  Python")
    
    print("\n" + "="*80)
    print("PRE-DELETION CHECKLIST")
    print("="*80)
    
    checks = [
        "✅ New Singapore Docker service is deployed and working",
        "✅ New service URL is tested and functional",
        "✅ OAuth redirect URLs updated to new service",
        "✅ All API keys configured in new service",
        "✅ Users are redirected to new URL",
        "✅ You have backup of any service-specific data"
    ]
    
    print("\nBefore proceeding, confirm you have completed:")
    for check in checks:
        print(f"  {check}")
    
    print("\n" + "="*80)
    print("⚠️  THIS ACTION IS IRREVERSIBLE!")
    print("="*80)
    
    # First confirmation
    print("\nType the service ID to confirm deletion:")
    confirmation1 = input(f"Enter '{OLD_SERVICE_ID}': ").strip()
    
    if confirmation1 != OLD_SERVICE_ID:
        print("\n❌ Service ID did not match. Deletion cancelled.")
        return False
    
    # Second confirmation
    print("\nAre you ABSOLUTELY SURE you want to delete this service?")
    confirmation2 = input("Type 'DELETE' to proceed: ").strip()
    
    if confirmation2 != 'DELETE':
        print("\n❌ Confirmation failed. Deletion cancelled.")
        return False
    
    # Perform deletion
    print("\n⏳ Deleting service...")
    
    try:
        client = RenderAPIClient()
        result = client.delete_service(OLD_SERVICE_ID)
        
        print("\n✅ Service deleted successfully!")
        print("\nThe following service has been removed:")
        print(f"  {OLD_SERVICE_NAME} ({OLD_SERVICE_ID})")
        print(f"\nURL {OLD_SERVICE_URL} is now inactive.")
        
        print("\n" + "="*80)
        print("POST-DELETION TASKS")
        print("="*80)
        print("\n1. Verify new Singapore service is handling all traffic")
        print("2. Update any documentation with new URL")
        print("3. Update browser bookmarks if needed")
        print("4. Consider downgrading Render plan if not needed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error deleting service: {e}")
        print("\nYou may need to delete manually:")
        print(f"https://dashboard.render.com/web/{OLD_SERVICE_ID}")
        return False


def main():
    """Main entry point"""
    success = delete_oregon_service()
    
    if success:
        print("\n✅ Deletion completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Deletion cancelled or failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
