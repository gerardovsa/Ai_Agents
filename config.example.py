#!/usr/bin/env python3
"""
config.example.py
EXAMPLE configuration file - Copy to config.py and add your real API keys
DO NOT commit config.py with real keys to git!
"""

import os
import json

# ==============================================
# ENVIRONMENT VARIABLE LOADING
# ==============================================

def get_env_list(env_var_name: str, default: list = None) -> list:
    """Get a list from environment variable (JSON format)"""
    env_value = os.getenv(env_var_name)
    if env_value:
        try:
            return json.loads(env_value)
        except json.JSONDecodeError:
            # Fallback: try to parse as comma-separated values
            return [key.strip().strip('"\'') for key in env_value.split(',')]
    return default or []

# ==============================================
# API KEYS FROM ENVIRONMENT
# ==============================================

# DeepSeek API Keys - Add your keys here or set DEEPSEEK_KEYS environment variable
DEEPSEEK_API_KEYS = get_env_list('DEEPSEEK_KEYS', [
    'sk-your-deepseek-key-1-here',
    'sk-your-deepseek-key-2-here',
])

# Anthropic API Keys - Add your keys here or set ANTHROPIC_KEYS environment variable
ANTHROPIC_API_KEYS = get_env_list('ANTHROPIC_KEYS', [
    'sk-ant-your-anthropic-key-here'
])

# Single Anthropic API key (for backwards compatibility)
single_anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
if single_anthropic_key and single_anthropic_key not in ANTHROPIC_API_KEYS:
    ANTHROPIC_API_KEYS.insert(0, single_anthropic_key)

# OpenAI API Keys - Add your keys here or set OPENAI_KEYS environment variable
OPENAI_API_KEYS = get_env_list('OPENAI_KEYS', [
    'sk-proj-your-openai-key-here'
])

# Single OpenAI API key (for backwards compatibility)
single_openai_key = os.getenv('OPENAI_API_KEY', '')
if single_openai_key and single_openai_key not in OPENAI_API_KEYS:
    OPENAI_API_KEYS.insert(0, single_openai_key)

# ==============================================
# API KEY ROTATION HELPER
# ==============================================

def get_api_key_enhanced(provider: str = 'deepseek', key_index: int = None) -> str:
    """
    Get an API key for the specified provider with round-robin rotation
    
    Args:
        provider: 'deepseek', 'anthropic', or 'openai'
        key_index: Optional specific index to use
    
    Returns:
        str: API key for the provider
    """
    if provider == 'deepseek':
        keys = DEEPSEEK_API_KEYS
    elif provider == 'anthropic':
        keys = ANTHROPIC_API_KEYS
    elif provider == 'openai':
        keys = OPENAI_API_KEYS
    else:
        raise ValueError(f"Unknown provider: {provider}")
    
    if not keys:
        raise ValueError(f"No API keys configured for {provider}")
    
    if key_index is not None:
        return keys[key_index % len(keys)]
    
    # Simple round-robin rotation
    import time
    index = int(time.time()) % len(keys)
    return keys[index]

# ==============================================
# AI MODEL CONFIGURATION
# ==============================================

MODEL_CONFIGS = {
    'deepseek-chat': {
        'model_id': 'deepseek-chat',
        'provider': 'deepseek',
        'max_tokens': 8192,
        'max_input_tokens': 128000,
        'supports_web_search': False,
        'supports_extended_thinking': False,
        'supports_server_tools': False,
        'supports_function_calling': True,
        'available_tools': [],
        'thinking_budget': 0,
    },
    'claude-4-ultimate': {
        'model_id': 'claude-4-ultimate',
        'provider': 'anthropic',
        'max_tokens': 8192,
        'max_input_tokens': 200000,
        'supports_web_search': True,
        'supports_extended_thinking': True,
        'supports_server_tools': True,
        'supports_function_calling': True,
        'available_tools': ['web_search', 'computer', 'bash'],
        'thinking_budget': 10000,
    },
    'gpt-4': {
        'model_id': 'gpt-4',
        'provider': 'openai',
        'max_tokens': 8192,
        'max_input_tokens': 128000,
        'supports_web_search': False,
        'supports_extended_thinking': False,
        'supports_server_tools': False,
        'supports_function_calling': True,
        'available_tools': [],
        'thinking_budget': 0,
    }
}

# ==============================================
# EXTERNAL SERVICE API KEYS
# ==============================================

# Add your service API keys here or use environment variables
RENDER_API_KEY = os.getenv('RENDER_API_KEY', '')
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY', '')
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Microsoft 365 OAuth
MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID', '')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET', '')
MICROSOFT_TENANT_ID = os.getenv('MICROSOFT_TENANT_ID', 'common')

# Google OAuth (uses service account JSON file)
# Place your service-account.json file in the project root

print("✅ Config loaded (EXAMPLE FILE - add your real keys to config.py)")
