"""
Enhanced Error Recovery - Comprehensive error handling and recovery strategies.

Provides intelligent error recovery, graceful degradation, and fallback
mechanisms for AI API failures, validation errors, and processing issues.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Dict, List, Optional, Callable, Any, TypeVar, Generic
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import functools

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"  # Cannot continue, must abort
    ERROR = "error"  # Serious issue, but may have fallback
    WARNING = "warning"  # Concerning but recoverable
    INFO = "info"  # Informational, no action needed


class RecoveryStrategy(Enum):
    """Error recovery strategies."""
    RETRY = "retry"  # Retry the operation
    FALLBACK = "fallback"  # Use fallback/alternative approach
    DEGRADE = "degrade"  # Continue with reduced functionality
    SKIP = "skip"  # Skip this item, continue with others
    ABORT = "abort"  # Stop processing entirely
    CACHE = "cache"  # Use cached result if available


@dataclass
class ErrorContext:
    """Context information about an error."""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    component: str = ""
    operation: str = ""
    attempt_number: int = 1
    max_attempts: int = 3
    stacktrace: Optional[str] = None
    user_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryResult(Generic[T]):
    """Result of error recovery attempt."""
    success: bool
    result: Optional[T] = None
    strategy_used: Optional[RecoveryStrategy] = None
    error_context: Optional[ErrorContext] = None
    recovery_notes: List[str] = field(default_factory=list)
    degraded_mode: bool = False


class ErrorRecoverySystem:
    """
    Comprehensive error recovery and handling system.
    
    Provides intelligent error recovery with configurable strategies,
    retry logic, fallback mechanisms, and graceful degradation.
    
    Example:
        >>> recovery = ErrorRecoverySystem()
        >>> result = await recovery.execute_with_recovery(
        ...     risky_operation,
        ...     strategies=[RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK],
        ...     fallback_fn=safe_alternative
        ... )
        >>> if result.success:
        ...     print(f"Got result: {result.result}")
        >>> elif result.degraded_mode:
        ...     print("Operating in degraded mode")
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay_seconds: float = 1.0,
        exponential_backoff: bool = True,
        enable_caching: bool = True
    ):
        """
        Initialize error recovery system.
        
        Args:
            max_retries: Maximum retry attempts
            retry_delay_seconds: Base delay between retries
            exponential_backoff: Use exponential backoff for retries
            enable_caching: Cache successful results for fallback
        """
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.exponential_backoff = exponential_backoff
        self.enable_caching = enable_caching
        
        # Cache for recovery fallbacks
        self._recovery_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Error statistics
        self._error_counts: Dict[str, int] = {}
        self._recovery_counts: Dict[str, int] = {}
        
        logger.info(
            f"ErrorRecoverySystem initialized "
            f"(max_retries={max_retries}, backoff={exponential_backoff})"
        )
    
    async def execute_with_recovery(
        self,
        operation: Callable[..., Any],
        *args,
        strategies: List[RecoveryStrategy] = None,
        fallback_fn: Optional[Callable[..., Any]] = None,
        cache_key: Optional[str] = None,
        component: str = "unknown",
        operation_name: str = "unknown",
        **kwargs
    ) -> RecoveryResult:
        """
        Execute operation with comprehensive error recovery.
        
        Tries operation with configured recovery strategies in order.
        
        Args:
            operation: The function/coroutine to execute
            *args: Positional arguments for operation
            strategies: Ordered list of recovery strategies to try
            fallback_fn: Optional fallback function
            cache_key: Optional key for caching results
            component: Component name for logging
            operation_name: Operation name for logging
            **kwargs: Keyword arguments for operation
            
        Returns:
            RecoveryResult with outcome and any recovered result
        """
        if strategies is None:
            strategies = [RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK]
        
        error_context = None
        last_error = None
        
        # Try each strategy in order
        for strategy in strategies:
            try:
                if strategy == RecoveryStrategy.RETRY:
                    result = await self._execute_with_retry(
                        operation,
                        *args,
                        component=component,
                        operation_name=operation_name,
                        **kwargs
                    )
                    
                    # Cache successful result
                    if self.enable_caching and cache_key:
                        self._cache_result(cache_key, result)
                    
                    return RecoveryResult(
                        success=True,
                        result=result,
                        strategy_used=RecoveryStrategy.RETRY
                    )
                
                elif strategy == RecoveryStrategy.CACHE and cache_key:
                    cached = self._get_cached_result(cache_key)
                    if cached is not None:
                        logger.info(f"Using cached result for {operation_name}")
                        return RecoveryResult(
                            success=True,
                            result=cached,
                            strategy_used=RecoveryStrategy.CACHE,
                            recovery_notes=["Used cached result from previous success"]
                        )
                
                elif strategy == RecoveryStrategy.FALLBACK and fallback_fn:
                    logger.info(f"Attempting fallback for {operation_name}")
                    
                    # Execute fallback
                    if asyncio.iscoroutinefunction(fallback_fn):
                        result = await fallback_fn(*args, **kwargs)
                    else:
                        result = fallback_fn(*args, **kwargs)
                    
                    return RecoveryResult(
                        success=True,
                        result=result,
                        strategy_used=RecoveryStrategy.FALLBACK,
                        recovery_notes=["Fallback function succeeded"],
                        degraded_mode=True
                    )
                
                elif strategy == RecoveryStrategy.DEGRADE:
                    # Return partial/degraded result
                    logger.warning(f"Operating in degraded mode for {operation_name}")
                    return RecoveryResult(
                        success=True,
                        result=None,
                        strategy_used=RecoveryStrategy.DEGRADE,
                        recovery_notes=["Operating in degraded mode"],
                        degraded_mode=True
                    )
                
                elif strategy == RecoveryStrategy.SKIP:
                    logger.info(f"Skipping failed operation: {operation_name}")
                    return RecoveryResult(
                        success=True,
                        result=None,
                        strategy_used=RecoveryStrategy.SKIP,
                        recovery_notes=["Skipped failed operation"]
                    )
            
            except Exception as e:
                logger.error(f"Recovery strategy {strategy.value} failed: {e}")
                last_error = e
                error_context = ErrorContext(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    severity=ErrorSeverity.ERROR,
                    component=component,
                    operation=operation_name
                )
        
        # All strategies exhausted
        logger.error(f"All recovery strategies failed for {operation_name}")
        self._record_error(component, operation_name)
        
        return RecoveryResult(
            success=False,
            error_context=error_context,
            recovery_notes=["All recovery strategies exhausted"]
        )
    
    async def _execute_with_retry(
        self,
        operation: Callable[..., Any],
        *args,
        component: str = "unknown",
        operation_name: str = "unknown",
        **kwargs
    ) -> Any:
        """Execute operation with retry logic."""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"Attempt {attempt}/{self.max_retries} for {operation_name}"
                )
                
                # Execute operation
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)
                
                # Success - record recovery if not first attempt
                if attempt > 1:
                    self._record_recovery(component, operation_name)
                    logger.info(
                        f"{operation_name} succeeded on attempt {attempt}"
                    )
                
                return result
            
            except Exception as e:
                last_error = e
                logger.warning(
                    f"{operation_name} failed (attempt {attempt}): {e}"
                )
                
                # Don't retry on last attempt
                if attempt < self.max_retries:
                    # Calculate delay
                    if self.exponential_backoff:
                        delay = self.retry_delay_seconds * (2 ** (attempt - 1))
                    else:
                        delay = self.retry_delay_seconds
                    
                    logger.debug(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        
        # All retries exhausted
        raise last_error
    
    def _cache_result(self, key: str, result: Any):
        """Cache a successful result."""
        self._recovery_cache[key] = result
        self._cache_timestamps[key] = datetime.now()
        logger.debug(f"Cached result for key: {key}")
    
    def _get_cached_result(
        self,
        key: str,
        max_age_seconds: int = 3600
    ) -> Optional[Any]:
        """Retrieve cached result if available and not expired."""
        if key not in self._recovery_cache:
            return None
        
        # Check age
        cached_at = self._cache_timestamps.get(key)
        if cached_at:
            age = (datetime.now() - cached_at).total_seconds()
            if age > max_age_seconds:
                logger.debug(f"Cache expired for key: {key}")
                del self._recovery_cache[key]
                del self._cache_timestamps[key]
                return None
        
        return self._recovery_cache[key]
    
    def _record_error(self, component: str, operation: str):
        """Record error occurrence for statistics."""
        key = f"{component}.{operation}"
        self._error_counts[key] = self._error_counts.get(key, 0) + 1
    
    def _record_recovery(self, component: str, operation: str):
        """Record successful recovery for statistics."""
        key = f"{component}.{operation}"
        self._recovery_counts[key] = self._recovery_counts.get(key, 0) + 1
    
    def get_error_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get error and recovery statistics."""
        return {
            'errors': dict(self._error_counts),
            'recoveries': dict(self._recovery_counts),
            'cache_entries': len(self._recovery_cache)
        }
    
    def clear_cache(self):
        """Clear recovery cache."""
        self._recovery_cache.clear()
        self._cache_timestamps.clear()
        logger.info("Recovery cache cleared")


# Decorator for automatic error recovery
def with_recovery(
    strategies: List[RecoveryStrategy] = None,
    max_retries: int = 3,
    component: str = "unknown"
):
    """
    Decorator to add error recovery to async functions.
    
    Example:
        >>> @with_recovery(
        ...     strategies=[RecoveryStrategy.RETRY, RecoveryStrategy.CACHE],
        ...     max_retries=3
        ... )
        ... async def risky_api_call():
        ...     return await external_api()
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            recovery_system = ErrorRecoverySystem(max_retries=max_retries)
            
            result = await recovery_system.execute_with_recovery(
                func,
                *args,
                strategies=strategies or [RecoveryStrategy.RETRY],
                component=component,
                operation_name=func.__name__,
                **kwargs
            )
            
            if result.success:
                return result.result
            else:
                raise RuntimeError(
                    f"Operation {func.__name__} failed after all recovery attempts"
                )
        
        return wrapper
    return decorator


# Utility functions for common error scenarios

async def safe_ai_call(
    ai_client,
    prompt: str,
    fallback_response: Optional[str] = None,
    cache_key: Optional[str] = None
) -> RecoveryResult[str]:
    """
    Execute AI API call with comprehensive error recovery.
    
    Args:
        ai_client: AI client (Claude or GPT)
        prompt: Prompt to send
        fallback_response: Optional fallback response
        cache_key: Optional cache key
        
    Returns:
        RecoveryResult with AI response or fallback
    """
    recovery = ErrorRecoverySystem()
    
    async def execute_call():
        return await ai_client.generate(prompt)
    
    async def fallback():
        return fallback_response or "Error: AI service unavailable"
    
    return await recovery.execute_with_recovery(
        execute_call,
        strategies=[
            RecoveryStrategy.RETRY,
            RecoveryStrategy.CACHE,
            RecoveryStrategy.FALLBACK
        ],
        fallback_fn=fallback if fallback_response else None,
        cache_key=cache_key,
        component="ai_client",
        operation_name="generate"
    )


async def safe_parallel_execution(
    operations: List[Callable],
    continue_on_failure: bool = True
) -> List[RecoveryResult]:
    """
    Execute multiple operations in parallel with error recovery.
    
    Args:
        operations: List of async operations to execute
        continue_on_failure: Continue even if some operations fail
        
    Returns:
        List of RecoveryResults
    """
    recovery = ErrorRecoverySystem()
    
    async def execute_with_recovery(op):
        return await recovery.execute_with_recovery(
            op,
            strategies=[
                RecoveryStrategy.RETRY,
                RecoveryStrategy.SKIP if continue_on_failure else RecoveryStrategy.ABORT
            ],
            component="parallel_execution",
            operation_name=op.__name__ if hasattr(op, '__name__') else 'operation'
        )
    
    results = await asyncio.gather(
        *[execute_with_recovery(op) for op in operations],
        return_exceptions=continue_on_failure
    )
    
    return results


# Example usage
if __name__ == "__main__":
    async def example():
        recovery = ErrorRecoverySystem(max_retries=3, exponential_backoff=True)
        
        # Example 1: Simple retry
        async def unreliable_operation():
            import random
            if random.random() < 0.7:
                raise ConnectionError("API timeout")
            return "Success!"
        
        result = await recovery.execute_with_recovery(
            unreliable_operation,
            strategies=[RecoveryStrategy.RETRY],
            component="example",
            operation_name="unreliable_op"
        )
        
        if result.success:
            print(f"Operation succeeded: {result.result}")
        else:
            print(f"Operation failed: {result.error_context.error_message}")
        
        # Example 2: With fallback
        async def risky_operation():
            raise ValueError("Always fails")
        
        def fallback_operation():
            return "Fallback result"
        
        result = await recovery.execute_with_recovery(
            risky_operation,
            strategies=[RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK],
            fallback_fn=fallback_operation,
            component="example",
            operation_name="risky_op"
        )
        
        print(f"Result: {result.result} (degraded: {result.degraded_mode})")
        
        # Show statistics
        stats = recovery.get_error_statistics()
        print(f"\nStatistics: {stats}")
    
    # Run example
    asyncio.run(example())
