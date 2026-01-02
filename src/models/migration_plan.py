"""
Pydantic models for migration planning and strategy.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    """Difficulty level for migration tasks."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class BreakingChange(BaseModel):
    """A breaking change between current and target tech stack."""

    area: str = Field(..., description="Area affected (e.g., 'authentication', 'database')")
    description: str = Field(..., description="Description of the breaking change")
    impact: str = Field(..., description="Impact on the application")
    mitigation: str = Field(..., description="How to handle this breaking change")
    severity: str = Field(
        default="medium",
        description="Severity: low, medium, high, critical",
    )


class MigrationPhase(BaseModel):
    """A single phase in the migration strategy."""

    phase_number: int = Field(..., description="Phase number (1, 2, 3, etc.)")
    name: str = Field(..., description="Phase name (e.g., 'Setup Infrastructure')")
    description: str = Field(..., description="Detailed description of the phase")
    tasks: List[str] = Field(
        default_factory=list,
        description="Specific tasks to complete in this phase",
    )
    estimated_effort_hours: float = Field(
        ...,
        ge=1,
        description="Estimated effort in hours",
    )
    dependencies: List[int] = Field(
        default_factory=list,
        description="Phase numbers this phase depends on",
    )
    risk_level: str = Field(
        default="medium",
        description="Risk level: low, medium, high",
    )
    notes: Optional[str] = Field(None, description="Additional notes")


class Recommendation(BaseModel):
    """A best practice recommendation for the migration."""

    title: str = Field(..., description="Recommendation title")
    category: str = Field(
        ...,
        description="Category: architecture, testing, deployment, performance, etc.",
    )
    description: str = Field(..., description="Detailed recommendation")
    priority: str = Field(
        default="medium",
        description="Priority: low, medium, high",
    )
    why: str = Field(..., description="Why this recommendation matters")
    how: str = Field(..., description="How to implement this recommendation")


class MigrationRisks(BaseModel):
    """Identified risks in the migration strategy."""

    risk: str = Field(..., description="Risk description")
    probability: str = Field(
        default="medium",
        description="Probability: low, medium, high",
    )
    impact: str = Field(
        default="medium",
        description="Impact if risk occurs: low, medium, high, critical",
    )
    mitigation: str = Field(..., description="How to mitigate this risk")


class MigrationSuccess(BaseModel):
    """Success criteria and metrics for the migration."""

    criteria: str = Field(..., description="Success criterion")
    metric: Optional[str] = Field(None, description="How to measure success")
    target_value: Optional[str] = Field(None, description="Target value or state")


class MigrationPlan(BaseModel):
    """Complete migration plan and strategy."""

    migration_title: str = Field(..., description="Title of the migration")
    from_stack: str = Field(..., description="Source tech stack (e.g., 'Java Spring Boot')")
    to_stack: str = Field(..., description="Target tech stack (e.g., 'Python FastAPI')")
    overall_difficulty: Difficulty = Field(..., description="Overall difficulty rating")
    estimated_total_effort_hours: float = Field(
        ...,
        ge=1,
        description="Total estimated effort in hours",
    )
    estimated_total_effort_weeks: Optional[float] = Field(
        None,
        description="Total estimated effort in weeks (assuming 40 hour weeks)",
    )

    # Strategy
    migration_strategy: str = Field(
        ...,
        description="High-level migration strategy description",
    )
    approach: str = Field(
        default="phased",
        description="Approach: big_bang, phased, parallel, strangler, etc.",
    )

    # Phases
    phases: List[MigrationPhase] = Field(
        default_factory=list,
        description="Ordered list of migration phases",
    )

    # Technical details
    architecture_changes: List[str] = Field(
        default_factory=list,
        description="Major architecture changes needed",
    )
    breaking_changes: List[BreakingChange] = Field(
        default_factory=list,
        description="Identified breaking changes",
    )
    data_migration_needed: bool = Field(
        default=False,
        description="Whether data migration is required",
    )
    data_migration_notes: Optional[str] = Field(
        None,
        description="Notes about data migration strategy",
    )

    # Best practices
    recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="Best practice recommendations",
    )

    # Risks
    risks: List[MigrationRisks] = Field(
        default_factory=list,
        description="Identified risks and mitigations",
    )

    # Testing
    testing_strategy: str = Field(
        default="comprehensive",
        description="Testing strategy: comprehensive, selective, minimal, etc.",
    )
    testing_phases: List[str] = Field(
        default_factory=list,
        description="When and what to test during migration",
    )

    # Success criteria
    success_criteria: List[MigrationSuccess] = Field(
        default_factory=list,
        description="Criteria and metrics for successful migration",
    )

    # Dependencies & prerequisites
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Prerequisites before migration can begin",
    )
    external_dependencies: List[str] = Field(
        default_factory=list,
        description="External systems/tools/resources needed",
    )

    # Rollback & contingency
    rollback_strategy: str = Field(
        default="maintain_parallel",
        description="Strategy if migration needs to be rolled back",
    )
    contingency_plans: List[str] = Field(
        default_factory=list,
        description="Contingency plans for identified risks",
    )

    # Resources & team
    team_skills_needed: List[str] = Field(
        default_factory=list,
        description="Skills needed in the team",
    )
    recommended_team_size: Optional[int] = Field(
        None,
        description="Recommended team size",
    )
    training_needed: List[str] = Field(
        default_factory=list,
        description="Training needed for the team",
    )

    # Timeline
    created_at: datetime = Field(default_factory=datetime.now)
    target_completion_date: Optional[str] = Field(
        None,
        description="Target completion date (ISO format)",
    )

    # General notes
    additional_notes: Optional[str] = Field(
        None,
        description="Additional notes and considerations",
    )

    # Confidence & maturity
    plan_confidence: str = Field(
        default="medium",
        description="Confidence in this plan: low, medium, high",
    )


class MigrationRoadmap(BaseModel):
    """High-level migration roadmap/timeline."""

    plan: MigrationPlan
    phase_timeline: List[dict] = Field(
        default_factory=list,
        description="Timeline for each phase",
    )
    critical_path: List[int] = Field(
        default_factory=list,
        description="Critical path phase numbers",
    )
    go_live_readiness_checklist: List[str] = Field(
        default_factory=list,
        description="Checklist for go-live readiness",
    )
