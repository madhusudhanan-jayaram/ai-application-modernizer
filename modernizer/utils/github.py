"""GitHub utility functions for cloning and validating repositories.

These helpers focus on public repositories for the MVP and rely on
GitPython for clone operations. URL validation is lightweight and avoids
any cloud LLM usage.
"""

import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from git import Repo, GitCommandError


class GitHubURLValidationError(Exception):
    """Raised when a GitHub repository URL is invalid."""


class GitCloneError(Exception):
    """Raised when cloning a repository fails."""


GITHUB_URL_RE = re.compile(
    r"^(https://github.com/[^/]+/[^/]+(?:.git)?$|git@github.com:[^/]+/[^/]+.git$|[^/]+/[^/]+$)"
)


def parse_github_url(url: str) -> Tuple[str, str]:
    """Parse a GitHub URL into (owner, repo_name).

    Supports:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    - owner/repo
    """

    raw = url.strip()

    if raw.startswith("git@github.com:"):
        owner_repo = raw.split("git@github.com:", 1)[1]
        owner_repo = owner_repo.removesuffix(".git")
    elif "github.com" in raw:
        # Strip protocol and .git suffix
        without_proto = raw.replace("https://", "").replace("http://", "")
        path_part = without_proto.split("github.com/", 1)[1]
        owner_repo = path_part.removesuffix(".git").rstrip("/")
    else:
        # Assume owner/repo
        owner_repo = raw

    owner, repo = owner_repo.split("/", 1)
    return owner, repo


def validate_github_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate that a URL looks like a GitHub repository URL.

    This does not guarantee the repo exists, but prevents obviously
    malformed inputs so we can fail fast in the UI.
    """

    raw = url.strip()
    if not raw:
        return False, "URL cannot be empty."

    if not GITHUB_URL_RE.match(raw):
        return False, "Unsupported GitHub URL format."

    try:
        parse_github_url(raw)
    except Exception as exc:  # pragma: no cover - defensive
        return False, f"Failed to parse GitHub URL: {exc}"

    return True, None


def clone_public_repo(url: str, depth: int = 1) -> Dict[str, str]:
    """Shallow-clone a public GitHub repository into a temp directory.

    Returns a dictionary with keys:
    - "repo_path": filesystem path to the cloned repo
    - "owner": GitHub owner
    - "name": repository name
    """

    is_valid, error = validate_github_url(url)
    if not is_valid:
        raise GitHubURLValidationError(error or "Invalid GitHub URL.")

    owner, name = parse_github_url(url)

    tmp_dir = Path(tempfile.mkdtemp(prefix="modernizer_repo_"))
    target_dir = tmp_dir / f"{owner}_{name}"

    try:
        Repo.clone_from(url, str(target_dir), depth=depth)
    except GitCommandError as exc:
        # Cleanup temp directory on failure
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise GitCloneError(f"Failed to clone repository: {exc}") from exc

    return {"repo_path": str(target_dir), "owner": owner, "name": name}
