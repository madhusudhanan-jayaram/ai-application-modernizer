"""File and output helpers for the GitHub modernizer MVP."""

import os
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


DOC_FILENAMES = [
    "EXECUTIVE_SUMMARY.md",
    "BUSINESS_REQUIREMENTS.md",
    "FUNCTIONAL_OVERVIEW.md",
    "NON_FUNCTIONAL_REQUIREMENTS.md",
    "CURRENT_ARCHITECTURE.md",
    "TARGET_ARCHITECTURE.md",
    "API_CONTRACTS.md",
    "RISKS_AND_ASSUMPTIONS.md",
    "MIGRATION_PLAN.md",
]


# Directories that are typically large or not relevant for high-level analysis
_SKIP_DIR_NAMES = {
    ".git",
    ".github",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "target",
    "out",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
}


def ensure_output_dirs(base_dir: Path) -> Dict[str, Path]:
    """Ensure the standard /output layout exists and return paths.

    Structure:
    - base_dir/
      - docs/
      - artifacts/
    """

    docs_dir = base_dir / "docs"
    code_dir = base_dir / "artifacts"

    docs_dir.mkdir(parents=True, exist_ok=True)
    code_dir.mkdir(parents=True, exist_ok=True)

    return {"root": base_dir, "docs": docs_dir, "artifacts": code_dir}


def build_file_tree(repo_path: Path, max_depth: int = 6, max_files: int = 800) -> List[str]:
    """Return a simple list of relative file paths in the repo.

    Large or deeply nested repositories are truncated using `max_depth`
    to avoid overwhelming the context window.
    """

    repo_path = repo_path.resolve()
    files: List[str] = []

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(repo_path)

        # Skip files under large or irrelevant directories like .git or node_modules
        if any(part in _SKIP_DIR_NAMES for part in rel.parts):
            continue

        if len(rel.parts) <= max_depth:
            files.append(str(rel))

        if len(files) >= max_files:
            break

    return sorted(files)


def find_key_artifacts(repo_path: Path) -> Dict[str, List[Path]]:
    """Find key project artifacts such as READMEs and build files."""

    repo_path = repo_path.resolve()

    readmes: List[Path] = []
    build_files: List[Path] = []
    configs: List[Path] = []
    entrypoints: List[Path] = []

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(repo_path)

        # Skip large or irrelevant directories
        if any(part in _SKIP_DIR_NAMES for part in rel.parts):
            continue

        name = path.name.lower()

        if name.startswith("readme"):
            readmes.append(path)
        if name in {"pom.xml", "build.gradle", "package.json", "requirements.txt"}:
            build_files.append(path)
        if name in {"application.yml", "application.yaml", "application.properties", "docker-compose.yml", "docker-compose.yaml", "dockerfile"}:
            configs.append(path)
        if name in {"app.py", "main.py", "server.js", "index.js", "index.ts"}:
            entrypoints.append(path)

    return {
        "readmes": readmes,
        "build_files": build_files,
        "configs": configs,
        "entrypoints": entrypoints,
    }


def read_text_file(path: Path, max_bytes: int = 16_000) -> str:
    """Read a text file safely, truncating very large files."""

    data = path.read_bytes()
    if len(data) > max_bytes:
        data = data[:max_bytes]
    return data.decode("utf-8", errors="replace")


def write_markdown_doc(docs_dir: Path, name: str, content: str) -> Path:
    """Write a markdown document under the docs directory."""

    target = docs_dir / name
    target.write_text(content, encoding="utf-8")
    return target


def write_artifact_file(artifacts_dir: Path, relative_path: str, content: str) -> Path:
    """Write a code/config artifact under the artifacts directory."""

    target = artifacts_dir / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def create_output_zip(base_dir: Path, zip_path: Path) -> Path:
    """Create a ZIP archive containing everything under base_dir."""

    base_dir = base_dir.resolve()
    zip_path = zip_path.resolve()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(base_dir):
            root_path = Path(root)
            for fname in files:
                file_path = root_path / fname
                arcname = file_path.relative_to(base_dir)
                zf.write(file_path, arcname=str(arcname))

    return zip_path
