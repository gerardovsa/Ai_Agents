"""
UNIVERSAL CONFIRMATION SYSTEM - AI Infrastructure Core
=======================================================

Enables ANY tool to request user confirmation before proceeding with
expensive/destructive/large operations.

This is a UNIVERSAL pattern that works for:
- Email (large attachments, many messages)
- File operations (delete many files, large downloads)
- API calls (expensive operations, rate limits)
- Database (bulk operations, destructive queries)
- Any tool that needs user approval

Key Features:
- Declarative confirmation requirements
- Token/cost estimation
- Risk level assessment
- User-friendly prompts
- Seamless multi-turn conversation

Usage:
    from AI_infrastructure.core.confirmation_manager import (
        requires_confirmation,
        ConfirmationRequest,
        ConfirmationLevel
    )
    
    @requires_confirmation(
        level=ConfirmationLevel.MEDIUM,
        estimate_cost=lambda args: calculate_token_cost(args['size'])
    )
    def my_expensive_tool(param1, param2, **kwargs):
        # Tool implementation
        pass
"""

from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass, asdict
import json


class ConfirmationLevel(Enum):
    """Risk/cost levels for operations requiring confirmation"""
    LOW = "low"              # < $0.01, < 1k tokens, low risk
    MEDIUM = "medium"        # $0.01-$0.10, 1k-20k tokens, medium risk
    HIGH = "high"            # $0.10-$1.00, 20k-100k tokens, high risk
    CRITICAL = "critical"    # > $1.00, > 100k tokens, destructive operations


