#!/usr/bin/env python3
"""
Utility Helper Functions

Provides common utilities for the Research Assistant:
- Logging setup
- Configuration loading
- Cache management
- Rate limiting
- Retry logic
- Text cleaning
- Author name formatting

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import re
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from pathlib import Path

import yaml


# Configure module logger
logger = logging.getLogger(__name__)


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        level: Logging level (logging.INFO, logging.DEBUG, etc.)
        log_file: Optional path to log file.
        format_str: Optional custom format string.

    Returns:
        Configured logger.
    """
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create formatter
    formatter = logging.Formatter(format_str)

    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Set up file handler if log_file specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(level)

    # Add console handler to root logger
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.setLevel(level)

    return logger


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, checks default locations.

    Returns:
        Configuration dictionary.
    """
    config = {}

    # Default locations to check
    default_paths = [
        'config.yaml',
        'config/config.yaml',
        '.research_assistant_config',
        os.path.expanduser('~/.research_assistant.yaml'),
    ]

    if config_path:
        default_paths.insert(0, config_path)

    for path in default_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    if path.endswith('.yaml') or path.endswith('.yml'):
                        config = yaml.safe_load(f) or {}
                    elif path.endswith('.json'):
                        config = json.load(f) or {}
                    else:
                        # Try both YAML and JSON
                        try:
                            config = yaml.safe_load(f) or {}
                        except yaml.YAMLError:
                            f.seek(0)
                            config = json.load(f) or {}

                logger.info(f"Loaded configuration from: {path}")
                break
            except Exception as e:
                logger.warning(f"Failed to load config from {path}: {e}")

    # Apply environment variable overrides
    env_overrides = {
        'SEMANTIC_SCHOLAR_API_KEY': 'semantic_scholar_api_key',
        'OPENALEX_API_KEY': 'openalex_api_key',
        'DEFAULT_MAX_RESULTS': 'default_max_results',
        'DEFAULT_CITATION_STYLE': 'default_citation_style',
        'ENABLE_CACHE': 'enable_cache',
        'CACHE_DAYS': 'cache_days',
        'LOG_LEVEL': 'log_level',
    }

    for env_var, config_key in env_overrides.items():
        value = os.environ.get(env_var)
        if value is not None:
            # Convert types
            if config_key in ('enable_cache',):
                value = value.lower() in ('true', '1', 'yes')
            elif config_key in ('default_max_results', 'cache_days'):
                value = int(value)
            config[config_key] = value

    return config


def save_config(config: Dict[str, Any], config_path: str = 'config.yaml') -> bool:
    """
    Save configuration to YAML file.

    Args:
        config: Configuration dictionary.
        config_path: Path to save config.

    Returns:
        True if successful.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"Saved configuration to: {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False


class CacheManager:
    """
    Simple file-based cache manager for API responses.
    """

    def __init__(
        self,
        cache_dir: str = ".cache",
        enabled: bool = True,
        cache_days: int = 7
    ):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache files.
            enabled: Whether caching is enabled.
            cache_days: How long to keep cache entries.
        """
        self.cache_dir = cache_dir
        self.enabled = enabled
        self.cache_days = cache_days

        # Create cache directory
        if enabled:
            os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, key: str) -> str:
        """Generate a safe filename for the cache key."""
        # Create hash of the key
        hash_value = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_value}.json")

    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found/expired.
        """
        if not self.enabled:
            return None

        cache_path = self._get_cache_key(key)

        if not os.path.exists(cache_path):
            return None

        try:
            # Check if expired
            mtime = os.path.getmtime(cache_path)
            modified = datetime.fromtimestamp(mtime)
            if datetime.now() - modified > timedelta(days=self.cache_days):
                os.remove(cache_path)
                return None

            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    def set(self, key: str, value: Any) -> bool:
        """
        Set cached value.

        Args:
            key: Cache key.
            value: Value to cache.

        Returns:
            True if successful.
        """
        if not self.enabled:
            return False

        cache_path = self._get_cache_key(key)

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        if not self.enabled:
            return False

        cache_path = self._get_cache_key(key)

        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
                return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")

        return False

    def clear(self) -> int:
        """Clear all cache entries."""
        if not self.enabled or not os.path.exists(self.cache_dir):
            return 0

        count = 0
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                try:
                    os.remove(os.path.join(self.cache_dir, file))
                    count += 1
                except Exception:
                    pass

        logger.info(f"Cleared {count} cache entries")
        return count

    def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
        if not self.enabled or not os.path.exists(self.cache_dir):
            return 0

        count = 0
        now = datetime.now()

        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                try:
                    file_path = os.path.join(self.cache_dir, file)
                    mtime = os.path.getmtime(file_path)
                    modified = datetime.fromtimestamp(mtime)

                    if now - modified > timedelta(days=self.cache_days):
                        os.remove(file_path)
                        count += 1
                except Exception:
                    pass

        logger.info(f"Cleaned up {count} expired cache entries")
        return count


