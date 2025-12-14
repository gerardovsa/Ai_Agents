import sys
sys.path.insert(0, '.')

from tools.registry_v3 import RegistryV3

missing = ['calculate_flyers', 'calculate_letterheads', 'calculate_perfect_bound_books', 'calculate_corflute_signs']

print('\n' + '='*60)
print('OLD-STYLE CALCULATOR REGISTRATION CHECK')
print('='*60)

registry = RegistryV3()

for name in missing:
    status = 'REGISTERED' if name in registry.tools else 'NOT FOUND'
    print(f'  {status:12} {name}')

print('\n' + '='*60)
print(f'Total tools in registry: {len(registry.tools)}')
print('='*60)
