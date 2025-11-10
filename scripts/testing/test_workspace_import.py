"""Test workspace routes import"""
import sys
sys.path.insert(0, 'AI_infrastructure')

try:
    from routes.workspace_routes import workspace_bp
    print("SUCCESS - workspace_bp imported")
    print(f"Blueprint name: {workspace_bp.name}")
    print(f"Blueprint import name: {workspace_bp.import_name}")
except Exception as e:
    print(f"FAILED - {e}")
    import traceback
    traceback.print_exc()
