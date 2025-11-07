#!/usr/bin/env python3
"""
Check Prerequisites for Render Deployment

Verifies all requirements are met before deploying to Render.com
"""

import os
import sys
from pathlib import Path
import subprocess

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = "" if exists else ("" if required else "⚠️ ")
    print(f"   {status} {filepath}")
    return exists

def check_git_repository():
    """Check if git is initialized"""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_git_remote():
    """Check if git remote is configured"""
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def check_env_file():
    """Check if .env.master exists and has API keys"""
    env_path = Path('.env.master')
    if not env_path.exists():
        return False, 0
    
    with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        required_keys = [
            'ANTHROPIC_API_KEY',
            'MICROSOFT_CLIENT_ID',
            'MICROSOFT_CLIENT_SECRET'
        ]
        found_keys = sum(1 for key in required_keys if key in content)
        return True, found_keys

def main():
    print("=" * 70)
    print("🔍 Render Deployment Prerequisites Check")
    print("=" * 70)
    
    all_good = True
    
    # Check required files
    print("\n📁 Required Files:")
    all_good &= check_file_exists('runtime.txt', required=True)
    all_good &= check_file_exists('requirements.txt', required=True)
    all_good &= check_file_exists('.gitignore', required=True)
    all_good &= check_file_exists('AI_infrastructure/flask_app.py', required=True)
    
    env_exists, key_count = check_env_file()
    if env_exists:
        print(f"    .env.master (found {key_count}/3 required keys)")
        if key_count < 3:
            print(f"      ⚠️  Missing some API keys")
            all_good = False
    else:
        print(f"    .env.master")
        all_good = False
    
    # Check git setup
    print("\n🔧 Git Configuration:")
    if check_git_repository():
        print("    Git repository initialized")
    else:
        print("    Git repository not initialized")
        print("      Run: git init")
        all_good = False
    
    if check_git_remote():
        print("    Git remote configured")
    else:
        print("   ⚠️  Git remote not configured")
        print("      You'll need to add: git remote add origin <github-url>")
    
    # Check Python version
    print("\n🐍 Python Environment:")
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"   ℹ️  Python version: {py_version}")
    
    # Check Render API key
    print("\n🔑 Render Credentials:")
    render_key = os.getenv('RENDER_API_KEY')
    if not render_key:
        # Try to load from .env.master
        from dotenv import load_dotenv
        load_dotenv('.env.master')
        render_key = os.getenv('RENDER_API_KEY')
    
    if render_key and render_key.startswith('rnd_'):
        print(f"    RENDER_API_KEY found")
    else:
        print(f"   ⚠️  RENDER_API_KEY not found or invalid")
        print(f"      Get it from: https://dashboard.render.com/u/settings")
    
    # Summary
    print("\n" + "=" * 70)
    if all_good:
        print(" All prerequisites met! Ready to deploy.")
        print("\nNext step: python Render_backend/deploy_to_render.py")
    else:
        print(" Some prerequisites missing. Fix issues above before deploying.")
    print("=" * 70)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
