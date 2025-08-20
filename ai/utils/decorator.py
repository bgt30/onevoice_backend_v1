import functools
import time
from rich import print as rprint

# ------------------------------
# retry decorator
# ------------------------------

def except_handler(error_msg, retry=0, delay=1, default_return=None):
    """
    Exception handler decorator with retry functionality
    
    Args:
        error_msg: Error message to display
        retry: Number of retry attempts
        delay: Base delay between retries (will be exponential)
        default_return: Default value to return on final failure
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(retry + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    rprint(f"[red]{error_msg}: {e}, retry: {i+1}/{retry}[/red]")
                    if i == retry:
                        if default_return is not None:
                            return default_return
                        raise last_exception
                    time.sleep(delay * (2**i))
        return wrapper
    return decorator
