"""
AI Infrastructure - Core Modules
Unified session management and Anthropic client for all AI UIs
"""

# Relative imports (works from anywhere)
from .unified_session_manager import UnifiedSessionManager, session_manager
from .unified_anthropic_client import UnifiedAnthropicClient, anthropic_client

__all__ = [
    'UnifiedSessionManager',
    'session_manager',
    'UnifiedAnthropicClient',
    'anthropic_client'
]
