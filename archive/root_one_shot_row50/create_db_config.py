#!/usr/bin/env python3
"""Create database config for quote calculator GOD calculators"""
import sys
import json
from pathlib import Path

# Add credentials path
sys.path.insert(0, 'AI_infrastructure/auth')
from supabase_credentials import get_database_config

# Get config
config = get_database_config()

# Create config directory
config_dir = Path('UI/modules_external/quote-calculator/config')
config_dir.mkdir(exist_ok=True)

# Write config
config_file = config_dir / 'database-config.json'
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Database config created: {config_file}")
print(f"   Type: {config.get('type')}")
print(f"   Host: {config.get('host', 'N/A')[:50]}...")
