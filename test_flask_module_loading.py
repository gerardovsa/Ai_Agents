import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_agents')
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_agents/AI_infrastructure')

from pathlib import Path
from core.module_registry import get_module_registry

base_dir = Path('C:/Users/gpoli/GIT/AI_agents')
registry = get_module_registry()

print(f"Before scanning: {len(registry.modules)} modules")

# Scan frontend/modules (like flask_app.py does)
frontend_modules_dir = base_dir / 'frontend' / 'modules'
print(f"\nScanning: {frontend_modules_dir}")
registry.initialize(str(frontend_modules_dir))
print(f"After frontend/: {len(registry.modules)} modules")

# Scan UI/external/modules
external_modules_dir = base_dir / 'UI' / 'external' / 'modules'
print(f"\nScanning: {external_modules_dir}")
registry.initialize(str(external_modules_dir))
print(f"After UI/external/: {len(registry.modules)} modules")

# Scan UI/modules
ui_modules_dir = base_dir / 'UI' / 'modules'
print(f"\nScanning: {ui_modules_dir}")
registry.initialize(str(ui_modules_dir))
print(f"After UI/modules/: {len(registry.modules)} modules")

# Check for synergy and workflow
synergy = registry.get_module('synergy_sessions')
workflow = registry.get_module('workflow_automation')

print(f"\nFinal results:")
print(f"  synergy_sessions: {'FOUND' if synergy else 'NOT FOUND'}")
print(f"  workflow_automation: {'FOUND' if workflow else 'NOT FOUND'}")

if synergy:
    print(f"\nsynergy module details:")
    print(f"  Name: {synergy.name}")
    print(f"  Has thread_card_integration: {synergy.thread_card_integration is not None}")
