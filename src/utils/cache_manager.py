"""
Cache Manager - Handles persistent caching of analysis results.
Uses diskcache for zero-config, fast local caching across sessions.
Avoids re-processing identical files and analysis results.
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import diskcache as dc
from src.utils.logger import setup_logger

from config.settings import settings

logger = setup_logger(__name__)


class CacheError(Exception):
    """Base exception for cache errors."""

    pass


class CacheManager:
    """
    Persistent caching manager using diskcache.

    Handles:
    - File parsing results caching
    - Analysis results caching
    - TTL-based cache expiration
    - Cache statistics and management
    - Fast lookups for duplicate repos
    """

    def __init__(self):
        """Initialize cache manager."""
        self.cache_dir = settings.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_ttl_hours = settings.CACHE_TTL_HOURS
        self.cache_ttl_seconds = self.cache_ttl_hours * 3600

        try:
            self.cache = dc.Cache(str(self.cache_dir))
            logger.info(f"✓ Cache initialized at {self.cache_dir}")
            logger.info(f"  TTL: {self.cache_ttl_hours} hours")
        except Exception as e:
            logger.error(f"Failed to initialize cache: {str(e)}")
            self.cache = None

    def _make_key(self, *args) -> str:
        """
        Create a cache key from arguments.

        Args:
            *args: Arguments to use for key generation

        Returns:
            Hash-based cache key
        """
        key_string = "|".join(str(arg) for arg in args)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"cache_{key_hash}"

    def _is_expired(self, cached_item: dict) -> bool:
        """
        Check if a cached item has expired.

        Args:
            cached_item: Cached item with timestamp

        Returns:
            True if item has expired
        """
        if "timestamp" not in cached_item:
            return True

        try:
            cached_time = datetime.fromisoformat(cached_item["timestamp"])
            expiry_time = cached_time + timedelta(seconds=self.cache_ttl_seconds)
            is_expired = datetime.now() > expiry_time

            if is_expired:
                logger.debug(f"Cache item expired (cached {cached_time})")

            return is_expired
        except Exception as e:
            logger.warning(f"Error checking cache expiry: {str(e)}")
            return True

    def get(self, *key_args) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            *key_args: Arguments for cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not self.cache:
            return None

        try:
            key = self._make_key(*key_args)

            if key not in self.cache:
                logger.debug(f"Cache miss: {key}")
                return None

            cached_item = self.cache[key]

            # Check expiration
            if self._is_expired(cached_item):
                del self.cache[key]
                logger.debug(f"Cache item expired, removed: {key}")
                return None

            logger.debug(f"Cache hit: {key}")
            return cached_item.get("value")

        except Exception as e:
            logger.warning(f"Error retrieving from cache: {str(e)}")
            return None

    def set(self, value: Any, *key_args) -> bool:
        """
        Set value in cache.

        Args:
            value: Value to cache
            *key_args: Arguments for cache key

        Returns:
            True if successfully cached
        """
        if not self.cache or not settings.ENABLE_CACHING:
            return False

        try:
            key = self._make_key(*key_args)

            cached_item = {
                "value": value,
                "timestamp": datetime.now().isoformat(),
            }

            self.cache[key] = cached_item
            logger.debug(f"Cached value: {key}")
            return True

        except Exception as e:
            logger.warning(f"Error writing to cache: {str(e)}")
            return False

    def delete(self, *key_args) -> bool:
        """
        Delete specific cache entry.

        Args:
            *key_args: Arguments for cache key

        Returns:
            True if deleted, False if not found
        """
        if not self.cache:
            return False

        try:
            key = self._make_key(*key_args)

            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Deleted cache entry: {key}")
                return True

            return False

        except Exception as e:
            logger.warning(f"Error deleting from cache: {str(e)}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful
        """
        if not self.cache:
            return False

        try:
            self.cache.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Error clearing cache: {str(e)}")
            return False

    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries.

        Returns:
            Number of entries removed
        """
        if not self.cache:
            return 0

        try:
            removed = 0
            expired_keys = []

            for key in list(self.cache.keys()):
                try:
                    item = self.cache[key]
                    if self._is_expired(item):
                        expired_keys.append(key)
                except Exception:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]
                removed += 1

            logger.info(f"Removed {removed} expired cache entries")
            return removed

        except Exception as e:
            logger.error(f"Error during cache cleanup: {str(e)}")
            return 0

    def cache_file_analysis(
        self,
        repo_url: str,
        file_path: str,
        language: str,
        analysis_result: dict,
    ) -> bool:
        """
        Cache file analysis result.

        Args:
            repo_url: Repository URL
            file_path: File path in repository
            language: Programming language
            analysis_result: Analysis result to cache

        Returns:
            True if successfully cached
        """
        key_args = (f"analysis_{repo_url}_{file_path}_{language}",)
        return self.set(analysis_result, *key_args)

    def get_file_analysis(
        self,
        repo_url: str,
        file_path: str,
        language: str,
    ) -> Optional[dict]:
        """
        Retrieve cached file analysis.

        Args:
            repo_url: Repository URL
            file_path: File path in repository
            language: Programming language

        Returns:
            Cached analysis result or None
        """
        key_args = (f"analysis_{repo_url}_{file_path}_{language}",)
        return self.get(*key_args)

    def cache_repo_structure(self, repo_url: str, structure: dict) -> bool:
        """
        Cache repository structure analysis.

        Args:
            repo_url: Repository URL
            structure: Repository structure analysis

        Returns:
            True if successfully cached
        """
        return self.set(structure, f"repo_structure_{repo_url}")

    def get_repo_structure(self, repo_url: str) -> Optional[dict]:
        """
        Retrieve cached repository structure.

        Args:
            repo_url: Repository URL

        Returns:
            Cached structure or None
        """
        return self.get(f"repo_structure_{repo_url}")

    def cache_tech_detection(self, repo_url: str, tech_stack: dict) -> bool:
        """
        Cache tech stack detection result.

        Args:
            repo_url: Repository URL
            tech_stack: Detected tech stack

        Returns:
            True if successfully cached
        """
        return self.set(tech_stack, f"tech_detection_{repo_url}")

    def get_tech_detection(self, repo_url: str) -> Optional[dict]:
        """
        Retrieve cached tech stack detection.

        Args:
            repo_url: Repository URL

        Returns:
            Cached tech stack or None
        """
        return self.get(f"tech_detection_{repo_url}")

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self.cache:
            return {
                "enabled": False,
                "total_entries": 0,
                "cache_size_mb": 0,
            }

        try:
            cache_size = sum(Path(f).stat().st_size
                           for f in Path(self.cache_dir).rglob("*")
                           if f.is_file()) / 1024 / 1024

            return {
                "enabled": True,
                "total_entries": len(self.cache),
                "cache_size_mb": round(cache_size, 2),
                "cache_dir": str(self.cache_dir),
                "ttl_hours": self.cache_ttl_hours,
            }

        except Exception as e:
            logger.warning(f"Error getting cache stats: {str(e)}")
            return {
                "enabled": True,
                "total_entries": len(self.cache),
                "cache_size_mb": 0,
            }

    def close(self) -> None:
        """Close cache connection (cleanup)."""
        if self.cache:
            self.cache.close()
            logger.debug("Cache connection closed")


# Global cache manager instance
cache_manager = CacheManager()
