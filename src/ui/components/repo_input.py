"""
Repository Input Component - Streamlit component for GitHub repository input.
Provides URL validation, format parsing, and repository verification.
"""

from typing import Optional, Tuple

from src.services.github_service import github_service
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RepositoryInputError(Exception):
    """Exception for repository input errors."""

    pass


class RepositoryInput:
    """
    Component for collecting and validating GitHub repository input.

    Features:
    - URL input with multiple format support
    - URL validation and parsing
    - Repository existence verification
    - Clone path generation
    - Format detection (HTTPS, SSH, simple)
    """

    # Supported URL formats
    SUPPORTED_FORMATS = [
        "https://github.com/owner/repo",
        "https://github.com/owner/repo.git",
        "git@github.com:owner/repo.git",
        "owner/repo",
    ]

    def __init__(self):
        """Initialize repository input component."""
        logger.debug("Repository input component initialized")

    def render_streamlit(self):
        """Render repository input in Streamlit."""
        try:
            import streamlit as st

            st.subheader("📥 GitHub Repository Input")

            repo_url = st.text_input(
                "Repository URL",
                placeholder="https://github.com/owner/repo",
                help="Supported formats:\n- https://github.com/owner/repo\n- git@github.com:owner/repo\n- owner/repo",
            )

            if repo_url:
                # Validate on input
                is_valid, error = self.validate_url(repo_url)

                if is_valid:
                    st.success(f"✓ Valid format: {self._parse_url(repo_url)[0]}/{self._parse_url(repo_url)[1]}")

                    # Check accessibility
                    if st.button("Verify Repository Access"):
                        with st.spinner("Checking repository..."):
                            is_accessible, access_error = self.verify_repository(repo_url)

                            if is_accessible:
                                st.success("✓ Repository is accessible")
                            else:
                                st.error(f"✗ Repository not accessible: {access_error}")
                else:
                    st.error(f"✗ Invalid URL format: {error}")

            return repo_url

        except ImportError:
            logger.warning("Streamlit not available - using CLI mode")
            return self._get_cli_input()

    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate GitHub URL format.

        Args:
            url: GitHub repository URL

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            owner, repo = self._parse_url(url)
            return True, None

        except Exception as e:
            return False, str(e)

    def verify_repository(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Verify repository exists and is accessible.

        Args:
            url: GitHub repository URL

        Returns:
            Tuple of (is_accessible, error_message)
        """
        try:
            is_valid, error = github_service.validate_repository(url)
            return is_valid, error

        except Exception as e:
            logger.error(f"Repository verification failed: {str(e)}")
            return False, str(e)

    def _parse_url(self, url: str) -> Tuple[str, str]:
        """
        Parse GitHub URL to owner and repo.

        Args:
            url: GitHub URL

        Returns:
            Tuple of (owner, repo)

        Raises:
            RepositoryInputError: If URL cannot be parsed
        """
        try:
            return github_service.parse_github_url(url)

        except Exception as e:
            raise RepositoryInputError(f"Failed to parse URL: {str(e)}") from e

    def _get_cli_input(self) -> str:
        """Get input from CLI."""
        print("\n📥 GitHub Repository Input")
        print(f"\nSupported formats:")
        for fmt in self.SUPPORTED_FORMATS:
            print(f"  - {fmt}")

        url = input("\nEnter repository URL: ").strip()

        is_valid, error = self.validate_url(url)

        if not is_valid:
            print(f"✗ Invalid URL: {error}")
            return self._get_cli_input()

        return url

    def get_clone_path(self, repo_url: str) -> str:
        """
        Get local clone path for repository.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Local clone path
        """
        try:
            owner, repo = self._parse_url(repo_url)
            return f"data/repos/{owner}_{repo}"

        except Exception as e:
            logger.error(f"Failed to generate clone path: {str(e)}")
            raise RepositoryInputError(f"Clone path generation failed: {str(e)}") from e


# Global instance
repository_input = RepositoryInput()
