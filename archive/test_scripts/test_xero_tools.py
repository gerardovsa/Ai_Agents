"""Quick test to verify all 5 Xero tools are now available"""
from tools.registry_v3 import RegistryV3

r = RegistryV3()

tools_to_test = [
    'xero_get_invoices',
    'xero_get_accounts', 
    'xero_get_bank_transactions',
    'xero_get_payments',
    'xero_get_contacts'
]

print('\n' + '='*60)
print('Testing 5 Read-Only Xero Tools')
print('='*60 + '\n')

all_passed = True
for i, tool_name in enumerate(tools_to_test, 1):
    func = r.get_tool_function(tool_name)
    status = 'FOUND' if func else 'NOT FOUND'
    icon = '✅' if func else '❌'
    print(f'{i}. {tool_name}: {icon} {status}')
    if not func:
        all_passed = False

print('\n' + '='*60)
if all_passed:
    print('✅ SUCCESS! All 5 Xero tools are now available!')
else:
    print('❌ FAILED - Some tools are missing')
print('='*60 + '\n')