def handle_rate_limit(wait_time: float = 1.0, max_retries: int = 3):
    """
    Decorator to handle rate limiting.

    Args:
        wait_time: Base wait time between requests.
        max_retries: Maximum number of retries.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_str = str(e).lower()

                    # Check for rate limit indicators
                    if any(indicator in error_str for indicator in [
                        'rate limit', 'too many requests', '429',
                        'service unavailable', '503', 'retry'
                    ]):
                        wait = wait_time * (2 ** retries)  # Exponential backoff
                        logger.warning(f"Rate limited, waiting {wait:.1f}s (attempt {retries + 1}/{max_retries})")
                        time.sleep(wait)
                        retries += 1
                    else:
                        raise

            raise Exception(f"Max retries ({max_retries}) exceeded for rate limiting")

        return wrapper
    return decorator


def retry_on_failure(max_attempts: int = 3, wait_time: float = 1.0):
    """
    Decorator to retry failed operations.

    Args:
        max_attempts: Maximum number of attempts.
        wait_time: Wait time between attempts.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        wait = wait_time * (attempt + 1)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                            f"Retrying in {wait:.1f}s"
                        )
                        time.sleep(wait)

            raise last_exception

        return wrapper
    return decorator


def clean_text(text: str) -> str:
    """
    Clean and normalize text.

    Args:
        text: Input text.

    Returns:
        Cleaned text.
    """
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text


def parse_author_string(author_str: str) -> Dict[str, str]:
    """
    Parse an author name string into components.

    Args:
        author_str: Author name string.

    Returns:
        Dictionary with 'first', 'last', 'middle' keys.
    """
    result = {
        'first': '',
        'middle': '',
        'last': '',
        'original': author_str
    }

    if not author_str:
        return result

    # Try to detect format
    # Common formats:
    # - "Last, First Middle"
    # - "First Middle Last"
    # - "First M. Last"
    # - "Last, First M."

    # Check for "Last, First" format
    if ',' in author_str:
        parts = author_str.split(',', 1)
        result['last'] = parts[0].strip()
        first_parts = parts[1].split()
        if first_parts:
            result['first'] = first_parts[0]
            if len(first_parts) > 1:
                result['middle'] = ' '.join(first_parts[1:])
    else:
        parts = author_str.split()
        if len(parts) >= 2:
            result['last'] = parts[-1]
            result['first'] = parts[0]
            if len(parts) > 2:
                result['middle'] = ' '.join(parts[1:-1])

    return result


def format_author_name(
    first: str,
    last: str,
    middle: str = "",
    format: str = "last_first"
) -> str:
    """
    Format an author name.

    Args:
        first: First name.
        last: Last name.
        middle: Middle name (optional).
        format: Output format ('last_first', 'first_last', 'initials').

    Returns:
        Formatted name string.
    """
    if format == "last_first":
        parts = [last]
        if first:
            initials = first[0]
            if middle:
                initials += f" {middle[0]}"
            parts.append(f"{initials}.")
        return ' '.join(parts)

    elif format == "first_last":
        parts = [first]
        if middle:
            parts.append(middle)
        parts.append(last)
        return ' '.join(parts)

    elif format == "initials":
        initials = ""
        if first:
            initials += first[0]
        if middle:
            initials += middle[0]
        return f"{initials}. {last}"

    else:
        return f"{first} {last}"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to max length with ellipsis.

    Args:
        text: Input text.
        max_length: Maximum length.
        suffix: Suffix to add when truncating.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text

    # Truncate to max_length - suffix length
    truncated = text[:max_length - len(suffix)]

    # Try to end at a word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.5:  # Only if we're not cutting too early
        truncated = truncated[:last_space]

    return truncated + suffix


def slugify(text: str) -> str:
    """
    Convert text to URL-safe slug.

    Args:
        text: Input text.

    Returns:
        Slugified text.
    """
    # Convert to lowercase
    text = text.lower()

    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)

    # Remove non-alphanumeric characters (except hyphens)
    text = re.sub(r'[^a-z0-9\-]', '', text)

    # Remove consecutive hyphens
    text = re.sub(r'-+', '-', text)

    # Trim hyphens from start/end
    text = text.strip('-')

    return text


def format_number(num: int) -> str:
    """
    Format a number with thousand separators.

    Args:
        num: Number to format.

    Returns:
        Formatted number string.
    """
    return f"{num:,}"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted duration string.
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {int(secs)}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"


def safe_get(data: Dict, *keys, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.

    Args:
        data: Dictionary to search.
        keys: Sequence of keys to traverse.
        default: Default value if key not found.

    Returns:
        Value at nested path or default.
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split a list into chunks.

    Args:
        lst: List to chunk.
        chunk_size: Size of each chunk.

    Returns:
        List of chunks.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(*dicts: Dict, overwrite: bool = True) -> Dict:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge.
        overwrite: Whether to overwrite existing values.

    Returns:
        Merged dictionary.
    """
    result = {}
    for d in dicts:
        if d:
            for key, value in d.items():
                if key not in result or overwrite:
                    result[key] = value
    return result


class Timer:
    """Context manager for timing operations."""

    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"{self.description} completed in {format_duration(duration)}")
        return False  # Don't suppress exceptions


def print_progress_bar(
    current: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    length: int = 50,
    fill: str = "█"
) -> None:
    """
    Print a progress bar.

    Args:
        current: Current progress.
        total: Total items.
        prefix: Prefix string.
        suffix: Suffix string.
        length: Bar length in characters.
        fill: Fill character.
    """
    percent = current / total if total > 0 else 1
    filled_length = int(length * percent)
    bar = fill * filled_length + '-' * (length - filled_length)

    print(f'\r{prefix} |{bar}| {percent:.1%} {suffix}', end='', flush=True)

    if current == total:
        print()  # New line when complete


if __name__ == "__main__":
    print("Utility Helper Functions")
    print("=" * 50)
    print("Common utilities for Research Assistant:")
    print("- Logging setup")
    print("- Configuration loading")
    print("- Cache management")
    print("- Rate limiting")
    print("- Text cleaning")
    print("- Author name formatting")
