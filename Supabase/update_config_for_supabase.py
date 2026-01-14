#!/usr/bin/env python3
"""
Update AI_infrastructure/config.py to Support Supabase

This script updates the config.py file to add Supabase PostgreSQL support
while maintaining backward compatibility with SQLite for local development.

Usage:
    python update_config_for_supabase.py
"""

import os
from pathlib import Path

# Path to config.py
config_path = Path(__file__).parent.parent / 'AI_infrastructure' / 'config.py'

# New configuration code to insert
supabase_config = '''
# Database Configuration
import os
from pathlib import Path

# Determine environment and database type
IS_PRODUCTION = os.getenv('RENDER') == 'true'
USE_SUPABASE = os.getenv('USE_SUPABASE') == 'true'

if USE_SUPABASE:
    # Supabase PostgreSQL configuration (Production)
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    DATABASE_URL = os.getenv('SUPABASE_DB_URL')
    
    # Database type flag
    DATABASE_TYPE = 'postgresql'
    
    print("🗄️  Using Supabase PostgreSQL database")
    print(f"   URL: {SUPABASE_URL}")
    
else:
    # SQLite configuration (Development)
    ROOT_DIR = Path(__file__).parent.parent
    DATA_DIR = ROOT_DIR / 'data' if not IS_PRODUCTION else Path('/data')
    
    # Database paths
    DB_CONFIG_PATH = DATA_DIR / 'database-config.json'
    SESSION_DB_PATH = DATA_DIR / 'sessions.db'
    AI_INFRASTRUCTURE_DB_PATH = DATA_DIR / 'ai_infrastructure.db'
    SYNERGY_SESSIONS_DB_PATH = DATA_DIR / 'synergy_sessions.db'
    KANBAN_ANALYTICS_DB_PATH = DATA_DIR / 'kanban_analytics.db'
    STOCK_DATA_DB_PATH = DATA_DIR / 'stock_data.db'
    
    # Database type flag
    DATABASE_TYPE = 'sqlite'
    DATABASE_URL = f'sqlite:///{AI_INFRASTRUCTURE_DB_PATH}'
    
    print("🗄️  Using SQLite databases (development)")
    print(f"   Data dir: {DATA_DIR}")
'''

# Backup message
backup_msg = """
================================================================================
CONFIG.PY UPDATE UTILITY
================================================================================

This script will update AI_infrastructure/config.py to support Supabase.

Changes:
  ✓ Add Supabase PostgreSQL configuration
  ✓ Add USE_SUPABASE environment variable check
  ✓ Maintain SQLite support for local development
  ✓ Add DATABASE_TYPE flag for conditional logic

BACKUP: Your current config.py will be backed up to config.py.backup

"""

print(backup_msg)
response = input("Proceed with update? (yes/no): ").strip().lower()

if response != 'yes':
    print("\nUpdate cancelled.")
    exit(0)

print("\nUpdating config.py...")

try:
    # Read current config
    with open(config_path, 'r', encoding='utf-8') as f:
        current_config = f.read()
    
    # Create backup
    backup_path = config_path.with_suffix('.py.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(current_config)
    
    print(f"✓ Backup created: {backup_path}")
    
    # Check if already updated
    if 'USE_SUPABASE' in current_config:
        print("\n⚠️  Config already appears to have Supabase support")
        print("   Skipping update to avoid duplication")
        exit(0)
    
    # Find where to insert new config (after imports, before Config class)
    lines = current_config.split('\n')
    insert_index = 0
    
    # Find last import or first class definition
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            insert_index = i + 1
        elif line.strip().startswith('class '):
            break
    
    # Insert new configuration
    lines.insert(insert_index, '\n' + supabase_config + '\n')
    
    # Write updated config
    updated_config = '\n'.join(lines)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(updated_config)
    
    print("✓ Config.py updated successfully")
    
    print("\n" + "="*80)
    print("UPDATE COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Run migration script: python migrate_to_supabase.py")
    print("2. Add env vars to Render: cd ../Render_backend && python add_supabase_env_vars.py")
    print("3. Test locally with USE_SUPABASE=true")
    print("4. Deploy to Render")
    print("\n" + "="*80 + "\n")

except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nYou can manually add the configuration to config.py")
    print("See SUPABASE_SETUP_GUIDE.md for details")
    exit(1)