@dataclass
class ConfirmationRequest:
    """
    Structured confirmation request that tools return
    
    This is the STANDARD format that all tools use when they need
    user confirmation before proceeding.
    """
    
    # Status flag (agent_worker.py checks for this)
    status: str = "confirmation_required"
    
    # Confirmation details
    level: str = ConfirmationLevel.MEDIUM.value
    reason: str = ""
    operation_summary: str = ""
    
    # Cost/resource estimates
    estimated_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None
    estimated_time_seconds: Optional[int] = None
    
    # Risk assessment
    is_destructive: bool = False
    is_reversible: bool = True
    affected_items: List[str] = None
    
    # Context for continuation
    tool_name: str = ""
    tool_args: Dict[str, Any] = None
    confirmation_prompt: str = ""
    
    # User-facing options
    options: List[Dict[str, str]] = None  # [{label, value, description}]
    default_option: Optional[str] = None
    
    def __post_init__(self):
        """Set defaults and validate"""
        if self.affected_items is None:
            self.affected_items = []
        
        if self.tool_args is None:
            self.tool_args = {}
        
        if self.options is None:
            # Default options
            self.options = [
                {
                    "label": "Proceed",
                    "value": "confirm",
                    "description": "Continue with this operation"
                },
                {
                    "label": "Cancel",
                    "value": "cancel",
                    "description": "Skip this operation"
                }
            ]
            self.default_option = "confirm"
        
        # Auto-generate prompt if not provided
        if not self.confirmation_prompt:
            self.confirmation_prompt = self._generate_prompt()
    
    def _generate_prompt(self) -> str:
        """Generate user-friendly confirmation prompt"""
        lines = [f"**{self.operation_summary}**\n"]
        
        if self.reason:
            lines.append(f"Reason: {self.reason}\n")
        
        # Cost estimates
        if self.estimated_tokens or self.estimated_cost_usd:
            lines.append("**Resource Requirements:**")
            if self.estimated_tokens:
                lines.append(f"- Tokens: ~{self.estimated_tokens:,}")
            if self.estimated_cost_usd:
                lines.append(f"- Cost: ~${self.estimated_cost_usd:.4f}")
            if self.estimated_time_seconds:
                mins = self.estimated_time_seconds // 60
                secs = self.estimated_time_seconds % 60
                if mins > 0:
                    lines.append(f"- Time: ~{mins}m {secs}s")
                else:
                    lines.append(f"- Time: ~{secs}s")
            lines.append("")
        
        # Risk warnings
        if self.is_destructive or not self.is_reversible:
            lines.append("**⚠️ Warning:**")
            if self.is_destructive:
                lines.append("- This operation is DESTRUCTIVE")
            if not self.is_reversible:
                lines.append("- This operation CANNOT be undone")
            lines.append("")
        
        # Affected items
        if self.affected_items:
            lines.append(f"**Affected Items ({len(self.affected_items)}):**")
            for item in self.affected_items[:5]:  # Show max 5
                lines.append(f"- {item}")
            if len(self.affected_items) > 5:
                lines.append(f"- ... and {len(self.affected_items) - 5} more")
            lines.append("")
        
        lines.append("**How would you like to proceed?**")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class ConfirmationManager:
    """
    Manages confirmation requests across the entire system
    
    This is used by:
    - agent_worker.py to detect confirmation requests
    - Tools to generate confirmation requests
    - Frontend to display confirmation dialogs
    """
    
    # Thresholds for automatic confirmation triggering
    TOKEN_THRESHOLD = 10000      # > 10k tokens requires confirmation
    COST_THRESHOLD = 0.03        # > $0.03 requires confirmation
    SIZE_THRESHOLD_MB = 5        # > 5 MB requires confirmation
    
    @staticmethod
    def should_confirm(
        tokens: Optional[int] = None,
        cost_usd: Optional[float] = None,
        size_mb: Optional[float] = None,
        is_destructive: bool = False,
        level: Optional[ConfirmationLevel] = None
    ) -> bool:
        """
        Determine if operation requires confirmation
        
        Args:
            tokens: Estimated token count
            cost_usd: Estimated cost in USD
            size_mb: Data size in MB
            is_destructive: Whether operation is destructive
            level: Explicit confirmation level
        
        Returns:
            True if confirmation needed
        """
        # Always confirm destructive operations
        if is_destructive:
            return True
        
        # Explicit level check
        if level and level in [ConfirmationLevel.HIGH, ConfirmationLevel.CRITICAL]:
            return True
        
        # Threshold checks
        if tokens and tokens > ConfirmationManager.TOKEN_THRESHOLD:
            return True
        
        if cost_usd and cost_usd > ConfirmationManager.COST_THRESHOLD:
            return True
        
        if size_mb and size_mb > ConfirmationManager.SIZE_THRESHOLD_MB:
            return True
        
        return False
    
    @staticmethod
    def create_request(
        tool_name: str,
        operation_summary: str,
        reason: str = "",
        level: ConfirmationLevel = ConfirmationLevel.MEDIUM,
        **kwargs
    ) -> ConfirmationRequest:
        """
        Create a standardized confirmation request
        
        Args:
            tool_name: Name of tool requesting confirmation
            operation_summary: One-line summary of operation
            reason: Why confirmation is needed
            level: Risk/cost level
            **kwargs: Additional ConfirmationRequest fields
        
        Returns:
            ConfirmationRequest instance
        """
        return ConfirmationRequest(
            tool_name=tool_name,
            operation_summary=operation_summary,
            reason=reason,
            level=level.value,
            **kwargs
        )
    
    @staticmethod
    def parse_user_response(user_message: str) -> Dict[str, Any]:
        """
        Parse user's confirmation response
        
        Args:
            user_message: User's response (e.g., "yes", "proceed", "cancel")
        
        Returns:
            {
                'action': 'confirm' | 'cancel' | 'modify',
                'confirmed': bool,
                'modifications': dict (if action='modify')
            }
        """
        msg_lower = user_message.lower().strip()
        
        # Confirm patterns
        confirm_patterns = [
            'yes', 'proceed', 'confirm', 'continue', 'do it',
            'go ahead', 'ok', 'okay', 'sure', 'read full',
            'read everything', 'full content'
        ]
        
        # Cancel patterns
        cancel_patterns = [
            'no', 'cancel', 'stop', 'skip', 'abort', 'never mind',
            'don\'t', 'do not', 'nope'
        ]
        
        # Modification patterns
        modify_patterns = [
            'just metadata', 'metadata only', 'summary only',
            'without attachments', 'skip attachments'
        ]
        
        # Check patterns
        if any(pattern in msg_lower for pattern in confirm_patterns):
            return {
                'action': 'confirm',
                'confirmed': True,
                'modifications': {}
            }
        
        if any(pattern in msg_lower for pattern in cancel_patterns):
            return {
                'action': 'cancel',
                'confirmed': False,
                'modifications': {}
            }
        
        if any(pattern in msg_lower for pattern in modify_patterns):
            # Parse specific modifications
            mods = {}
            if 'metadata' in msg_lower:
                mods['format'] = 'metadata'
            if 'without attachments' in msg_lower or 'skip attachments' in msg_lower:
                mods['include_attachments'] = False
            
            return {
                'action': 'modify',
                'confirmed': True,
                'modifications': mods
            }
        
        # Default: assume confirmation if ambiguous
        return {
            'action': 'confirm',
            'confirmed': True,
            'modifications': {}
        }


