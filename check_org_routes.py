import sys, os
sys.path.insert(0, 'AI_infrastructure')
os.environ.setdefault('FLASK_ENV', 'development')

from flask import Flask
app = Flask(__name__)

try:
    from routes.organisation_credentials_routes import org_credentials_bp
    app.register_blueprint(org_credentials_bp)
    print('[OK] org_credentials_bp registered')
except Exception as e:
    print('[FAIL] org_credentials_bp:', e)
    import traceback
    traceback.print_exc()

print()
print('=== /api/org routes ===')
for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
    if '/api/org' in str(rule):
        methods = rule.methods - {'HEAD', 'OPTIONS'}
        print(f'  {methods} {rule}')
