import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_agents')
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_agents/AI_infrastructure')

from core.module_registry import get_module_registry
from pathlib import Path

base_dir = Path('C:/Users/gpoli/GIT/AI_agents')
ui_modules_dir = base_dir / 'UI' / 'modules'

print(f"Scanning: {ui_modules_dir}")
print(f"Exists: {ui_modules_dir.exists()}")

registry = get_module_registry()
print(f"\nRegistry has {len(registry.modules)} modules before UI scan")

# Scan UI/modules
registry.initialize(str(ui_modules_dir))
print(f"Registry has {len(registry.modules)} modules after UI scan")

# Check for synergy and workflow
synergy = registry.get_module('synergy_sessions')
workflow = registry.get_module('workflow_automation')

print(f"\nSynergy found: {synergy is not None}")
print(f"Workflow found: {workflow is not None}")

if synergy:
    print(f"Synergy has thread_card_integration: {synergy.thread_card_integration is not None}")
    if synergy.thread_card_integration:
        print(f"  Badge enabled: {synergy.thread_card_integration.get('badge', {}).get('enabled')}")

if workflow:
    print(f"Workflow has thread_card_integration: {workflow.thread_card_integration is not None}")
    if workflow.thread_card_integration:
        print(f"  Badge enabled: {workflow.thread_card_integration.get('badge', {}).get('enabled')}")

# List all modules
print(f"\nAll modules ({len(registry.modules)}):")
for module_id in sorted(registry.modules.keys()):
    print(f"  - {module_id}")
