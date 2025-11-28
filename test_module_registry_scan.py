"""Test module registry scanning both directories"""

from pathlib import Path
from AI_infrastructure.core.module_registry import get_module_registry

# Get registry
registry = get_module_registry()

# Clear any existing modules (fresh start)
registry.modules.clear()
registry.module_paths.clear()
registry._modules_loaded = False

print("\n" + "="*70)
print("TESTING MODULE REGISTRY - SCANNING BOTH DIRECTORIES")
print("="*70)

base_dir = Path(__file__).parent

# Scan frontend/modules
frontend_dir = base_dir / 'frontend' / 'modules'
print(f"\n[1] Scanning: {frontend_dir}")
print(f"    Exists: {frontend_dir.exists()}")
registry.initialize(str(frontend_dir))
print(f"    Modules after scan: {len(registry.modules)}")
if registry.modules:
    for mid in registry.modules.keys():
        print(f"      - {mid}")

# Scan UI/external/modules
external_dir = base_dir / 'UI' / 'external' / 'modules'
print(f"\n[2] Scanning: {external_dir}")
print(f"    Exists: {external_dir.exists()}")
registry.initialize(str(external_dir))
print(f"    Modules after scan: {len(registry.modules)}")

print(f"\n[3] FINAL RESULTS:")
print(f"    Total modules: {len(registry.modules)}")
print(f"\n    All module IDs:")
for mid in sorted(registry.modules.keys()):
    module = registry.modules[mid]
    print(f"      - {mid:30s} ({module.name})")

print(f"\n[4] COMMUNICATION HUB CHECK:")
comm_hub = registry.modules.get('communication-hub')
if comm_hub:
    print(f"    ✅ FOUND!")
    print(f"       Name: {comm_hub.name}")
    print(f"       Show in sidebar: {comm_hub.show_in_sidebar}")
    print(f"       Main tab: {comm_hub.main_tab}")
    print(f"       Icon: {comm_hub.icon}")
    print(f"       Path: {comm_hub.module_path}")
else:
    print(f"    ❌ NOT FOUND")

print("\n" + "="*70 + "\n")
