"""
Error Handler - Advanced error recovery and retry strategies
Part of V4 Modular Architecture

Responsibilities:
- Define custom exception hierarchy
- Implement retry logic with exponential backoff
- Categorize errors (temporary vs permanent)
- Format error messages for users
- Log errors comprehensively
"""

from typing import Optional, Callable, Any, Dict
import time
import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# CUSTOM EXCEPTION HIERARCHY
# ============================================================

class AgentError(Exception):
    """Base exception for all agent-related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        logger.error(f"{self.__class__.__name__}: {message}", extra={'details': self.details})


class ToolExecutionError(AgentError):
    """Error during tool execution."""
    pass


class CredentialError(AgentError):
    """Error retrieving or validating credentials."""
    pass


class SessionError(AgentError):
    """Error managing conversation sessions."""
    pass


class APIError(AgentError):
    """Error communicating with external API (Claude, Google, etc.)."""
    pass


class ValidationError(AgentError):
    """Input validation failed."""
    pass


class TemporaryError(AgentError):
    """Temporary error that may succeed on retry."""
    pass


class PermanentError(AgentError):
    """Permanent error that will not succeed on retry."""
    pass


# ============================================================
# ERROR CATEGORIZATION
# ============================================================

def is_temporary_error(error: Exception) -> bool:
    """
    Determine if error is temporary (worth retrying).
    
    Args:
        error: Exception instance
        
    Returns:
        True if error may resolve on retry, False otherwise
    """
    temporary_errors = (
        TemporaryError,
        ConnectionError,
        TimeoutError,
    )
    
    # Check exception type
    if isinstance(error, temporary_errors):
        return True
    
    # Check error message for temporary indicators
    error_str = str(error).lower()
    temporary_keywords = [
        'timeout',
        'connection',
        'rate limit',
        'too many requests',
        'temporarily unavailable',
        '429',
        '503',
        '504'
    ]
    
    return any(keyword in error_str for keyword in temporary_keywords)


def categorize_error(error: Exception) -> str:
    """
    Categorize error type for logging and handling.
    
    Args:
        error: Exception instance
        
    Returns:
        Category string: 'temporary', 'permanent', 'credential', 'validation', 'api', 'unknown'
    """
    if isinstance(error, TemporaryError):
        return 'temporary'
    elif isinstance(error, PermanentError):
        return 'permanent'
    elif isinstance(error, CredentialError):
        return 'credential'
    elif isinstance(error, ValidationError):
        return 'validation'
    elif isinstance(error, APIError):
        return 'api'
    elif is_temporary_error(error):
        return 'temporary'
    else:
        return 'unknown'


# ============================================================
# RETRY LOGIC
# ============================================================

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with exponential backoff retry strategy.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay between retries (seconds)
        *args, **kwargs: Arguments to pass to func
        
    Returns:
        Result from successful function execution
        
    Raises:
        Exception: Last exception if all retries exhausted
        
    Example:
        result = retry_with_backoff(
            call_api,
            max_retries=3,
            api_key="sk-...",
            endpoint="/users"
        )
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"Executing {func.__name__} (attempt {attempt + 1}/{max_retries + 1})")
            result = func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"{func.__name__} succeeded after {attempt} retries")
            
            return result
            
        except Exception as e:
            last_exception = e
            
            # Check if error is worth retrying
            if not is_temporary_error(e):
                logger.warning(f"{func.__name__} failed with permanent error: {e}")
                raise
            
            # Last attempt - don't wait
            if attempt >= max_retries:
                logger.error(f"{func.__name__} failed after {max_retries} retries: {e}")
                raise
            
            # Wait before retry with exponential backoff
            logger.warning(f"{func.__name__} failed (attempt {attempt + 1}): {e}. "
                         f"Retrying in {delay:.1f}s...")
            time.sleep(delay)
            
            # Increase delay for next attempt
            delay = min(delay * backoff_factor, max_delay)
    
    # Should never reach here, but just in case
    raise last_exception


# ============================================================
# ERROR FORMATTING
# ============================================================

def format_error_for_user(error: Exception) -> str:
    """
    Format error message for user display (hide technical details).
    
    Args:
        error: Exception instance
        
    Returns:
        User-friendly error message
    """
    category = categorize_error(error)
    
    # User-friendly error messages
    messages = {
        'credential': "Authentication failed. Please reconnect your account.",
        'validation': "Invalid input. Please check your request and try again.",
        'temporary': "Service temporarily unavailable. Please try again in a moment.",
        'api': "Unable to communicate with service. Please try again later.",
        'permanent': "Request failed. Please contact support if this persists.",
        'unknown': "An unexpected error occurred. Please try again."
    }
    
    base_message = messages.get(category, messages['unknown'])
    
    # Add specific error message if it's user-safe
    if isinstance(error, AgentError):
        return f"{base_message}\n\nDetails: {error.message}"
    
    return base_message


def format_error_for_log(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Format detailed error message for logging.
    
    Args:
        error: Exception instance
        context: Optional context dictionary (user_id, session_id, etc.)
        
    Returns:
        Detailed error message for logs
    """
    category = categorize_error(error)
    
    parts = [
        f"[{category.upper()} ERROR]",
        f"Type: {error.__class__.__name__}",
        f"Message: {str(error)}",
    ]
    
    if context:
        parts.append(f"Context: {context}")
    
    if isinstance(error, AgentError) and error.details:
        parts.append(f"Details: {error.details}")
    
    return " | ".join(parts)


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def safe_execute(func: Callable, *args, **kwargs) -> tuple[bool, Optional[Any], Optional[Exception]]:
    """
    Execute function safely, catching all exceptions.
    
    Args:
        func: Function to execute
        *args, **kwargs: Arguments to pass to func
        
    Returns:
        Tuple of (success: bool, result: Any, error: Exception)
        
    Example:
        success, result, error = safe_execute(risky_function, param1="value")
        if success:
            print(f"Result: {result}")
        else:
            print(f"Error: {error}")
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        logger.error(f"safe_execute caught error in {func.__name__}: {e}")
        return False, None, e


def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Comprehensive error handling - log and format for response.
    
    Args:
        error: Exception instance
        context: Optional context dictionary
        
    Returns:
        Dictionary with error information for API response
    """
    category = categorize_error(error)
    
    # Log detailed error
    log_message = format_error_for_log(error, context)
    logger.error(log_message)
    
    # Format user-friendly error
    user_message = format_error_for_user(error)
    
    return {
        'success': False,
        'error': user_message,
        'error_type': category,
        'error_class': error.__class__.__name__,
        'retry_recommended': is_temporary_error(error)
    }


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    # Exception classes
    'AgentError',
    'ToolExecutionError',
    'CredentialError',
    'SessionError',
    'APIError',
    'ValidationError',
    'TemporaryError',
    'PermanentError',
    # Functions
    'is_temporary_error',
    'categorize_error',
    'retry_with_backoff',
    'format_error_for_user',
    'format_error_for_log',
    'safe_execute',
    'handle_error'
]
