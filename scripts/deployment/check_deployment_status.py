"""Quick deployment status check"""
import requests
import json
from datetime import datetime

service_id = "srv-d4b2723uibrs73ff02t0"
api_key = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
headers = {"Authorization": f"Bearer {api_key}"}

# Get latest deployment
url = f"https://api.render.com/v1/services/{service_id}/deploys"
response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()

data = response.json()

# Handle API response format
if isinstance(data, list) and len(data) > 0:
    # Response is a list of deploy objects wrapped in {'deploy': {...}}
    latest = data[0].get('deploy', data[0]) if isinstance(data[0], dict) else data[0]
else:
    print("No deployments found")
    exit(0)

print("\n" + "="*70)
print("RENDER DEPLOYMENT STATUS")
print("="*70)
print(f"Status: {latest.get('status', 'unknown').upper()}")
print(f"Deploy ID: {latest.get('id', 'N/A')}")
print(f"Created: {latest.get('createdAt', 'N/A')}")
print(f"Updated: {latest.get('updatedAt', 'N/A')}")

# Show commit info if available
if 'commit' in latest:
    commit = latest['commit']
    print(f"Commit: {commit.get('id', 'N/A')[:8]}")
    print(f"Message: {commit.get('message', 'N/A')[:80]}...")
    
# Get logs
log_url = f"https://api.render.com/v1/services/{service_id}/deploys/{latest.get('id')}/logs"
try:
    log_response = requests.get(log_url, headers=headers, timeout=10)
    log_response.raise_for_status()
    logs = log_response.text
except Exception as e:
    print(f"\nWarning: Could not fetch logs: {e}")
    logs = ""
    
# Quick analysis
if logs:
    log_lines = logs.split('\n')
    errors = [l for l in log_lines if 'error' in l.lower() or 'exception' in l.lower() or 'failed' in l.lower()]
    success = [l for l in log_lines if 'Serving on' in l or 'Connected to Supabase' in l or 'tools loaded' in l.lower()]
    
    print("\n" + "="*70)
    print("LOG ANALYSIS")
    print("="*70)
    print(f"Total lines: {len(log_lines)}")
    print(f"Success markers: {len(success)}")
    print(f"Potential errors: {len(errors)}")
    
    if success:
        print("\nLast 5 success markers:")
        for marker in success[-5:]:
            print(f"  {marker[:100]}")
    
    if errors:
        print("\nLast 10 errors/warnings:")
        for error in errors[-10:]:
            print(f"  {error[:100]}")

print("\n" + "="*70)
status = latest.get('status', 'unknown')
if status == 'live':
    print("DEPLOYMENT SUCCESSFUL")
    print("\nTest endpoints:")
    print("  Health: https://ai-agents-backend-singapore.onrender.com/health")
    print("  Chat: POST https://ai-agents-backend-singapore.onrender.com/api/agent/chat")
elif status == 'failed':
    print("DEPLOYMENT FAILED - Review errors above")
else:
    print(f"DEPLOYMENT IN PROGRESS ({status})")
print("="*70 + "\n")
