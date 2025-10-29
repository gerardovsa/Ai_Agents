"""
AI Infrastructure Package
Clean, unified architecture for all AI chat interfaces
"""

# Make core modules available at package level
from .core import (
    UnifiedSessionManager,
    session_manager,
    UnifiedAnthropicClient,
    anthropic_client
)

__all__ = [
    'UnifiedSessionManager',
    'session_manager',
    'UnifiedAnthropicClient',
    'anthropic_client'
]

__version__ = '1.0.0'
