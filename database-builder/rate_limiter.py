"""
Simple rate limiting utilities for API calls and web scraping.
"""

import time
import logging

logger = logging.getLogger(__name__)


def simple_retry(func, max_attempts=3, delay=2.0):
    """
    Simple retry wrapper with exponential backoff.

    Args:
        func: Function to execute (should take no arguments - use lambda if needed)
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (doubles each time)

    Returns:
        Result of the function call
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt < max_attempts - 1:
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_attempts} attempts failed")
                raise


def rate_limit_delay(seconds=1.0):
    """
    Simple delay to respect rate limits.

    Args:
        seconds: Number of seconds to wait
    """
    time.sleep(seconds)
