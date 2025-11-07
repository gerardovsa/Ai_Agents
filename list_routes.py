"""List all Flask routes"""
import sys
from pathlib import Path

# Add AI_infrastructure to path
root = Path(__file__).parent
sys.path.insert(0, str(root / "AI_infrastructure"))

from flask_app import app

print("\n" + "="*80)
print("FLASK ROUTES")
print("="*80 + "\n")

routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
        'path': str(rule)
    })

# Sort by path
routes.sort(key=lambda x: x['path'])

# Print routes
for route in routes:
    print(f"{route['methods']:10s} {route['path']}")

print(f"\n{'='*80}")
print(f"Total routes: {len(routes)}")
print("="*80 + "\n")

# Check for feedback routes specifically
feedback_routes = [r for r in routes if 'feedback' in r['path'].lower()]
if feedback_routes:
    print("FEEDBACK ROUTES FOUND:")
    for route in feedback_routes:
        print(f"  {route['methods']:10s} {route['path']}")
else:
    print("❌ NO FEEDBACK ROUTES FOUND")
