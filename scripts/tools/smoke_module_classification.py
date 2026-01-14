"""
Small smoke-test to classify modules vs components by scanning manifest.json
Usage: python scripts/tools/smoke_module_classification.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIRS = [ROOT / 'UI' / 'modules_internal', ROOT / 'UI' / 'modules_external']

results = []
for base in MODULE_DIRS:
    if not base.exists():
        continue
    for manifest in base.rglob('manifest.json'):
        try:
            m = json.loads(manifest.read_text(encoding='utf-8'))
        except Exception as e:
            results.append((str(manifest), 'ERROR', str(e)))
            continue
        module_id = m.get('id') or manifest.parent.name
        name = m.get('name') or ''
        enabled = m.get('enabled', True)
        module_type = m.get('module_type') or ('component' if m.get('exports') and not m.get('main_tab') else 'module')
        floating = bool(m.get('floating_toggle') or m.get('floating') or m.get('floating_toggle_position'))
        sidebar = bool(m.get('sidebar') or m.get('capabilities', {}).get('sidebar'))
        main_tab = bool(m.get('main_tab'))
        results.append({
            'manifest': str(manifest.relative_to(ROOT)),
            'id': module_id,
            'name': name,
            'enabled': enabled,
            'module_type': module_type,
            'main_tab': main_tab,
            'floating_toggle': floating,
            'sidebar': sidebar,
        })

# Print summary
modules = [r for r in results if isinstance(r, dict) and r['module_type'] == 'module']
components = [r for r in results if isinstance(r, dict) and r['module_type'] == 'component']
errors = [r for r in results if not isinstance(r, dict)]

print('\nSMOKE MODULE CLASSIFICATION REPORT')
print('Root:', ROOT)
print('\nTotal manifests scanned:', len(results))
print('Modules:', len(modules))
print('Components:', len(components))
print('Errors:', len(errors))

print('\n-- Sample Modules (first 20) --')
for r in modules[:20]:
    print(f"{r['id']:30} | main_tab={r['main_tab']:5} | floating={r['floating_toggle']:5} | sidebar={r['sidebar']:5} | {r['manifest']}")

print('\n-- Sample Components (first 20) --')
for r in components[:20]:
    print(f"{r['id']:30} | main_tab={r['main_tab']:5} | floating={r['floating_toggle']:5} | sidebar={r['sidebar']:5} | {r['manifest']}")

if errors:
    print('\nErrors reading manifests:')
    for e in errors:
        print(e)

# Exit code style print for automation
print('\nREPORT_COMPLETE')
