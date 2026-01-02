"""
GitHub Service - Handles repository cloning, fetching, and access.
Supports both public and private repositories (with authentication).
"""

import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from git import Repo
from git.exc import GitCommandError
from github import Github
from src.utils.logger import setup_logger

from config.settings import settings

logger = setup_logger(__name__)


class GitHubError(Exception):
    """Base exception for GitHub service errors."""

    pass


class RepositoryNotFoundError(GitHubError):
    """Raised when repository is not found."""

    pass


class CloneError(GitHubError):
    """Raised when repository cloning fails."""

    pass


class GitHubService:
    """
    Service for GitHub repository operations.

    Handles:
    - Repository cloning (public and private)
    - File reading and analysis
    - Repository metadata extraction
    - Authentication (optional, for private repos)
    """

    def __init__(self):
        """Initialize GitHub service with optional authentication."""
        self.github_token = settings.GITHUB_TOKEN
        self.repos_dir = settings.REPOS_DIR
        self.repos_dir.mkdir(parents=True, exist_ok=True)

        # Initialize GitHub client if token provided
        self.gh = None
        if self.github_token:
            try:
                self.gh = Github(self.github_token)
                self._test_github_connection()
                logger.info("✓ GitHub authenticated with personal access token")
            except Exception as e:
                logger.warning(f"GitHub authentication failed: {str(e)}")
                self.gh = None
        else:
            logger.info("GitHub service initialized (unauthenticated - public repos only)")

    def _test_github_connection(self) -> None:
        """Test GitHub API connection."""
        try:
            user = self.gh.get_user()
            logger.debug(f"GitHub user verified: {user.login}")
        except Exception as e:
            raise GitHubError(f"GitHub connection test failed: {str(e)}") from e

    def parse_github_url(self, url: str) -> Tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repo name.

        Args:
            url: GitHub repository URL

        Returns:
            Tuple of (owner, repo_name)

        Raises:
            GitHubError: If URL format is invalid
        """
        url = url.strip()

        # Handle different URL formats
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        # owner/repo

        try:
            if url.startswith("git@github.com:"):
                # git@github.com:owner/repo.git
                parts = url.replace("git@github.com:", "").replace(".git", "").split("/")
                owner, repo = parts[0], parts[1]
            elif "github.com" in url:
                # https://github.com/owner/repo or https://github.com/owner/repo.git
                parts = url.rstrip("/").replace("https://", "").replace("http://", "")
                parts = parts.replace("github.com/", "").replace(".git", "").split("/")
                owner, repo = parts[0], parts[1]
            else:
                # owner/repo format
                parts = url.split("/")
                if len(parts) == 2:
                    owner, repo = parts
                else:
                    raise ValueError("Invalid format")

            logger.debug(f"Parsed GitHub URL: owner={owner}, repo={repo}")
            return owner, repo

        except Exception as e:
            raise GitHubError(f"Invalid GitHub URL format: {url}") from e

    def validate_repository(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a repository exists and is accessible.

        Args:
            url: GitHub repository URL

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            owner, repo_name = self.parse_github_url(url)

            if self.gh:
                # Use API to validate (requires authentication)
                try:
                    repo = self.gh.get_user(owner).get_repo(repo_name)
                    logger.info(f"✓ Repository validated: {owner}/{repo_name}")
                    return True, None
                except Exception as e:
                    return False, f"Repository not found or not accessible: {str(e)}"
            else:
                # Can't validate without API access, assume valid
                logger.info(f"Repository URL format valid: {owner}/{repo_name}")
                return True, None

        except GitHubError as e:
            return False, str(e)

    def clone_repository(self, url: str, depth: Optional[int] = None) -> str:
        """
        Clone a GitHub repository to local storage.

        Args:
            url: GitHub repository URL
            depth: Optional shallow clone depth (for large repos)

        Returns:
            Local path to cloned repository

        Raises:
            GitHubError: If cloning fails
            RepositoryNotFoundError: If repository doesn't exist
        """
        try:
            owner, repo_name = self.parse_github_url(url)
            clone_path = self.repos_dir / f"{owner}_{repo_name}"

            # Remove existing clone if it exists
            if clone_path.exists():
                logger.info(f"Removing existing clone at {clone_path}")
                shutil.rmtree(clone_path)

            logger.info(f"Cloning {url} to {clone_path}")

            # Prepare git clone args
            git_args = {}
            if depth:
                git_args["depth"] = depth
                logger.info(f"Using shallow clone with depth={depth}")

            # Clone repository
            repo = Repo.clone_from(url, clone_path, **git_args)

            logger.info(f"✓ Successfully cloned repository to {clone_path}")
            return str(clone_path)

        except GitCommandError as e:
            if "not found" in str(e).lower() or "does not appear" in str(e).lower():
                raise RepositoryNotFoundError(f"Repository not found: {url}") from e
            raise CloneError(f"Failed to clone repository: {str(e)}") from e
        except Exception as e:
            raise CloneError(f"Unexpected error cloning repository: {str(e)}") from e

    def read_file(self, repo_path: str, file_path: str) -> str:
        """
        Read a file from the cloned repository.

        Args:
            repo_path: Path to cloned repository
            file_path: Relative path to file within repository

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
            GitHubError: If file cannot be read
        """
        try:
            full_path = Path(repo_path) / file_path
            full_path = full_path.resolve()

            # Security check: ensure path is within repo
            repo_root = Path(repo_path).resolve()
            if not str(full_path).startswith(str(repo_root)):
                raise GitHubError(f"Path traversal attempt detected: {file_path}")

            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            logger.debug(f"Read file: {file_path} ({len(content)} bytes)")
            return content

        except FileNotFoundError:
            raise
        except Exception as e:
            raise GitHubError(f"Error reading file {file_path}: {str(e)}") from e

    def list_files(
        self,
        repo_path: str,
        pattern: Optional[str] = None,
        max_depth: int = 10,
        exclude_dirs: Optional[List[str]] = None,
    ) -> List[str]:
        """
        List files in the cloned repository.

        Args:
            repo_path: Path to cloned repository
            pattern: Optional glob pattern to filter files
            max_depth: Maximum directory depth to traverse
            exclude_dirs: Directories to exclude (default: node_modules, __pycache__, etc.)

        Returns:
            List of relative file paths
        """
        if exclude_dirs is None:
            exclude_dirs = [
                "node_modules",
                "__pycache__",
                ".git",
                ".venv",
                "venv",
                "dist",
                "build",
                ".egg-info",
                ".pytest_cache",
                ".vscode",
                ".idea",
                "target",
                "bin",
            ]

        try:
            repo_root = Path(repo_path)
            files = []

            for file_path in repo_root.rglob("*"):
                if file_path.is_file():
                    # Check depth
                    relative_path = file_path.relative_to(repo_root)
                    if len(relative_path.parts) > max_depth:
                        continue

                    # Check excluded directories
                    if any(part in exclude_dirs for part in relative_path.parts):
                        continue

                    # Apply pattern filter
                    if pattern:
                        if not file_path.match(pattern):
                            continue

                    files.append(str(relative_path))

            logger.info(f"Found {len(files)} files in repository")
            return sorted(files)

        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise GitHubError(f"Error listing files: {str(e)}") from e

    def get_repository_metadata(self, url: str) -> dict:
        """
        Get metadata about a GitHub repository.

        Args:
            url: GitHub repository URL

        Returns:
            Dictionary with repository metadata
        """
        try:
            owner, repo_name = self.parse_github_url(url)

            metadata = {
                "owner": owner,
                "name": repo_name,
                "url": url,
                "full_name": f"{owner}/{repo_name}",
                "stars": 0,
                "forks": 0,
                "open_issues": 0,
                "language": None,
                "description": None,
                "is_public": True,
            }

            # Get additional metadata from API if available
            if self.gh:
                try:
                    repo = self.gh.get_user(owner).get_repo(repo_name)
                    metadata.update({
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "open_issues": repo.open_issues_count,
                        "language": repo.language,
                        "description": repo.description,
                        "is_public": not repo.private,
                        "created_at": repo.created_at.isoformat(),
                        "updated_at": repo.updated_at.isoformat(),
                    })
                    logger.debug(f"Retrieved metadata for {owner}/{repo_name}")
                except Exception as e:
                    logger.warning(f"Could not retrieve full metadata: {str(e)}")

            return metadata

        except Exception as e:
            logger.error(f"Error getting repository metadata: {str(e)}")
            raise GitHubError(f"Error getting metadata: {str(e)}") from e

    def cleanup_repository(self, repo_path: str) -> None:
        """
        Remove a cloned repository to free up space.

        Args:
            repo_path: Path to cloned repository to remove
        """
        try:
            repo_path = Path(repo_path)
            if repo_path.exists():
                shutil.rmtree(repo_path)
                logger.info(f"Cleaned up repository at {repo_path}")
            else:
                logger.debug(f"Repository path not found for cleanup: {repo_path}")
        except Exception as e:
            logger.error(f"Error cleaning up repository: {str(e)}")

    def get_repository_size(self, repo_path: str) -> int:
        """
        Get total size of cloned repository in bytes.

        Args:
            repo_path: Path to cloned repository

        Returns:
            Total size in bytes
        """
        try:
            repo_path = Path(repo_path)
            total_size = 0

            for file_path in repo_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size

            logger.debug(f"Repository size: {total_size / 1024 / 1024:.2f} MB")
            return total_size

        except Exception as e:
            logger.error(f"Error calculating repository size: {str(e)}")
            return 0


# Global GitHub service instance
github_service = GitHubService()
