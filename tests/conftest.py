"""Pytest configuration and shared fixtures for tests."""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service."""
    mock = MagicMock()
    mock.generate_response.return_value = 'Mock response'
    mock.count_tokens.return_value = 100
    mock.get_available_models.return_value = ['qwen2.5-coder:7b']
    return mock


@pytest.fixture
def mock_github_service():
    """Create mock GitHub service."""
    mock = MagicMock()
    mock.parse_github_url.return_value = ('owner', 'repo')
    mock.validate_repository.return_value = (True, None)
    mock.clone_repository.return_value = '/tmp/repo'
    return mock


@pytest.fixture
def mock_cache_manager():
    """Create mock cache manager."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = None
    mock.exists.return_value = False
    return mock


@pytest.fixture
def temp_repository(tmp_path):
    """Create a temporary repository structure."""
    # Create standard Python project structure
    src_dir = tmp_path / 'src'
    src_dir.mkdir()

    # Create __init__.py
    (src_dir / '__init__.py').write_text('')

    # Create main module
    (src_dir / 'main.py').write_text('''
"""Main module."""

def main():
    print("Hello, World!")

if __name__ == '__main__':
    main()
''')

    # Create requirements.txt
    (tmp_path / 'requirements.txt').write_text('''
Flask==2.0.0
SQLAlchemy==1.4.0
requests==2.26.0
pytest==6.2.5
''')

    # Create README.md
    (tmp_path / 'README.md').write_text('''
# Test Repository

This is a test repository for testing purposes.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```
''')

    return tmp_path


@pytest.fixture
def test_python_code():
    """Sample Python code for testing."""
    return '''
from typing import List, Optional
import json

class User:
    """User model."""

    def __init__(self, name: str, email: str):
        """Initialize user."""
        self.name = name
        self.email = email

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {'name': self.name, 'email': self.email}


def create_user(name: str, email: str) -> User:
    """Create a new user."""
    return User(name, email)


def get_users(users: List[User]) -> List[dict]:
    """Get all users as dictionaries."""
    return [u.to_dict() for u in users]
'''


@pytest.fixture
def test_java_code():
    """Sample Java code for testing."""
    return '''
package com.example.api;

import java.util.List;

/**
 * User controller.
 */
public class UserController {
    private UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    public List<User> getUsers() {
        return userService.findAll();
    }

    public User getUser(Long id) {
        return userService.findById(id);
    }

    public User createUser(CreateUserRequest request) {
        return userService.save(request);
    }
}
'''


@pytest.fixture
def test_javascript_code():
    """Sample JavaScript code for testing."""
    return '''
/**
 * User service for API operations.
 */

class UserService {
    constructor(apiClient) {
        this.apiClient = apiClient;
    }

    async getAllUsers() {
        const response = await this.apiClient.get('/api/users');
        return response.data;
    }

    async getUserById(id) {
        const response = await this.apiClient.get(`/api/users/${id}`);
        return response.data;
    }

    async createUser(userData) {
        const response = await this.apiClient.post('/api/users', userData);
        return response.data;
    }

    async updateUser(id, userData) {
        const response = await this.apiClient.put(`/api/users/${id}`, userData);
        return response.data;
    }

    async deleteUser(id) {
        await this.apiClient.delete(`/api/users/${id}`);
    }
}

module.exports = UserService;
'''


@pytest.fixture
def test_repository_url():
    """Test GitHub repository URL."""
    return 'https://github.com/anthropics/claude-code'


@pytest.fixture
def test_target_stack():
    """Test target technology stack."""
    return 'Python 3 + FastAPI'


# Pytest plugins and options
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line('markers', 'unit: unit tests')
    config.addinivalue_line('markers', 'integration: integration tests')
    config.addinivalue_line('markers', 'e2e: end-to-end tests')
    config.addinivalue_line('markers', 'slow: slow tests')


# Pytest hooks for test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Auto-mark tests based on their location
        if 'unit' in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif 'integration' in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif 'e2e' in item.nodeid:
            item.add_marker(pytest.mark.e2e)
