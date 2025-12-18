"""
FILE: AI_infrastructure/shared/circuit_breaker.py
PURPOSE: Circuit breaker pattern to prevent cascading failures

Prevents repeated calls to failing services that could exhaust connection pools
or cause other resource exhaustion issues.

PATTERN:
- CLOSED: Normal operation, all requests pass through
- OPEN: Too many failures, all requests fail fast without trying
- HALF_OPEN: After cooldown, allow one test request

USAGE:
    from shared.circuit_breaker import CircuitBreaker
    
    gmail_circuit = CircuitBreaker(
        name='gmail_api',
        failure_threshold=5,      # Open after 5 failures
        recovery_timeout=60,      # Try again after 60 seconds
        expected_exception=Exception
    )
    
    @gmail_circuit.call
    def fetch_gmail_messages():
        # Your code here
        pass
"""

import time
import logging
from typing import Callable, Any, Optional
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures
    
    Tracks failures and opens circuit to fail fast when threshold exceeded.
    After recovery timeout, allows one test request (half-open state).
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            name: Identifier for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
        logger.info(f"[CIRCUIT_BREAKER] Initialized '{name}' circuit breaker "
                   f"(threshold={failure_threshold}, timeout={recovery_timeout}s)")
    
    def call(self, func: Callable) -> Callable:
        """
        Decorator to wrap function with circuit breaker
        
        Usage:
            @circuit_breaker.call
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self._execute(func, *args, **kwargs)
        return wrapper
    
    def _execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(f"[CIRCUIT_BREAKER] '{self.name}' entering HALF_OPEN state for test request")
                self.state = CircuitState.HALF_OPEN
            else:
                time_until_reset = self.recovery_timeout - (time.time() - self.last_failure_time)
                logger.warning(f"[CIRCUIT_BREAKER] '{self.name}' is OPEN "
                             f"(wait {int(time_until_reset)}s before retry)")
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable, retry in {int(time_until_reset)} seconds."
                )
        
        # Attempt to execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"[CIRCUIT_BREAKER] '{self.name}' test request succeeded, closing circuit")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
        elif self.failure_count > 0:
            # Gradually recover from failures
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            logger.warning(f"[CIRCUIT_BREAKER] '{self.name}' test request failed, reopening circuit")
            self.state = CircuitState.OPEN
        elif self.failure_count >= self.failure_threshold:
            logger.error(f"[CIRCUIT_BREAKER] '{self.name}' threshold reached "
                        f"({self.failure_count} failures), opening circuit")
            self.state = CircuitState.OPEN
        else:
            logger.warning(f"[CIRCUIT_BREAKER] '{self.name}' failure {self.failure_count}/"
                          f"{self.failure_threshold}")
    
    def reset(self):
        """Manually reset circuit breaker"""
        logger.info(f"[CIRCUIT_BREAKER] '{self.name}' manually reset")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
    
    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'last_failure_time': self.last_failure_time,
            'recovery_timeout': self.recovery_timeout
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and request is rejected"""
    pass
