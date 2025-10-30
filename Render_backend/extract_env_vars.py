#!/usr/bin/env python3
"""
Extract Environment Variables - Convert .env.master to Render format

This script reads .env.master and exports environment variables to a JSON file
compatible with Render's API format.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import dotenv_values

def load_env_master():
    """Load environment variables from .env.master"""
    env_path = Path('.env.master')
    
    if not env_path.exists():
        print("❌ .env.master file not found")
        print("\n💡 Create .env.master with your API keys:")
        print("   ANTHROPIC_API_KEY=sk-ant-...")
        print("   OPENAI_API_KEY=sk-...")
        print("   DEEPSEEK_API_KEY_1=sk-...")
        print("   MICROSOFT_CLIENT_ID=...")
        print("   MICROSOFT_CLIENT_SECRET=...")
        return None
    
    try:
        # Load with UTF-8 encoding and ignore errors
        env_vars = dotenv_values(env_path, encoding='utf-8', errors='ignore')
        return env_vars
    except Exception as e:
        print(f"❌ Error reading .env.master: {e}")
        return None

def validate_required_keys(env_vars):
    """Check if required API keys are present"""
    required_keys = [
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY',
        'DEEPSEEK_API_KEY_1',
    ]
    
    missing = []
    for key in required_keys:
        if key not in env_vars or not env_vars[key]:
            missing.append(key)
    
    if missing:
        print(f"⚠️  Missing required keys: {', '.join(missing)}")
        return False
    
    return True

def convert_to_render_format(env_vars):
    """Convert env vars to Render API format"""
    render_vars = []
    
    for key, value in env_vars.items():
        if value and value.strip():  # Skip empty values
            render_vars.append({
                "key": key,
                "value": str(value).strip()
            })
    
    return render_vars

def save_to_json(render_vars, output_file='render_env_vars.json'):
    """Save environment variables to JSON file"""
    output_path = Path(output_file)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(render_vars, f, indent=2)
        
        print(f"✅ Saved {len(render_vars)} environment variables to {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")
        return False

def preview_vars(render_vars):
    """Show preview of environment variables (masked)"""
    print("\n📋 Environment Variables Preview:")
    print("=" * 70)
    
    for var in render_vars:
        key = var['key']
        value = var['value']
        
        # Mask sensitive values
        if any(secret in key.upper() for secret in ['KEY', 'SECRET', 'TOKEN', 'PASSWORD']):
            if len(value) > 10:
                masked = f"{value[:4]}...{value[-4:]}"
            else:
                masked = "***"
        else:
            masked = value
        
        print(f"   {key}: {masked}")
    
    print("=" * 70)

def main():
    print("=" * 70)
    print("📦 Extract Environment Variables")
    print("=" * 70)
    
    # Step 1: Load .env.master
    print("\n1️⃣  Loading .env.master...")
    env_vars = load_env_master()
    if not env_vars:
        return 1
    
    print(f"   ✅ Loaded {len(env_vars)} environment variables")
    
    # Step 2: Validate required keys
    print("\n2️⃣  Validating required API keys...")
    if not validate_required_keys(env_vars):
        print("   ⚠️  Some required keys are missing (deployment may fail)")
    else:
        print("   ✅ All required keys present")
    
    # Step 3: Convert to Render format
    print("\n3️⃣  Converting to Render format...")
    render_vars = convert_to_render_format(env_vars)
    
    # Add PORT if not present
    if not any(var['key'] == 'PORT' for var in render_vars):
        render_vars.append({"key": "PORT", "value": "10000"})
        print("   ✅ Added PORT=10000 (Render default)")
    
    # Step 4: Preview
    preview_vars(render_vars)
    
    # Step 5: Save to JSON
    print("\n4️⃣  Saving to render_env_vars.json...")
    if not save_to_json(render_vars):
        return 1
    
    # Step 6: Next steps
    print("\n" + "=" * 70)
    print("✅ Environment variables exported successfully!")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print("\n1. Review the generated render_env_vars.json")
    print("2. Deploy to Render:")
    print("   python Render_backend/deploy_to_render.py")
    print("\n3. Or manually update on Render dashboard:")
    print("   https://dashboard.render.com/web/YOUR_SERVICE_ID")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
