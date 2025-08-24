import time
import random
from typing import Callable, Any, Optional
from tenacity import Retrying, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

# Import logger only when needed to avoid circular imports
def get_logger_safe():
    """Safely get logger to avoid circular imports."""
    try:
        from logging_config import get_logger
        return get_logger()
    except ImportError:
        import logging
        return logging.getLogger(__name__)

class RetryableHTTPError(Exception):
    """Custom exception for retryable HTTP errors (5xx)."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")

def is_retryable_error(exception: Exception) -> bool:
    """Check if an exception is retryable (5xx HTTP errors or connection issues)."""
    if isinstance(exception, RetryableHTTPError):
        return 500 <= exception.status_code < 600
    if isinstance(exception, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
        return True
    return False

def retry_with_tenacity(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    *args,
    **kwargs
) -> Any:
    """
    Retry function using tenacity library with exponential backoff.
    
    Args:
        func: Function to retry
        max_attempts: Maximum retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        *args, **kwargs: Arguments to pass to function
        
    Returns:
        Function result
        
    Raises:
        Exception: Final exception if all retries fail
    """
    logger = get_logger_safe()
    attempt_count = 0
    
    def log_retry_attempt(retry_state):
        nonlocal attempt_count
        attempt_count += 1
        logger.warning(
            "Retry attempt",
            attempt=attempt_count,
            max_attempts=max_attempts,
            delay_seconds=retry_state.next_action.sleep if hasattr(retry_state.next_action, 'sleep') else 0,
            exception=str(retry_state.outcome.exception()) if retry_state.outcome.failed else None
        )
    
    try:
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=base_delay, max=max_delay),
            retry=retry_if_exception_type((RetryableHTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout)),
            before_sleep=log_retry_attempt
        ):
            with attempt:
                logger.info("Function call attempt", attempt=attempt_count + 1)
                result = func(*args, **kwargs)
                if attempt_count > 0:
                    logger.info("Retry succeeded", final_attempt=attempt_count + 1)
                return result
                
    except Exception as e:
        logger.error(
            "All retry attempts failed",
            final_attempt=attempt_count,
            max_attempts=max_attempts,
            final_exception=str(e)
        )
        raise

def retry_with_custom_backoff(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    *args,
    **kwargs
) -> Any:
    """
    Custom implementation of exponential backoff retry.
    
    Args:
        func: Function to retry
        max_attempts: Maximum retry attempts
        base_delay: Base delay in seconds
        *args, **kwargs: Arguments to pass to function
        
    Returns:
        Function result
        
    Raises:
        Exception: Final exception if all retries fail
    """
    logger = get_logger_safe()  # Add this line to fix the undefined logger
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            logger.info("Function call attempt", attempt=attempt + 1, max_attempts=max_attempts)
            result = func(*args, **kwargs)
            
            if attempt > 0:
                logger.info("Retry succeeded", final_attempt=attempt + 1)
            return result
            
        except Exception as e:
            last_exception = e
            
            if not is_retryable_error(e):
                logger.error("Non-retryable error encountered", exception=str(e), attempt=attempt + 1)
                raise
            
            if attempt == max_attempts - 1:
                logger.error(
                    "All retry attempts failed",
                    final_attempt=attempt + 1,
                    max_attempts=max_attempts,
                    final_exception=str(e)
                )
                raise
            
            # Calculate delay with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
            
            logger.warning(
                "Retry attempt failed",
                attempt=attempt + 1,
                exception=str(e),
                next_delay_seconds=delay
            )
            
            time.sleep(delay)
    
    # Should never reach here, but just in case
    raise last_exception or Exception("Unknown retry failure")
