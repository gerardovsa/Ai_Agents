"""
Supabase integration module for VSA Automation Agent
Provides database connectivity and configuration management
"""

from .supabase_client import SupabaseClient

# Compatibility alias for uppercase import
class SupabaseConfig:
    """Configuration class for Supabase connections"""
    
    @staticmethod
    def get_client():
        """Get configured Supabase client"""
        return SupabaseClient()
    
    # Import credentials from environment
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://wuwmvtslltqhaycyukxk.supabase.co')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

__all__ = ['SupabaseClient', 'SupabaseConfig']
