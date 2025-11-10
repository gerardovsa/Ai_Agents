"""
Workspace Exceptions - Custom error types for workspace operations
"""


class WorkspaceError(Exception):
    """Base exception for workspace errors"""
    pass


class WorkspaceNotFoundError(WorkspaceError):
    """Workspace not found"""
    
    def __init__(self, workspace_id: int = None, slug: str = None):
        if workspace_id:
            message = f"Workspace not found: ID={workspace_id}"
        elif slug:
            message = f"Workspace not found: slug={slug}"
        else:
            message = "Workspace not found"
        super().__init__(message)
        self.workspace_id = workspace_id
        self.slug = slug


class WorkspaceSlugExistsError(WorkspaceError):
    """Workspace slug already exists"""
    
    def __init__(self, slug: str):
        super().__init__(f"Workspace slug already exists: {slug}")
        self.slug = slug


class WorkspacePermissionError(WorkspaceError):
    """User lacks required permission"""
    
    def __init__(self, user_id: int, workspace_id: int, permission: str):
        message = f"User {user_id} lacks permission '{permission}' in workspace {workspace_id}"
        super().__init__(message)
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.permission = permission


class WorkspaceArchivedError(WorkspaceError):
    """Workspace is archived"""
    
    def __init__(self, workspace_id: int):
        super().__init__(f"Workspace {workspace_id} is archived")
        self.workspace_id = workspace_id


class WorkspaceCapacityError(WorkspaceError):
    """Workspace at capacity"""
    
    def __init__(self, workspace_id: int, current: int, limit: int):
        message = f"Workspace {workspace_id} at capacity ({current}/{limit} members)"
        super().__init__(message)
        self.workspace_id = workspace_id
        self.current_members = current
        self.member_limit = limit


class WorkspaceMemberNotFoundError(WorkspaceError):
    """Workspace member not found"""
    
    def __init__(self, workspace_id: int, user_id: int):
        message = f"User {user_id} is not a member of workspace {workspace_id}"
        super().__init__(message)
        self.workspace_id = workspace_id
        self.user_id = user_id


class WorkspaceMemberAlreadyExistsError(WorkspaceError):
    """User is already a workspace member"""
    
    def __init__(self, workspace_id: int, user_id: int):
        message = f"User {user_id} is already a member of workspace {workspace_id}"
        super().__init__(message)
        self.workspace_id = workspace_id
        self.user_id = user_id


class CannotRemoveSelfError(WorkspaceError):
    """Cannot remove yourself from workspace"""
    
    def __init__(self, workspace_id: int, user_id: int):
        message = f"User {user_id} cannot remove themselves from workspace {workspace_id}"
        super().__init__(message)
        self.workspace_id = workspace_id
        self.user_id = user_id


class InvitationError(WorkspaceError):
    """Base exception for invitation errors"""
    pass


class InvitationNotFoundError(InvitationError):
    """Invitation not found"""
    
    def __init__(self, invitation_id: int = None, token: str = None):
        if invitation_id:
            message = f"Invitation not found: ID={invitation_id}"
        elif token:
            message = f"Invitation not found: token={token[:8]}..."
        else:
            message = "Invitation not found"
        super().__init__(message)
        self.invitation_id = invitation_id
        self.token = token


class InvitationExpiredError(InvitationError):
    """Invitation has expired"""
    
    def __init__(self, invitation_id: int):
        super().__init__(f"Invitation {invitation_id} has expired")
        self.invitation_id = invitation_id


class InvitationAlreadyProcessedError(InvitationError):
    """Invitation already accepted/declined/cancelled"""
    
    def __init__(self, invitation_id: int, status: str):
        message = f"Invitation {invitation_id} already processed: {status}"
        super().__init__(message)
        self.invitation_id = invitation_id
        self.status = status


class InvalidRoleError(WorkspaceError):
    """Invalid workspace role"""
    
    def __init__(self, role: str):
        super().__init__(f"Invalid workspace role: {role}")
        self.role = role


class SlugError(WorkspaceError):
    """Base exception for slug errors"""
    pass


class InvalidSlugError(SlugError):
    """Slug format is invalid"""
    
    def __init__(self, slug: str, reason: str = None):
        message = f"Invalid slug: {slug}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)
        self.slug = slug
        self.reason = reason


class ReservedSlugError(SlugError):
    """Slug is reserved and cannot be used"""
    
    def __init__(self, slug: str):
        super().__init__(f"Slug is reserved: {slug}")
        self.slug = slug


class MemberNotFoundError(WorkspaceError):
    """Member record not found"""
    
    def __init__(self, workspace_id: int, user_id: int):
        message = f"Member not found: user={user_id} in workspace={workspace_id}"
        super().__init__(message)
        self.workspace_id = workspace_id
        self.user_id = user_id


class InvalidWorkspaceSlugError(SlugError):
    """Workspace slug is invalid"""
    
    def __init__(self, slug: str, reason: str = None):
        message = f"Invalid workspace slug: {slug}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)
        self.slug = slug
        self.reason = reason


class DuplicateWorkspaceError(WorkspaceError):
    """Workspace with same slug already exists"""
    
    def __init__(self, slug: str):
        super().__init__(f"Workspace already exists with slug: {slug}")
        self.slug = slug


class MaxMembersReachedError(WorkspaceError):
    """Workspace has reached maximum member limit"""
    
    def __init__(self, workspace_id: int, limit: int):
        super().__init__(f"Workspace {workspace_id} has reached member limit ({limit})")
        self.workspace_id = workspace_id
        self.limit = limit


class UserNotFoundError(WorkspaceError):
    """User not found"""
    
    def __init__(self, user_id: int):
        super().__init__(f"User not found: {user_id}")
        self.user_id = user_id


class DuplicateMemberError(WorkspaceError):
    """User is already a member of workspace"""
    
    def __init__(self, workspace_id: int, user_id: int):
        super().__init__(f"User {user_id} is already member of workspace {workspace_id}")
        self.workspace_id = workspace_id
        self.user_id = user_id


class DatabaseError(WorkspaceError):
    """Database operation failed"""
    
    def __init__(self, operation: str, details: str = None):
        message = f"Database error during {operation}"
        if details:
            message += f": {details}"
        super().__init__(message)
        self.operation = operation
        self.details = details
