"""
Retry Logic and Utilities for SnapWiz
Handles retrying operations that may fail due to temporary issues
"""

import time
import functools
from typing import Callable, Any, Tuple, Type
from exceptions import (
    NetworkError, NetworkTimeoutError, DownloadError,
    InstallationTimeoutError, is_retryable_error
)


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        max_delay=30.0,
        retryable_exceptions=None
    ):
        """
        Initialize retry configuration
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry
            backoff_factor: Multiplier for delay on each retry (exponential backoff)
            max_delay: Maximum delay between retries
            retryable_exceptions: Tuple of exception types that should trigger retry
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        
        if retryable_exceptions is None:
            self.retryable_exceptions = (
                NetworkError,
                NetworkTimeoutError,
                DownloadError,
                InstallationTimeoutError,
            )
        else:
            self.retryable_exceptions = retryable_exceptions


# Default retry configurations
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    backoff_factor=2.0,
    max_delay=30.0
)

NETWORK_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay=2.0,
    backoff_factor=2.0,
    max_delay=60.0,
    retryable_exceptions=(NetworkError, NetworkTimeoutError, DownloadError)
)

INSTALLATION_RETRY_CONFIG = RetryConfig(
    max_attempts=2,
    initial_delay=3.0,
    backoff_factor=1.5,
    max_delay=10.0,
    retryable_exceptions=(InstallationTimeoutError,)
)


def retry_on_failure(
    config=None,
    on_retry_callback=None,
    on_final_failure_callback=None
):
    """
    Decorator to retry a function on failure
    
    Args:
        config: RetryConfig instance (uses DEFAULT_RETRY_CONFIG if None)
        on_retry_callback: Function to call before each retry (attempt_num, exception, delay)
        on_final_failure_callback: Function to call after all retries fail (exception)
    
    Example:
        @retry_on_failure(config=NETWORK_RETRY_CONFIG)
        def download_file(url):
            # Download logic that may fail
            pass
    """
    if config is None:
        config = DEFAULT_RETRY_CONFIG
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    # Try to execute the function
                    return func(*args, **kwargs)
                
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    # If this was the last attempt, give up
                    if attempt >= config.max_attempts:
                        if on_final_failure_callback:
                            on_final_failure_callback(e)
                        raise
                    
                    # Call retry callback if provided
                    if on_retry_callback:
                        on_retry_callback(attempt, e, delay)
                    
                    # Wait before retrying
                    time.sleep(delay)
                    
                    # Calculate next delay (exponential backoff)
                    delay = min(delay * config.backoff_factor, config.max_delay)
                
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def retry_with_progress(
    func,
    args=(),
    kwargs=None,
    config=None,
    progress_callback=None
):
    """
    Retry a function with progress reporting
    
    Args:
        func: Function to execute
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        config: RetryConfig instance
        progress_callback: Function to call with progress updates
                          (attempt, max_attempts, status, message)
    
    Returns:
        Result of the function
    
    Raises:
        Last exception if all retries fail
    """
    if kwargs is None:
        kwargs = {}
    if config is None:
        config = DEFAULT_RETRY_CONFIG
    
    last_exception = None
    delay = config.initial_delay
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            # Report attempt
            if progress_callback:
                progress_callback(
                    attempt,
                    config.max_attempts,
                    'trying',
                    f"Attempt {attempt} of {config.max_attempts}"
                )
            
            # Try to execute
            result = func(*args, **kwargs)
            
            # Report success
            if progress_callback:
                progress_callback(
                    attempt,
                    config.max_attempts,
                    'success',
                    f"Succeeded on attempt {attempt}"
                )
            
            return result
        
        except config.retryable_exceptions as e:
            last_exception = e
            
            # Report failure
            if progress_callback:
                status = 'retrying' if attempt < config.max_attempts else 'failed'
                message = f"Attempt {attempt} failed: {str(e)}"
                if attempt < config.max_attempts:
                    message += f". Retrying in {delay:.1f}s..."
                progress_callback(attempt, config.max_attempts, status, message)
            
            # If this was the last attempt, give up
            if attempt >= config.max_attempts:
                raise
            
            # Wait before retrying
            time.sleep(delay)
            
            # Calculate next delay
            delay = min(delay * config.backoff_factor, config.max_delay)
        
        except Exception as e:
            # Non-retryable exception
            if progress_callback:
                progress_callback(
                    attempt,
                    config.max_attempts,
                    'error',
                    f"Non-retryable error: {str(e)}"
                )
            raise
    
    # Should never reach here
    if last_exception:
        raise last_exception


class RetryableOperation:
    """
    Context manager for retryable operations
    
    Example:
        with RetryableOperation(config=NETWORK_RETRY_CONFIG) as retry:
            result = retry.execute(download_file, url)
    """
    
    def __init__(self, config=None):
        self.config = config if config else DEFAULT_RETRY_CONFIG
        self.attempt = 0
        self.last_error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Let exceptions propagate
        return False
    
    def execute(self, func, *args, **kwargs):
        """Execute a function with retry logic"""
        return retry_with_progress(
            func,
            args=args,
            kwargs=kwargs,
            config=self.config
        )


def should_retry(exception, max_attempts=3, current_attempt=1):
    """
    Determine if an operation should be retried
    
    Args:
        exception: The exception that occurred
        max_attempts: Maximum retry attempts
        current_attempt: Current attempt number
    
    Returns:
        Tuple (should_retry: bool, delay: float)
    """
    # Check if we've exceeded max attempts
    if current_attempt >= max_attempts:
        return False, 0
    
    # Check if exception is retryable
    if not is_retryable_error(exception):
        return False, 0
    
    # Calculate delay (exponential backoff)
    delay = min(2 ** (current_attempt - 1), 30)  # Max 30 seconds
    
    return True, delay


def format_retry_message(attempt, max_attempts, exception, delay=None):
    """
    Format a user-friendly retry message
    
    Args:
        attempt: Current attempt number
        max_attempts: Maximum attempts
        exception: The exception that occurred
        delay: Delay before next retry (seconds)
    
    Returns:
        Formatted message string
    """
    msg = f"⚠️ Attempt {attempt}/{max_attempts} failed: {str(exception)}"
    
    if attempt < max_attempts and delay:
        msg += f"\n🔄 Retrying in {delay:.1f} seconds..."
    elif attempt >= max_attempts:
        msg += "\n❌ All retry attempts exhausted."
    
    return msg


# ==================== Examples ====================

def example_retryable_download(url):
    """Example of a retryable download operation"""
    
    @retry_on_failure(
        config=NETWORK_RETRY_CONFIG,
        on_retry_callback=lambda attempt, exc, delay: print(
            f"Download failed (attempt {attempt}): {exc}. Retrying in {delay}s..."
        ),
        on_final_failure_callback=lambda exc: print(
            f"Download failed after all retries: {exc}"
        )
    )
    def download():
        # Actual download logic here
        import urllib.request
        response = urllib.request.urlopen(url, timeout=10)
        return response.read()
    
    return download()


def example_with_progress_callback():
    """Example using progress callback"""
    
    def progress_handler(attempt, max_attempts, status, message):
        print(f"[{status.upper()}] {message}")
    
    def risky_operation():
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise NetworkTimeoutError("Operation timed out", 10)
        return "Success!"
    
    result = retry_with_progress(
        risky_operation,
        config=NETWORK_RETRY_CONFIG,
        progress_callback=progress_handler
    )
    
    return result
