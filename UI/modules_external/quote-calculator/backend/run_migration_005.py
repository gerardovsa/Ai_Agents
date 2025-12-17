"""
Run Migration 005: Custom Calculator Tables
"""
import os
import sys
from pathlib import Path

# Add parent directories to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Add AI_infrastructure to path for database_utils
ai_infra_dir = Path(backend_dir).parent.parent.parent.parent / 'AI_infrastructure'
sys.path.insert(0, str(ai_infra_dir))

from shared.database_utils import get_database_connection
from dotenv import load_dotenv

# Load environment variables
root_dir = Path(backend_dir).parent.parent.parent.parent
env_file = root_dir / '.env.master'
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

def run_migration_005():
    """Execute migration 005"""
    print('='*80)
    print('MIGRATION 005: CUSTOM CALCULATOR TABLES')
    print('='*80)
    
    # Load migration SQL
    migration_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'database',
        'migrations',
        '005_custom_calculators_tables.sql'
    )
    
    print(f'\n[+] Loading migration from: {migration_file}')
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print(f'[+] Migration SQL loaded ({len(migration_sql)} characters)')
    
    # Execute migration using database_utils connection
    print('\n[+] Connecting to Supabase (ai-agents-production-inhouse)...')
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    print('[+] Executing migration...')
    
    try:
        # Execute the migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print('\n[SUCCESS] MIGRATION 005 COMPLETE!')
        print('\nTables created:')
        print('  * custom_calculators')
        print('  * custom_calculator_parameters')
        print('  * custom_calculator_components')
        print('  * pricing_scenario_models')
        print('  * quote_history_archive')
        print('  * pricing_impact_projections')
        print('\nExtended tables:')
        print('  * calculator_parameter_overrides (added custom_calculator_id column)')
        print('\nHelper functions:')
        print('  * get_parameter_with_override()')
        print('  * update_calculator_usage_stats()')
        print('\nNew parameters:')
        print('  * profit_margin_standard, profit_margin_premium, profit_margin_bulk')
        print('  * complexity_multiplier_standard, complexity_multiplier_challenging, complexity_multiplier_rush')
        print('  * labor_rate_specialist, labor_multiplier_after_hours, labor_multiplier_public_holiday')
        
        return True
        
    except Exception as e:
        print(f'\n[ERROR] Migration failed: {e}')
        conn.rollback()
        raise
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    try:
        run_migration_005()
    except Exception as e:
        print(f'\n❌ Migration failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
