"""Update new workflows to be active and enabled"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Update the 4 new workflows
cursor.execute("""
    UPDATE visual_automations
    SET status = 'active'
    WHERE automation_id LIKE %s
""", ('wf_%_1763946900',))

updated_count = cursor.rowcount
conn.commit()

print('\n' + '='*70)
print('✅ WORKFLOWS ACTIVATED')
print('='*70)
print(f'\nUpdated {updated_count} workflows from draft → active')
print('\nWorkflows now have status="active" which makes them visible')
print('when "Enabled" filter is selected in the UI.')
print('\n📍 Next steps:')
print('   1. Refresh browser (Ctrl+Shift+F5)')
print('   2. Click Load button')
print('   3. You should now see all 4 new workflows!')
print('\n' + '='*70 + '\n')

conn.close()
