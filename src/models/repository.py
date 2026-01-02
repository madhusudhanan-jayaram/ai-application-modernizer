"""
Pydantic models for GitHub repository metadata and analysis results.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class FileInfo(BaseModel):
    """Information about a single file in the repository."""

    path: str = Field(..., description="Relative path from repository root")
    name: str = Field(..., description="File name")
    extension: str = Field(..., description="File extension (e.g., 'py', 'java')")
    size_bytes: int = Field(..., description="File size in bytes")
    lines_of_code: Optional[int] = Field(None, description="Approximate line count")


class DependencyInfo(BaseModel):
    """Information about a project dependency."""

    name: str = Field(..., description="Dependency name")
    version: Optional[str] = Field(None, description="Dependency version")
    dependency_type: str = Field(..., description="Type: production, development, test")


class RepositoryMetadata(BaseModel):
    """Metadata about a GitHub repository."""

    url: HttpUrl = Field(..., description="Repository URL")
    owner: str = Field(..., description="Repository owner/organization")
    name: str = Field(..., description="Repository name")
    description: Optional[str] = Field(None, description="Repository description")
    clone_path: Optional[str] = Field(None, description="Local path where repo was cloned")
    analyzed_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            HttpUrl: str,
        }


class RepositoryStructure(BaseModel):
    """Overall structure of a repository."""

    metadata: RepositoryMetadata
    root_path: str = Field(..., description="Root directory path")
    total_files: int = Field(..., description="Total number of files")
    total_size_bytes: int = Field(..., description="Total size of repository in bytes")
    language_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Count of files by programming language",
    )
    files: List[FileInfo] = Field(default_factory=list, description="List of analyzed files")
    entry_points: List[str] = Field(
        default_factory=list,
        description="Identified entry point files (main, index, etc.)",
    )
    configuration_files: List[str] = Field(
        default_factory=list,
        description="Configuration files (package.json, pom.xml, requirements.txt, etc.)",
    )
    dependencies: List[DependencyInfo] = Field(
        default_factory=list,
        description="Extracted dependencies",
    )


class RepositoryAnalysis(BaseModel):
    """Complete analysis result for a repository."""

    structure: RepositoryStructure
    detected_patterns: List[str] = Field(
        default_factory=list,
        description="Architecture patterns (MVC, microservices, monolith, etc.)",
    )
    analysis_summary: Optional[str] = Field(
        None,
        description="Human-readable summary of the repository",
    )
