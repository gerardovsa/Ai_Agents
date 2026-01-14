"""
FILE: AI_infrastructure/auth/permission_checker.py
PURPOSE: Permission checker middleware for role-based access control

DEPENDENCIES:
- sqlite3 (built-in) - Database access
- json (built-in) - JSON parsing for permissions
- datetime (built-in) - Time-based restrictions

EXPORTS:
- PermissionChecker class:
  * check_tool_permission(user_id, tool_name) -> bool
  * check_agent_access(user_id, agent_id) -> bool
  * check_data_access(user_id, resource_owner_id) -> bool
  * check_workspace_access(user_id, workspace_id, required_role) -> bool
  * is_within_work_hours(user_id) -> bool
  * check_usage_limit(user_id) -> bool
- get_permission_checker() -> PermissionChecker (singleton)

USED BY:
- tools/registry_v3.py (tool execution protection)
- AI_infrastructure/core/agent_worker.py (AI agent access)
- AI_infrastructure/routes/*.py (data access protection)

RELATED FILES:
- data/ai_infrastructure.db (users table with permission columns)
- AI_infrastructure/auth/user_auth.py (user authentication)

NOTES:
- Implements 6-role hierarchy: owner/admin/team_lead/team/readonly/guest
- Tool permissions: NULL = all allowed, empty list = none, list = whitelist
- Agent permissions: NULL = all allowed, empty list = none, list = whitelist
- Data scope: 'own' | 'team' | 'department' | 'all'
- Work hours: HH:MM format (e.g., '09:00' to '17:00')
- Usage limits: Daily API call counter (TODO: implement tracking)

LAST MODIFIED: 2025-11-17 - Removed SQLite remnants for Supabase migration
"""

import json
from shared.db_connection_wrapper import get_connection
from datetime import datetime, time
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class PermissionError(Exception):
    """Custom exception for permission denials"""
    pass