def requires_confirmation(
    level: ConfirmationLevel = ConfirmationLevel.MEDIUM,
    estimate_cost: Optional[Callable] = None,
    estimate_tokens: Optional[Callable] = None,
    check_condition: Optional[Callable] = None,
    operation_summary: Optional[str] = None
):
    """
    Decorator to add confirmation capability to any tool
    
    This is the EASY way to add confirmation to tools. Just decorate
    your function and it will automatically check if confirmation is
    needed before executing.
    
    Args:
        level: Default confirmation level
        estimate_cost: Function to estimate cost from args
        estimate_tokens: Function to estimate tokens from args
        check_condition: Function to check if confirmation needed
        operation_summary: Human-readable operation description
    
    Example:
        @requires_confirmation(
            level=ConfirmationLevel.HIGH,
            estimate_tokens=lambda args: len(args['messages']) * 1000,
            operation_summary="Analyze email thread"
        )
        def analyze_email_thread(thread_id, **kwargs):
            # Implementation
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check if this is a confirmation bypass
            if kwargs.get('_confirmation_bypassed'):
                # Remove flag and execute
                kwargs.pop('_confirmation_bypassed')
                return func(*args, **kwargs)
            
            # Build args dict for estimation
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            args_dict = dict(bound_args.arguments)
            
            # Estimate resources
            tokens = estimate_tokens(args_dict) if estimate_tokens else None
            cost = estimate_cost(args_dict) if estimate_cost else None
            
            # Check if confirmation needed
            needs_confirm = check_condition(args_dict) if check_condition else \
                           ConfirmationManager.should_confirm(
                               tokens=tokens,
                               cost_usd=cost,
                               level=level
                           )
            
            if needs_confirm:
                # Generate confirmation request
                summary = operation_summary or f"Execute {func.__name__}"
                
                request = ConfirmationManager.create_request(
                    tool_name=func.__name__,
                    operation_summary=summary,
                    reason=f"Operation may use {tokens or 'many'} tokens" if tokens else "High resource usage",
                    level=level,
                    estimated_tokens=tokens,
                    estimated_cost_usd=cost,
                    tool_args=args_dict
                )
                
                return request.to_dict()
            
            # No confirmation needed, execute directly
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ==================== HELPER FUNCTIONS ====================

def create_email_confirmation(
    message_id: str,
    subject: str,
    from_addr: str,
    attachments: List[Dict],
    size_mb: float,
    estimated_tokens: int
) -> ConfirmationRequest:
    """
    Helper to create email-specific confirmation requests
    
    Example:
        request = create_email_confirmation(
            message_id="msg_123",
            subject="Q4 Contract Review",
            from_addr="john@example.com",
            attachments=[...],
            size_mb=12.5,
            estimated_tokens=25000
        )
    """
    # Format attachment list
    attachment_names = [att.get('filename', 'Unknown') for att in attachments]
    
    # Calculate cost (rough estimate: $3 per 1M tokens)
    cost_usd = (estimated_tokens / 1_000_000) * 3
    
    return ConfirmationRequest(
        tool_name="gmail_get_message_parsed",
        operation_summary=f"Read email: '{subject}' from {from_addr}",
        reason=f"Email has {len(attachments)} attachments ({size_mb:.1f} MB total)",
        level=ConfirmationLevel.HIGH.value if size_mb > 10 else ConfirmationLevel.MEDIUM.value,
        estimated_tokens=estimated_tokens,
        estimated_cost_usd=cost_usd,
        affected_items=attachment_names,
        tool_args={'message_id': message_id},
        options=[
            {
                "label": "Read Full Content",
                "value": "confirm",
                "description": f"Parse email and {len(attachments)} attachments (~{estimated_tokens:,} tokens)"
            },
            {
                "label": "Metadata Only",
                "value": "metadata",
                "description": "Just show subject, sender, and snippet (~500 tokens)"
            },
            {
                "label": "Cancel",
                "value": "cancel",
                "description": "Skip this email"
            }
        ],
        default_option="confirm"
    )


def create_file_operation_confirmation(
    operation: str,
    file_paths: List[str],
    is_destructive: bool = False,
    estimated_time_seconds: Optional[int] = None
) -> ConfirmationRequest:
    """
    Helper for file operation confirmations
    
    Example:
        request = create_file_operation_confirmation(
            operation="Delete",
            file_paths=['file1.txt', 'file2.txt'],
            is_destructive=True
        )
    """
    return ConfirmationRequest(
        tool_name="file_operations",
        operation_summary=f"{operation} {len(file_paths)} files",
        reason=f"{'Destructive' if is_destructive else 'Bulk'} operation affecting multiple files",
        level=ConfirmationLevel.CRITICAL.value if is_destructive else ConfirmationLevel.MEDIUM.value,
        is_destructive=is_destructive,
        is_reversible=not is_destructive,
        affected_items=file_paths[:10],  # Show max 10
        estimated_time_seconds=estimated_time_seconds,
        tool_args={'operation': operation, 'files': file_paths}
    )


def create_database_confirmation(
    query: str,
    affected_rows: int,
    is_destructive: bool = False
) -> ConfirmationRequest:
    """
    Helper for database operation confirmations
    
    Example:
        request = create_database_confirmation(
            query="DELETE FROM users WHERE active=0",
            affected_rows=150,
            is_destructive=True
        )
    """
    return ConfirmationRequest(
        tool_name="database_query",
        operation_summary=f"Execute database query affecting {affected_rows} rows",
        reason="Bulk database operation",
        level=ConfirmationLevel.CRITICAL.value if is_destructive else ConfirmationLevel.MEDIUM.value,
        is_destructive=is_destructive,
        is_reversible=False,
        affected_items=[f"{affected_rows} database rows"],
        tool_args={'query': query}
    )
