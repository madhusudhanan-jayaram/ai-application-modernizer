"""
Pydantic models for technology stack representation.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Language(BaseModel):
    """Programming language information."""

    name: str = Field(..., description="Language name (e.g., 'Java', 'Python')")
    version: Optional[str] = Field(None, description="Language version")
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)",
    )


class Framework(BaseModel):
    """Web/application framework information."""

    name: str = Field(..., description="Framework name (e.g., 'Spring Boot')")
    version: Optional[str] = Field(None, description="Framework version")
    category: str = Field(
        ...,
        description="Category: web, orm, testing, auth, etc.",
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)",
    )


class Library(BaseModel):
    """Library or dependency information."""

    name: str = Field(..., description="Library name")
    version: Optional[str] = Field(None, description="Library version")
    category: str = Field(
        ...,
        description="Category: utility, testing, database, etc.",
    )


class TechStack(BaseModel):
    """Detected technology stack for a repository."""

    primary_languages: List[Language] = Field(
        default_factory=list,
        description="Primary programming languages used",
    )
    frameworks: List[Framework] = Field(
        default_factory=list,
        description="Detected frameworks",
    )
    libraries: List[Library] = Field(
        default_factory=list,
        description="Major libraries/dependencies",
    )
    database_technologies: List[str] = Field(
        default_factory=list,
        description="Database systems (SQL, NoSQL, etc.)",
    )
    architecture_style: Optional[str] = Field(
        None,
        description="Architecture style: monolith, microservices, serverless, etc.",
    )
    deployment_target: Optional[str] = Field(
        None,
        description="Deployment target: on-prem, cloud, containerized, etc.",
    )
    other_technologies: List[str] = Field(
        default_factory=list,
        description="Other technologies (build tools, CI/CD, etc.)",
    )
    overall_maturity: str = Field(
        default="unknown",
        description="Technology maturity: legacy, outdated, current, modern",
    )
    analysis_notes: Optional[str] = Field(
        None,
        description="Additional notes about tech stack",
    )


class TechStackPair(BaseModel):
    """A pair of current and target tech stacks."""

    current: TechStack = Field(..., description="Current tech stack")
    target: TechStack = Field(..., description="Target tech stack for migration")
    migration_difficulty: str = Field(
        default="medium",
        description="Estimated difficulty: easy, medium, hard",
    )