class PermissionChecker:
    """
    Permission checker for role-based access control
    
    Checks permissions for:
    - Tool usage (594 tools across 20+ platforms)
    - AI agent access (5 agents: prime, agent-1 through agent-4)
    - Data access (own/team/department/all scopes)
    - Workspace access (multi-tenant isolation)
    - Time restrictions (work hours)
    - Usage limits (daily rate limiting)
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize permission checker
        
        Args:
            db_path: Path to ai_infrastructure.db (auto-detected if None)
        """
        if db_path is None:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
        
        self.db_path = str(db_path)
        
        # Role hierarchy (higher = more permissions)
        self.role_hierarchy = {
            'owner': 6,
            'admin': 5,
            'team_lead': 4,
            'team': 3,
            'readonly': 2,
            'guest': 1,
            'user': 3  # Default role, same as 'team'
        }
    
    def get_user_permissions(self, user_id: int) -> Optional[Dict]:
        """
        Get complete permission set for user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with all permission fields, or None if user not found
        """
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    role, permissions, allowed_tools, allowed_agents, 
                    data_access_scope, parent_user_id, is_sub_user,
                    usage_limit_daily, access_start_time, access_end_time,
                    account_expires_at
                FROM ai_infrastructure.users 
                WHERE id = %s
            """, [user_id])
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Parse JSON fields
            permissions = json.loads(row['permissions']) if row['permissions'] else {}
            allowed_tools = json.loads(row['allowed_tools']) if row['allowed_tools'] else None
            allowed_agents = json.loads(row['allowed_agents']) if row['allowed_agents'] else None
            
            return {
                'role': row['role'] or 'user',
                'permissions': permissions,
                'allowed_tools': allowed_tools,
                'allowed_agents': allowed_agents,
                'data_access_scope': row['data_access_scope'] or 'own',
                'parent_user_id': row['parent_user_id'],
                'is_sub_user': bool(row['is_sub_user']),
                'usage_limit_daily': row['usage_limit_daily'] or 1000,
                'access_start_time': row['access_start_time'],
                'access_end_time': row['access_end_time'],
                'account_expires_at': row['account_expires_at']
            }
        finally:
            conn.close()
    
    def get_role_level(self, role: str) -> int:
        """
        Get numeric level for role (higher = more permissions)
        
        Args:
            role: Role name
        
        Returns:
            Numeric level (1-6)
        """
        return self.role_hierarchy.get(role, 0)
    
    def has_role_level(self, user_id: int, required_level: int) -> bool:
        """
        Check if user has at least the required role level
        
        Args:
            user_id: User ID
            required_level: Minimum role level needed
        
        Returns:
            True if user meets requirement
        """
        perms = self.get_user_permissions(user_id)
        if not perms:
            return False
        
        user_level = self.get_role_level(perms['role'])
        return user_level >= required_level
    
    def check_tool_permission(self, user_id: int, tool_name: str) -> bool:
        """
        Check if user has permission to use a tool
        
        Logic:
        1. owner/admin roles = full access to all tools
        2. allowed_tools = None → all tools allowed (default)
        3. allowed_tools = [] → no tools allowed
        4. allowed_tools = ['tool1', 'tool2'] → only listed tools
        
        Args:
            user_id: User ID
            tool_name: Tool name (e.g., 'gmail_send_email')
        
        Returns:
            True if allowed, False if denied
        
        Raises:
            PermissionError: If permission denied with reason
        """
        perms = self.get_user_permissions(user_id)
        
        if not perms:
            raise PermissionError(f"User {user_id} not found")
        
        # Owner and admin have full access
        if perms['role'] in ['owner', 'admin']:
            return True
        
        allowed_tools = perms.get('allowed_tools')
        
        # None = all tools allowed (default for regular users)
        if allowed_tools is None:
            return True
        
        # Empty list = no tools allowed
        if isinstance(allowed_tools, list) and len(allowed_tools) == 0:
            raise PermissionError(
                f"User {user_id} (role: {perms['role']}) has no tool access"
            )
        
        # Check whitelist
        if tool_name not in allowed_tools:
            raise PermissionError(
                f"Tool '{tool_name}' not in allowed list for user {user_id} "
                f"(role: {perms['role']})"
            )
        
        return True
    
    def check_agent_access(self, user_id: int, agent_id: str) -> bool:
        """
        Check if user can access an AI agent
        
        Logic:
        1. owner/admin roles = full access to all agents
        2. allowed_agents = None → all agents allowed (default)
        3. allowed_agents = [] → no agents allowed
        4. allowed_agents = ['prime', 'agent-1'] → only listed agents
        
        Args:
            user_id: User ID
            agent_id: Agent ID ('prime', 'agent-1', 'agent-2', etc.)
        
        Returns:
            True if allowed, False if denied
        
        Raises:
            PermissionError: If permission denied with reason
        """
        perms = self.get_user_permissions(user_id)
        
        if not perms:
            raise PermissionError(f"User {user_id} not found")
        
        # Owner and admin have full access
        if perms['role'] in ['owner', 'admin']:
            return True
        
        allowed_agents = perms.get('allowed_agents')
        
        # None = all agents allowed (default)
        if allowed_agents is None:
            return True
        
        # Empty list = no agents allowed
        if isinstance(allowed_agents, list) and len(allowed_agents) == 0:
            raise PermissionError(
                f"User {user_id} (role: {perms['role']}) has no agent access"
            )
        
        # Check whitelist
        if agent_id not in allowed_agents:
            raise PermissionError(
                f"Agent '{agent_id}' not in allowed list for user {user_id} "
                f"(role: {perms['role']})"
            )
        
        return True
    
    def check_data_access(self, user_id: int, resource_owner_id: int) -> bool:
        """
        Check if user can access another user's data
        
        Logic:
        1. owner/admin roles = access all data
        2. Can always access own data
        3. data_access_scope determines access to others' data:
           - 'own': only own data
           - 'team': own + team members' data (TODO: implement team concept)
           - 'department': own + department data (TODO: implement)
           - 'all': all users' data
        
        Args:
            user_id: Requesting user ID
            resource_owner_id: Owner of the resource
        
        Returns:
            True if allowed, False if denied
        
        Raises:
            PermissionError: If permission denied with reason
        """
        perms = self.get_user_permissions(user_id)
        
        if not perms:
            raise PermissionError(f"User {user_id} not found")
        
        # Owner and admin can access all data
        if perms['role'] in ['owner', 'admin']:
            return True
        
        # Can always access own data
        if user_id == resource_owner_id:
            return True
        
        # Check data access scope
        data_scope = perms.get('data_access_scope', 'own')
        
        if data_scope == 'own':
            raise PermissionError(
                f"User {user_id} (role: {perms['role']}) can only access own data"
            )
        
        if data_scope == 'all':
            return True
        
        # TODO: Implement 'team' and 'department' scope checks
        # For now, deny access
        raise PermissionError(
            f"User {user_id} (role: {perms['role']}, scope: {data_scope}) "
            f"cannot access data owned by user {resource_owner_id}"
        )
    
    def is_within_work_hours(self, user_id: int) -> bool:
        """
        Check if current time is within user's allowed work hours
        
        Args:
            user_id: User ID
        
        Returns:
            True if within work hours (or no restriction), False otherwise
        
        Raises:
            PermissionError: If outside work hours
        """
        perms = self.get_user_permissions(user_id)
        
        if not perms:
            raise PermissionError(f"User {user_id} not found")
        
        # No restrictions = always allowed
        start_time_str = perms.get('access_start_time')
        end_time_str = perms.get('access_end_time')
        
        if not start_time_str or not end_time_str:
            return True
        
        # Parse work hours
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            current_time = datetime.now().time()
            
            # Check if within range
            if not (start_time <= current_time <= end_time):
                raise PermissionError(
                    f"Access denied: outside work hours "
                    f"({start_time_str} - {end_time_str})"
                )
            
            return True
            
        except ValueError as e:
            # Invalid time format, allow access
            return True
    
    def check_usage_limit(self, user_id: int) -> bool:
        """
        Check if user has exceeded daily usage limit
        
        TODO: Implement usage tracking table:
        CREATE TABLE usage_logs (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            tool_name TEXT,
            timestamp TIMESTAMP,
            success BOOLEAN
        )
        
        Args:
            user_id: User ID
        
        Returns:
            True if within limit, False if exceeded
        
        Raises:
            PermissionError: If limit exceeded
        """
        # TODO: Query usage_logs table and count today's calls
        # For now, always allow (no tracking implemented yet)
        return True
    
    def check_account_expiry(self, user_id: int) -> bool:
        """
        Check if user account has expired
        
        Args:
            user_id: User ID
        
        Returns:
            True if account is active
        
        Raises:
            PermissionError: If account expired
        """
        perms = self.get_user_permissions(user_id)
        
        if not perms:
            raise PermissionError(f"User {user_id} not found")
        
        expiry = perms.get('account_expires_at')
        
        if not expiry:
            return True  # No expiry set
        
        try:
            expiry_date = datetime.fromisoformat(expiry)
            if datetime.now() > expiry_date:
                raise PermissionError(
                    f"Account expired on {expiry_date.strftime('%Y-%m-%d')}"
                )
            return True
        except ValueError:
            # Invalid date format, allow access
            return True
    
    def check_all_restrictions(self, user_id: int, 
                             tool_name: str = None,
                             agent_id: str = None,
                             resource_owner_id: int = None) -> bool:
        """
        Check all applicable restrictions for a user action
        
        Args:
            user_id: User ID
            tool_name: Tool being accessed (optional)
            agent_id: Agent being accessed (optional)
            resource_owner_id: Data owner being accessed (optional)
        
        Returns:
            True if all checks pass
        
        Raises:
            PermissionError: If any check fails
        """
        # Check account expiry
        self.check_account_expiry(user_id)
        
        # Check work hours
        self.is_within_work_hours(user_id)
        
        # Check usage limit
        self.check_usage_limit(user_id)
        
        # Check tool permission
        if tool_name:
            self.check_tool_permission(user_id, tool_name)
        
        # Check agent access
        if agent_id:
            self.check_agent_access(user_id, agent_id)
        
        # Check data access
        if resource_owner_id and resource_owner_id != user_id:
            self.check_data_access(user_id, resource_owner_id)
        
        return True


# Singleton instance
_permission_checker = None


def get_permission_checker() -> PermissionChecker:
    """
    Get global permission checker instance (singleton)
    
    Returns:
        PermissionChecker instance
    """
    global _permission_checker
    if _permission_checker is None:
        _permission_checker = PermissionChecker()
    return _permission_checker

