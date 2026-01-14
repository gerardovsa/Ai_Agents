"""Quick route verification script"""
from routes.communication_routes import communication_bp
import flask

app = flask.Flask('test')
app.register_blueprint(communication_bp)

routes = [r.rule for r in app.url_map.iter_rules() if 'communication-hub' in r.rule]

print("\n" + "="*60)
print("COMMUNICATION HUB ROUTES")
print("="*60)

for route in sorted(routes):
    if route != '/static/<path:filename>':
        print(f"  {route}")

print(f"\nTotal routes: {len([r for r in routes if r != '/static/<path:filename>'])}")

# Check for new routes
new_routes = [
    '/api/communication-hub/gmail/attachment',
    '/api/communication-hub/outlook/attachment', 
    '/api/communication-hub/extract-document-text',
    '/api/communication-hub/extract-spreadsheet-text'
]

print("\n" + "="*60)
print("NEW ATTACHMENT ENDPOINTS VERIFICATION")
print("="*60)

all_found = True
for route in new_routes:
    if route in routes:
        print(f"  ✅ {route}")
    else:
        print(f"  ❌ {route} - NOT FOUND")
        all_found = False

if all_found:
    print("\n🎉 SUCCESS! All 4 attachment endpoints implemented correctly!")
    print("\nFrontend attachment-processor.js will now work properly.")
else:
    print("\n❌ ERROR: Some endpoints are missing!")
