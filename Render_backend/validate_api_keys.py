#!/usr/bin/env python3
"""
Validate API Keys - Test API keys before deployment

This script validates that API keys are working by making test requests
to each service. Helps catch invalid keys before deploying.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import dotenv_values

def test_anthropic_key(api_key):
    """Test Anthropic API key"""
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        
        # Simple test: list models (doesn't use credits)
        # If key is invalid, this will raise an error
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
        
        return True, "Valid"
    except ImportError:
        return False, "anthropic package not installed (pip install anthropic)"
    except Exception as e:
        return False, str(e)

def test_openai_key(api_key):
    """Test OpenAI API key"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Simple test: list models
        models = client.models.list()
        
        return True, "Valid"
    except ImportError:
        return False, "openai package not installed (pip install openai)"
    except Exception as e:
        return False, str(e)

def test_deepseek_key(api_key):
    """Test DeepSeek API key"""
    try:
        from openai import OpenAI
        
        # DeepSeek uses OpenAI-compatible API
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Test with minimal request
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        return True, "Valid"
    except ImportError:
        return False, "openai package not installed (pip install openai)"
    except Exception as e:
        return False, str(e)

def test_microsoft_credentials(client_id, client_secret):
    """Test Microsoft OAuth credentials"""
    try:
        import msal
        
        app = msal.ConfidentialClientApplication(
            client_id,
            authority="https://login.microsoftonline.com/common",
            client_credential=client_secret
        )
        
        # Try to get token for Graph API
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        
        if "access_token" in result:
            return True, "Valid"
        else:
            return False, result.get("error_description", "Unknown error")
    except ImportError:
        return False, "msal package not installed (pip install msal)"
    except Exception as e:
        return False, str(e)

def load_env_master():
    """Load environment variables from .env.master"""
    env_path = Path('.env.master')
    
    if not env_path.exists():
        print(" .env.master file not found")
        return None
    
    try:
        env_vars = dotenv_values(env_path, encoding='utf-8', errors='ignore')
        return env_vars
    except Exception as e:
        print(f" Error reading .env.master: {e}")
        return None

def main():
    print("=" * 70)
    print("🔐 Validate API Keys")
    print("=" * 70)
    
    # Load environment variables
    print("\n📥 Loading .env.master...")
    env_vars = load_env_master()
    if not env_vars:
        return 1
    
    print(f"    Loaded {len(env_vars)} environment variables")
    
    # Test results
    results = []
    
    # Test Anthropic
    print("\n1️⃣  Testing Anthropic API key...")
    anthropic_key = env_vars.get('ANTHROPIC_API_KEY')
    if anthropic_key:
        valid, message = test_anthropic_key(anthropic_key)
        status = "" if valid else ""
        print(f"   {status} Anthropic: {message}")
        results.append({"service": "Anthropic", "valid": valid, "message": message})
    else:
        print("   ⚠️  ANTHROPIC_API_KEY not found")
        results.append({"service": "Anthropic", "valid": False, "message": "Key not found"})
    
    # Test OpenAI
    print("\n2️⃣  Testing OpenAI API key...")
    openai_key = env_vars.get('OPENAI_API_KEY')
    if openai_key:
        valid, message = test_openai_key(openai_key)
        status = "" if valid else ""
        print(f"   {status} OpenAI: {message}")
        results.append({"service": "OpenAI", "valid": valid, "message": message})
    else:
        print("   ⚠️  OPENAI_API_KEY not found")
        results.append({"service": "OpenAI", "valid": False, "message": "Key not found"})
    
    # Test DeepSeek
    print("\n3️⃣  Testing DeepSeek API key...")
    deepseek_key = env_vars.get('DEEPSEEK_API_KEY_1')
    if deepseek_key:
        valid, message = test_deepseek_key(deepseek_key)
        status = "" if valid else ""
        print(f"   {status} DeepSeek: {message}")
        results.append({"service": "DeepSeek", "valid": valid, "message": message})
    else:
        print("   ⚠️  DEEPSEEK_API_KEY_1 not found")
        results.append({"service": "DeepSeek", "valid": False, "message": "Key not found"})
    
    # Test Microsoft
    print("\n4️⃣  Testing Microsoft OAuth credentials...")
    client_id = env_vars.get('MICROSOFT_CLIENT_ID')
    client_secret = env_vars.get('MICROSOFT_CLIENT_SECRET')
    if client_id and client_secret:
        valid, message = test_microsoft_credentials(client_id, client_secret)
        status = "" if valid else ""
        print(f"   {status} Microsoft: {message}")
        results.append({"service": "Microsoft", "valid": valid, "message": message})
    else:
        print("   ⚠️  MICROSOFT_CLIENT_ID or MICROSOFT_CLIENT_SECRET not found")
        results.append({"service": "Microsoft", "valid": False, "message": "Credentials not found"})
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Validation Summary")
    print("=" * 70)
    
    valid_count = sum(1 for r in results if r['valid'])
    total_count = len(results)
    
    for result in results:
        status = "" if result['valid'] else ""
        print(f"   {status} {result['service']}: {result['message']}")
    
    print(f"\n   {valid_count}/{total_count} services validated successfully")
    
    if valid_count == total_count:
        print("\n All API keys are valid! Ready to deploy.")
        return 0
    else:
        print("\n⚠️  Some API keys are invalid. Fix them before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
