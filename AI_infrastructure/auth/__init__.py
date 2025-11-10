"""
Authentication Package
=====================

User authentication, profiles, and workspace management
"""

from .user_auth import UserAuthManager, user_auth_manager, require_auth

__all__ = ['UserAuthManager', 'user_auth_manager', 'require_auth']
