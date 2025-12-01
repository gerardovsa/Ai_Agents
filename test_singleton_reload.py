import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_agents')
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_agents/AI_infrastructure')

# Force reload of module_registry
if 'core.module_registry' in sys.modules:
    del sys.modules['core.module_registry']

from pathlib import Path
from core.module_registry import get_module_registry

base_dir = Path('C:/Users/gpoli/GIT/AI_agents')

# Test the scenario flask_app.py encounters
print("Simulating flask_app.py loading sequence:")
print("="*60)

# First, import module_routes (which imports get_module_registry)
print("\n1. Importing module_routes (like flask_app.py line 161)...")
# This triggers _ensure_initialized() which scans UI/external/modules
registry = get_module_registry()
print(f"   After module_routes import: {len(registry.modules)} modules")
print(f"   _modules_loaded flag: {registry._modules_loaded}")

# Now try to initialize additional directories (like flask_app.py lines 278-293)
print("\n2. Scanning frontend/modules...")
frontend_dir = base_dir / 'frontend' / 'modules'
registry.initialize(str(frontend_dir))
print(f"   After frontend: {len(registry.modules)} modules")

print("\n3. Scanning UI/external/modules...")
external_dir = base_dir / 'UI' / 'external' / 'modules'
registry.initialize(str(external_dir))
print(f"   After UI/external: {len(registry.modules)} modules")

print("\n4. Scanning UI/modules...")
ui_dir = base_dir / 'UI' / 'modules'
registry.initialize(str(ui_dir))
print(f"   After UI/modules: {len(registry.modules)} modules")

# Set loaded flag
registry._modules_loaded = True

# Check results
print("\n" + "="*60)
print("FINAL RESULTS:")
print("="*60)
synergy = registry.get_module('synergy_sessions')
workflow = registry.get_module('workflow_automation')
print(f"Total modules: {len(registry.modules)}")
print(f"synergy_sessions: {'FOUND' if synergy else 'NOT FOUND'}")
print(f"workflow_automation: {'FOUND' if workflow else 'NOT FOUND'}")
