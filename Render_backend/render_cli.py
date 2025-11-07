"""
Render CLI Tool - Query and manage Render.com services

Usage:
    python render_cli.py list                          # List all services
    python render_cli.py status <service-id>           # Get service status
    python render_cli.py logs <service-id>             # Get recent logs
    python render_cli.py deploys <service-id>          # List recent deploys
    python render_cli.py info                          # Show account info
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from render_api_client import RenderAPIClient
import json

# Load API key from environment or use default
API_KEY = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def list_services():
    """List all Render services"""
    print_header("RENDER SERVICES")
    
    client = RenderAPIClient(API_KEY)
    
    try:
        services = client.list_services(limit=50)
        
        if not services:
            print("\nNo services found.")
            return
        
        print(f"\nFound {len(services)} service(s):\n")
        
        for i, item in enumerate(services, 1):
            # Handle wrapped service structure
            service = item.get('service', item)
            
            name = service.get('name', 'N/A')
            service_id = service.get('id', 'N/A')
            service_type = service.get('type', 'N/A')
            suspended = service.get('suspended', 'unknown')
            
            details = service.get('serviceDetails', {})
            url = details.get('url', 'N/A')
            region = details.get('region', 'N/A')
            env = details.get('env', 'N/A')
            plan = details.get('plan', 'N/A')
            
            # Status indicator
            status_icon = "✅" if suspended == "not_suspended" else "⚠️"
            
            print(f"{i}. {status_icon} {name}")
            print(f"   ID:     {service_id}")
            print(f"   Type:   {service_type}")
            print(f"   URL:    {url}")
            print(f"   Region: {region}")
            print(f"   Plan:   {plan}")
            print(f"   Env:    {env}")
            print(f"   Status: {suspended}")
            print()
        
    except Exception as e:
        print(f"\n❌ Error listing services: {e}")
        import traceback
        traceback.print_exc()

def get_service_status(service_id):
    """Get detailed service status"""
    print_header(f"SERVICE STATUS: {service_id}")
    
    client = RenderAPIClient(API_KEY)
    
    try:
        service = client.get_service(service_id)
        
        print(f"\nName:       {service.get('name', 'N/A')}")
        print(f"Type:       {service.get('type', 'N/A')}")
        print(f"Created:    {service.get('createdAt', 'N/A')}")
        print(f"Updated:    {service.get('updatedAt', 'N/A')}")
        
        details = service.get('serviceDetails', {})
        print(f"\nURL:        {details.get('url', 'N/A')}")
        print(f"Region:     {details.get('region', 'N/A')}")
        print(f"Plan:       {details.get('plan', 'N/A')}")
        print(f"Env:        {details.get('env', 'N/A')}")
        print(f"Runtime:    {details.get('runtime', 'N/A')}")
        
        # Check if suspended
        suspended = service.get('suspended', 'N/A')
        if suspended == 'suspended':
            print(f"\n⚠️  WARNING: Service is SUSPENDED")
        elif suspended == 'not_suspended':
            print(f"\n✅ Service is ACTIVE")
        else:
            print(f"\nStatus:     {suspended}")
        
    except Exception as e:
        print(f"\n❌ Error getting service status: {e}")
        import traceback
        traceback.print_exc()

def get_service_logs(service_id, limit=50):
    """Get recent service logs"""
    print_header(f"SERVICE LOGS: {service_id}")
    
    client = RenderAPIClient(API_KEY)
    
    try:
        logs = client.get_service_logs(service_id, limit=limit)
        
        if not logs:
            print("\nNo logs found.")
            return
        
        print(f"\nShowing last {len(logs)} log entries:\n")
        
        for log in logs:
            timestamp = log.get('timestamp', 'N/A')
            message = log.get('message', '')
            print(f"[{timestamp}] {message}")
        
    except Exception as e:
        print(f"\n❌ Error getting logs: {e}")
        import traceback
        traceback.print_exc()

def list_deploys(service_id, limit=10):
    """List recent deploys for a service"""
    print_header(f"RECENT DEPLOYS: {service_id}")
    
    client = RenderAPIClient(API_KEY)
    
    try:
        deploys = client.list_deploys(service_id, limit=limit)
        
        if not deploys:
            print("\nNo deploys found.")
            return
        
        print(f"\nShowing last {len(deploys)} deploy(s):\n")
        
        for i, item in enumerate(deploys, 1):
            deploy = item.get('deploy', {})
            deploy_id = deploy.get('id', 'N/A')
            status = deploy.get('status', 'N/A')
            created = deploy.get('createdAt', 'N/A')
            commit = deploy.get('commit', {})
            commit_msg = commit.get('message', 'N/A')
            
            print(f"{i}. Deploy ID: {deploy_id}")
            print(f"   Status:     {status}")
            print(f"   Created:    {created}")
            print(f"   Commit:     {commit_msg}")
            print()
        
    except Exception as e:
        print(f"\n❌ Error listing deploys: {e}")
        import traceback
        traceback.print_exc()

def show_account_info():
    """Show Render account information"""
    print_header("RENDER ACCOUNT INFO")
    
    client = RenderAPIClient(API_KEY)
    
    try:
        # Get all services to show summary
        services = client.list_services(limit=100)
        
        print(f"\nAPI Key:    {API_KEY[:15]}...{API_KEY[-5:]}")
        print(f"Services:   {len(services)}")
        
        # Count by type
        types = {}
        regions = {}
        for s in services:
            stype = s.get('type', 'unknown')
            types[stype] = types.get(stype, 0) + 1
            
            region = s.get('serviceDetails', {}).get('region', 'unknown')
            regions[region] = regions.get(region, 0) + 1
        
        print(f"\nBy Type:")
        for stype, count in types.items():
            print(f"  - {stype}: {count}")
        
        print(f"\nBy Region:")
        for region, count in regions.items():
            print(f"  - {region}: {count}")
        
    except Exception as e:
        print(f"\n❌ Error getting account info: {e}")
        import traceback
        traceback.print_exc()

def show_usage():
    """Show usage information"""
    print("""
Render CLI Tool - Query and manage Render.com services

Usage:
    python render_cli.py list                          # List all services
    python render_cli.py status <service-id>           # Get service status
    python render_cli.py logs <service-id> [limit]     # Get recent logs
    python render_cli.py deploys <service-id> [limit]  # List recent deploys
    python render_cli.py info                          # Show account info

Examples:
    python render_cli.py list
    python render_cli.py status srv-abc123
    python render_cli.py logs srv-abc123 100
    python render_cli.py deploys srv-abc123 5

Environment Variables:
    RENDER_API_KEY    Your Render API key (optional, has default)
""")

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_services()
    
    elif command == 'status':
        if len(sys.argv) < 3:
            print("❌ Error: service-id required")
            print("Usage: python render_cli.py status <service-id>")
            return
        service_id = sys.argv[2]
        get_service_status(service_id)
    
    elif command == 'logs':
        if len(sys.argv) < 3:
            print("❌ Error: service-id required")
            print("Usage: python render_cli.py logs <service-id> [limit]")
            return
        service_id = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        get_service_logs(service_id, limit)
    
    elif command == 'deploys':
        if len(sys.argv) < 3:
            print("❌ Error: service-id required")
            print("Usage: python render_cli.py deploys <service-id> [limit]")
            return
        service_id = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        list_deploys(service_id, limit)
    
    elif command == 'info':
        show_account_info()
    
    elif command in ['help', '-h', '--help']:
        show_usage()
    
    else:
        print(f"❌ Unknown command: {command}")
        show_usage()

if __name__ == '__main__':
    main()
