"""Unit tests for GitHub service."""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.services.github_service import GitHubService, GitHubServiceError


@pytest.fixture
def service():
    """Create service instance."""
    return GitHubService()


class TestGitHubService:
    """Test cases for GitHubService."""

    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, 'clone_repository')
        assert hasattr(service, 'parse_github_url')

    def test_parse_github_url_https(self, service):
        """Test parsing HTTPS GitHub URL."""
        url = 'https://github.com/owner/repo'
        owner, repo = service.parse_github_url(url)

        assert owner == 'owner'
        assert repo == 'repo'

    def test_parse_github_url_https_git(self, service):
        """Test parsing HTTPS GitHub URL with .git suffix."""
        url = 'https://github.com/owner/repo.git'
        owner, repo = service.parse_github_url(url)

        assert owner == 'owner'
        assert repo == 'repo'

    def test_parse_github_url_ssh(self, service):
        """Test parsing SSH GitHub URL."""
        url = 'git@github.com:owner/repo.git'
        owner, repo = service.parse_github_url(url)

        assert owner == 'owner'
        assert repo == 'repo'

    def test_parse_github_url_short(self, service):
        """Test parsing short format GitHub URL."""
        url = 'owner/repo'
        owner, repo = service.parse_github_url(url)

        assert owner == 'owner'
        assert repo == 'repo'

    def test_parse_github_url_invalid(self, service):
        """Test parsing invalid GitHub URL."""
        url = 'invalid-url'

        with pytest.raises(GitHubServiceError):
            service.parse_github_url(url)

    def test_get_clone_url_https(self, service):
        """Test getting HTTPS clone URL."""
        url = service.get_clone_url('owner', 'repo', 'https')

        assert 'https://github.com/owner/repo' in url

    def test_get_clone_url_ssh(self, service):
        """Test getting SSH clone URL."""
        url = service.get_clone_url('owner', 'repo', 'ssh')

        assert 'git@github.com:owner/repo' in url

    def test_validate_url_valid(self, service):
        """Test validating valid GitHub URL."""
        url = 'https://github.com/owner/repo'
        is_valid, error = service.validate_url(url)

        assert is_valid is True
        assert error is None

    def test_validate_url_invalid(self, service):
        """Test validating invalid URL."""
        url = 'not-a-github-url'
        is_valid, error = service.validate_url(url)

        assert is_valid is False
        assert error is not None

    @patch('src.services.github_service.os.path.exists')
    def test_repository_exists(self, mock_exists, service):
        """Test checking if repository path exists."""
        mock_exists.return_value = True
        exists = service.repository_exists('/path/to/repo')

        assert exists is True
        mock_exists.assert_called_once()

    def test_get_clone_path(self, service):
        """Test getting clone path."""
        path = service.get_clone_path('owner', 'repo')

        assert 'owner' in path
        assert 'repo' in path
        assert path.endswith('owner_repo')

    @patch('src.services.github_service.GitPython')
    def test_clone_repository_success(self, mock_git, service, tmp_path):
        """Test successful repository cloning."""
        # Mock successful clone
        mock_git.Repo.clone_from = Mock()

        clone_path = str(tmp_path / 'test_repo')
        service.clone_repository('https://github.com/owner/repo', clone_path)

        # Verify clone was called
        assert mock_git.Repo.clone_from.called

    def test_read_file_content(self, service, tmp_path):
        """Test reading file content."""
        # Create test file
        test_file = tmp_path / 'test.py'
        content = 'print("Hello, World!")'
        test_file.write_text(content)

        read_content = service.read_file(str(test_file))

        assert read_content == content

    def test_list_files_in_directory(self, service, tmp_path):
        """Test listing files in directory."""
        # Create test files
        (tmp_path / 'file1.py').touch()
        (tmp_path / 'file2.py').touch()
        (tmp_path / 'subdir').mkdir()
        (tmp_path / 'subdir' / 'file3.py').touch()

        files = service.list_files(str(tmp_path), pattern='*.py')

        assert len(files) >= 2

    @patch('src.services.github_service.requests.get')
    def test_validate_repository_exists(self, mock_get, service):
        """Test validating repository exists via API."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 123}
        mock_get.return_value = mock_response

        is_valid, error = service.validate_repository('https://github.com/owner/repo')

        assert is_valid is True

    @patch('src.services.github_service.requests.get')
    def test_validate_repository_not_found(self, mock_get, service):
        """Test validating non-existent repository."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        is_valid, error = service.validate_repository('https://github.com/owner/nonexistent')

        assert is_valid is False
        assert error is not None

    def test_get_repository_url_components(self, service):
        """Test getting repository URL components."""
        url = 'https://github.com/anthropics/claude-code'
        owner, repo = service.parse_github_url(url)

        assert owner == 'anthropics'
        assert repo == 'claude-code'
