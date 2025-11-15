"""
Slug Generator - Unique URL-safe identifiers

Generates unique, collision-resistant slugs for workspaces and threads.
"""

import re
import sqlite3
import sys
import secrets
from typing import Optional, Set
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection


class SlugGenerator:
    """
    Slug Generation Utilities
    
    Creates URL-safe slugs from names with collision detection.
    
    Methods:
        generate_workspace_slug() - Generate workspace slug
        generate_thread_slug() - Generate thread slug
        is_slug_available() - Check slug availability
        validate_slug() - Validate slug format
    """
    
    # Reserved slugs that cannot be used
    RESERVED_SLUGS = {
        'admin', 'api', 'auth', 'login', 'logout', 'signup', 'register',
        'settings', 'profile', 'account', 'billing', 'help', 'support',
        'dashboard', 'new', 'create', 'edit', 'delete', 'public', 'private',
        'system', 'root', 'user', 'users', 'workspace', 'workspaces',
        'thread', 'threads', 'message', 'messages', 'invite', 'invitations',
        'home', 'about', 'contact', 'terms', 'privacy', 'docs', 'documentation'
    }
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SlugGenerator
        
        Args:
            db_path: Path to ai_infrastructure.db
        """
        if db_path is None:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
        
        self.db_path = str(db_path)
    
    def _get_connection(self):
        """Get database connection (SQLite or Supabase)"""
        conn = get_database_connection('ai_infrastructure')
        if hasattr(conn, 'row_factory'):  # SQLite
            conn.row_factory = sqlite3.Row
        return conn
    
    def _slugify(self, text: str) -> str:
        """
        Convert text to URL-safe slug
        
        Args:
            text: Input text
        
        Returns:
            str: Slugified text
        
        Examples:
            "My Workspace" -> "my-workspace"
            "AI Agent 2024!" -> "ai-agent-2024"
            "Test___Spaces" -> "test-spaces"
        """
        # Convert to lowercase
        slug = text.lower()
        
        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        
        # Remove non-alphanumeric characters except hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug
    
    def validate_slug(self, slug: str) -> bool:
        """
        Validate slug format
        
        Args:
            slug: Slug to validate
        
        Returns:
            bool: True if valid
        
        Rules:
            - 3-63 characters
            - Only lowercase letters, numbers, hyphens
            - Cannot start or end with hyphen
            - Cannot be reserved word
        """
        if not slug or len(slug) < 3 or len(slug) > 63:
            return False
        
        if slug in self.RESERVED_SLUGS:
            return False
        
        if slug.startswith('-') or slug.endswith('-'):
            return False
        
        # Must match pattern: lowercase, numbers, hyphens only
        pattern = r'^[a-z0-9-]+$'
        return bool(re.match(pattern, slug))
    
    def is_workspace_slug_available(self, slug: str, exclude_workspace_id: Optional[int] = None) -> bool:
        """
        Check if workspace slug is available
        
        Args:
            slug: Slug to check
            exclude_workspace_id: Exclude this workspace from check (for updates)
        
        Returns:
            bool: True if available
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id FROM workspaces WHERE slug = ?"
        params = [slug]
        
        if exclude_workspace_id:
            query += " AND id != ?"
            params.append(exclude_workspace_id)
        
        cursor.execute(query, params)
        exists = cursor.fetchone() is not None
        conn.close()
        
        return not exists
    
    def is_thread_slug_available(
        self,
        slug: str,
        workspace_id: int,
        exclude_thread_id: Optional[int] = None
    ) -> bool:
        """
        Check if thread slug is available in workspace
        
        Args:
            slug: Slug to check
            workspace_id: Workspace ID (thread slugs are workspace-scoped)
            exclude_thread_id: Exclude this thread from check
        
        Returns:
            bool: True if available
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Note: Assumes threads table has slug column
        # This will be added in database migration
        query = "SELECT id FROM threads WHERE workspace_id = ? AND slug = ?"
        params = [workspace_id, slug]
        
        if exclude_thread_id:
            query += " AND id != ?"
            params.append(exclude_thread_id)
        
        try:
            cursor.execute(query, params)
            exists = cursor.fetchone() is not None
            conn.close()
            return not exists
        except sqlite3.OperationalError:
            # Slug column doesn't exist yet
            conn.close()
            return True
    
    def generate_workspace_slug(
        self,
        name: str,
        max_attempts: int = 10
    ) -> str:
        """
        Generate unique workspace slug
        
        Args:
            name: Workspace name
            max_attempts: Max collision resolution attempts
        
        Returns:
            str: Unique slug
        
        Raises:
            ValueError: If cannot generate unique slug
        """
        base_slug = self._slugify(name)
        
        if not base_slug:
            # Fallback if name is empty or non-alphanumeric
            base_slug = f"workspace-{secrets.token_hex(4)}"
        
        # Check if base slug is available
        if self.validate_slug(base_slug) and self.is_workspace_slug_available(base_slug):
            return base_slug
        
        # Try with numeric suffixes
        for i in range(1, max_attempts):
            candidate = f"{base_slug}-{i}"
            
            if self.validate_slug(candidate) and self.is_workspace_slug_available(candidate):
                return candidate
        
        # Last resort: Add random hex
        random_slug = f"{base_slug}-{secrets.token_hex(4)}"
        
        if self.validate_slug(random_slug) and self.is_workspace_slug_available(random_slug):
            return random_slug
        
        raise ValueError(f"Could not generate unique slug for name: {name}")
    
    def generate_thread_slug(
        self,
        title: str,
        workspace_id: int,
        max_attempts: int = 10
    ) -> str:
        """
        Generate unique thread slug within workspace
        
        Args:
            title: Thread title
            workspace_id: Workspace ID
            max_attempts: Max collision resolution attempts
        
        Returns:
            str: Unique slug within workspace
        
        Raises:
            ValueError: If cannot generate unique slug
        """
        base_slug = self._slugify(title)
        
        if not base_slug:
            # Fallback
            base_slug = f"thread-{secrets.token_hex(4)}"
        
        # Check if base slug is available
        if self.validate_slug(base_slug) and self.is_thread_slug_available(base_slug, workspace_id):
            return base_slug
        
        # Try with numeric suffixes
        for i in range(1, max_attempts):
            candidate = f"{base_slug}-{i}"
            
            if self.validate_slug(candidate) and self.is_thread_slug_available(candidate, workspace_id):
                return candidate
        
        # Last resort: Add random hex
        random_slug = f"{base_slug}-{secrets.token_hex(4)}"
        
        if self.validate_slug(random_slug) and self.is_thread_slug_available(random_slug, workspace_id):
            return random_slug
        
        raise ValueError(f"Could not generate unique slug for title: {title}")
    
    def ensure_unique_workspace_slug(
        self,
        preferred_slug: str,
        exclude_workspace_id: Optional[int] = None
    ) -> str:
        """
        Ensure slug is unique, modify if needed
        
        Args:
            preferred_slug: Desired slug
            exclude_workspace_id: Exclude this workspace ID
        
        Returns:
            str: Unique slug (may be modified)
        """
        # Validate format
        if not self.validate_slug(preferred_slug):
            preferred_slug = self._slugify(preferred_slug)
            
            if not self.validate_slug(preferred_slug):
                raise ValueError(f"Invalid slug format: {preferred_slug}")
        
        # Check if available
        if self.is_workspace_slug_available(preferred_slug, exclude_workspace_id):
            return preferred_slug
        
        # Add suffix to make unique
        for i in range(1, 100):
            candidate = f"{preferred_slug}-{i}"
            
            if self.is_workspace_slug_available(candidate, exclude_workspace_id):
                return candidate
        
        # Last resort
        return f"{preferred_slug}-{secrets.token_hex(4)}"
    
    def suggest_workspace_slugs(self, name: str, count: int = 5) -> list:
        """
        Generate multiple slug suggestions
        
        Args:
            name: Workspace name
            count: Number of suggestions
        
        Returns:
            list: Available slug suggestions
        """
        suggestions = []
        base_slug = self._slugify(name)
        
        # Original
        if self.validate_slug(base_slug) and self.is_workspace_slug_available(base_slug):
            suggestions.append(base_slug)
        
        # With numbers
        for i in range(1, 20):
            if len(suggestions) >= count:
                break
            
            candidate = f"{base_slug}-{i}"
            if self.validate_slug(candidate) and self.is_workspace_slug_available(candidate):
                suggestions.append(candidate)
        
        # With random suffixes
        while len(suggestions) < count:
            candidate = f"{base_slug}-{secrets.token_hex(2)}"
            if self.validate_slug(candidate) and self.is_workspace_slug_available(candidate):
                if candidate not in suggestions:  # Avoid duplicates
                    suggestions.append(candidate)
        
        return suggestions[:count]
    
    def get_workspace_by_slug(self, slug: str) -> Optional[int]:
        """
        Get workspace ID by slug
        
        Args:
            slug: Workspace slug
        
        Returns:
            Optional[int]: Workspace ID or None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM workspaces WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        conn.close()
        
        return row['id'] if row else None
    
    def get_thread_by_slug(self, slug: str, workspace_id: int) -> Optional[int]:
        """
        Get thread ID by slug in workspace
        
        Args:
            slug: Thread slug
            workspace_id: Workspace ID
        
        Returns:
            Optional[int]: Thread ID or None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id FROM threads WHERE workspace_id = ? AND slug = ?",
                (workspace_id, slug)
            )
            row = cursor.fetchone()
            conn.close()
            return row['id'] if row else None
        except sqlite3.OperationalError:
            # Slug column doesn't exist yet
            conn.close()
            return None
