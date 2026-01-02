"""Unit tests for cache manager."""

import pytest
import time
from pathlib import Path
from src.utils.cache_manager import CacheManager


@pytest.fixture
def cache(tmp_path):
    """Create cache manager instance with temporary directory."""
    return CacheManager(cache_dir=str(tmp_path / 'cache'))


class TestCacheManager:
    """Test cases for CacheManager."""

    def test_cache_initialization(self, cache):
        """Test cache initialization."""
        assert cache is not None
        assert hasattr(cache, 'set')
        assert hasattr(cache, 'get')
        assert hasattr(cache, 'delete')

    def test_set_and_get(self, cache):
        """Test setting and getting values."""
        key = 'test_key'
        value = {'data': 'test_data'}

        cache.set(key, value)
        retrieved = cache.get(key)

        assert retrieved == value

    def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key."""
        result = cache.get('nonexistent_key')

        assert result is None

    def test_delete_key(self, cache):
        """Test deleting key."""
        key = 'test_key'
        cache.set(key, 'value')

        assert cache.get(key) == 'value'

        cache.delete(key)
        assert cache.get(key) is None

    def test_set_multiple_values(self, cache):
        """Test setting multiple values."""
        data = {
            'key1': 'value1',
            'key2': {'nested': 'value'},
            'key3': [1, 2, 3],
        }

        for key, value in data.items():
            cache.set(key, value)

        for key, value in data.items():
            assert cache.get(key) == value

    def test_cache_with_complex_objects(self, cache):
        """Test caching complex objects."""
        class_instance = {
            'name': 'TestClass',
            'methods': ['method1', 'method2'],
            'properties': {'prop1': 'value1'},
        }

        cache.set('class_instance', class_instance)
        retrieved = cache.get('class_instance')

        assert retrieved == class_instance

    def test_cache_key_namespace(self, cache):
        """Test cache key namespacing."""
        repo_url = 'https://github.com/owner/repo'
        file_path = 'src/main.py'

        key1 = cache._make_key(repo_url, file_path, 'analysis')
        key2 = cache._make_key(repo_url, file_path, 'parsing')

        cache.set(key1, 'analysis_data')
        cache.set(key2, 'parsing_data')

        assert cache.get(key1) == 'analysis_data'
        assert cache.get(key2) == 'parsing_data'

    def test_cache_exists(self, cache):
        """Test checking if key exists in cache."""
        key = 'test_key'
        assert cache.exists(key) is False

        cache.set(key, 'value')
        assert cache.exists(key) is True

    def test_cache_clear(self, cache):
        """Test clearing cache."""
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        cache.clear()

        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_cache_size(self, cache):
        """Test getting cache size."""
        initial_size = cache.size()

        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        new_size = cache.size()
        assert new_size >= initial_size

    def test_cache_memory_efficiency(self, cache):
        """Test cache memory efficiency."""
        # Set large number of entries
        for i in range(100):
            cache.set(f'key_{i}', f'value_{i}' * 100)

        # Verify all are retrievable
        for i in range(100):
            assert cache.get(f'key_{i}') == f'value_{i}' * 100

    def test_cache_with_repo_analysis(self, cache):
        """Test caching repo analysis results."""
        repo_url = 'https://github.com/example/repo'
        analysis_key = f'{repo_url}:analysis'

        analysis_data = {
            'files': ['file1.py', 'file2.py'],
            'languages': ['python', 'javascript'],
            'total_lines': 5000,
        }

        cache.set(analysis_key, analysis_data)
        retrieved = cache.get(analysis_key)

        assert retrieved == analysis_data

    def test_cache_get_all_keys(self, cache):
        """Test getting all cache keys."""
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')

        keys = cache.keys()

        assert 'key1' in keys
        assert 'key2' in keys
        assert 'key3' in keys

    def test_cache_persistence(self, tmp_path):
        """Test cache persistence across instances."""
        cache_dir = str(tmp_path / 'cache')

        # First cache instance
        cache1 = CacheManager(cache_dir=cache_dir)
        cache1.set('persistent_key', 'persistent_value')

        # Second cache instance with same directory
        cache2 = CacheManager(cache_dir=cache_dir)
        retrieved = cache2.get('persistent_key')

        assert retrieved == 'persistent_value'

    def test_cache_concurrent_access(self, cache):
        """Test concurrent access to cache."""
        # Simulate concurrent reads and writes
        for i in range(10):
            cache.set(f'key_{i}', f'value_{i}')

        # Read multiple times
        for i in range(10):
            for _ in range(5):
                assert cache.get(f'key_{i}') == f'value_{i}'

        # All values should still be present
        for i in range(10):
            assert cache.exists(f'key_{i}')
