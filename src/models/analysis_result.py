"""
Pydantic models for complete analysis results.
Aggregates all analysis, detection, and planning into final comprehensive results.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .migration_plan import MigrationPlan, MigrationRoadmap
from .repository import RepositoryAnalysis
from .tech_stack import TechStack, TechStackPair


class AnalysisSummary(BaseModel):
    """High-level summary of the entire analysis."""

    repository_name: str = Field(..., description="Repository name")
    repository_url: str = Field(..., description="Repository URL")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_duration_seconds: float = Field(
        ...,
        ge=0,
        description="How long the analysis took",
    )

    current_tech_stack_summary: str = Field(
        ...,
        description="Brief summary of current tech stack",
    )
    target_tech_stack_summary: str = Field(
        ...,
        description="Brief summary of target tech stack",
    )
    migration_difficulty_summary: str = Field(
        ...,
        description="High-level migration difficulty assessment",
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="Top 5-10 key findings from analysis",
    )
    critical_issues: List[str] = Field(
        default_factory=list,
        description="Critical issues that must be addressed",
    )
    immediate_actions: List[str] = Field(
        default_factory=list,
        description="Immediate actions recommended",
    )


class CodeQualityMetrics(BaseModel):
    """Code quality metrics extracted during analysis."""

    total_lines_of_code: int = Field(..., description="Total LOC in repository")
    language_distribution: dict = Field(
        ...,
        description="Distribution of code by language",
    )
    files_analyzed: int = Field(..., description="Number of files analyzed")
    code_complexity_estimate: str = Field(
        default="medium",
        description="Overall code complexity: low, medium, high, very_high",
    )
    maintainability_estimate: str = Field(
        default="medium",
        description="Estimated maintainability: poor, fair, good, excellent",
    )
    technical_debt_estimate: str = Field(
        default="medium",
        description="Estimated technical debt: low, medium, high, critical",
    )
    dependencies_count: int = Field(default=0, description="Total number of dependencies")
    outdated_dependencies_count: int = Field(
        default=0,
        description="Count of outdated dependencies",
    )
    security_issues_identified: int = Field(
        default=0,
        description="Number of security issues identified",
    )


class ArchitectureAssessment(BaseModel):
    """Assessment of current and proposed architecture."""

    current_architecture_pattern: str = Field(
        ...,
        description="Current architecture pattern",
    )
    proposed_architecture_pattern: str = Field(
        ...,
        description="Proposed architecture pattern for target stack",
    )
    architecture_improvement_potential: str = Field(
        default="medium",
        description="Improvement potential: low, medium, high",
    )
    modularity_assessment: str = Field(
        ...,
        description="Assessment of code modularity",
    )
    scalability_assessment: str = Field(
        ...,
        description="Assessment of current scalability",
    )
    scalability_improvements: List[str] = Field(
        default_factory=list,
        description="Proposed scalability improvements in new stack",
    )
    security_improvements: List[str] = Field(
        default_factory=list,
        description="Security improvements in new stack",
    )
    performance_improvements: List[str] = Field(
        default_factory=list,
        description="Performance improvements in new stack",
    )


class ComplianceAndStandards(BaseModel):
    """Compliance and standards assessment."""

    current_standards_compliance: List[str] = Field(
        default_factory=list,
        description="Current standards being followed",
    )
    recommended_standards: List[str] = Field(
        default_factory=list,
        description="Standards recommended for target stack",
    )
    compliance_gaps: List[str] = Field(
        default_factory=list,
        description="Compliance gaps in current codebase",
    )
    compliance_improvements: List[str] = Field(
        default_factory=list,
        description="Compliance improvements in new stack",
    )


class LearningAndTraining(BaseModel):
    """Learning resources and training recommendations."""

    team_learning_curve: str = Field(
        default="medium",
        description="Team learning curve for new stack: low, medium, high",
    )
    recommended_training_resources: List[str] = Field(
        default_factory=list,
        description="Recommended training materials/courses",
    )
    skill_gaps: List[str] = Field(
        default_factory=list,
        description="Identified skill gaps in team",
    )
    knowledge_transfer_strategy: str = Field(
        default="documentation_and_mentoring",
        description="Strategy for knowledge transfer",
    )


class ComprehensiveAnalysisResult(BaseModel):
    """Complete, comprehensive analysis result combining all analyses."""

    # Metadata
    analysis_id: str = Field(
        ...,
        description="Unique analysis identifier",
    )
    summary: AnalysisSummary

    # Analysis components
    repository_analysis: RepositoryAnalysis = Field(
        ...,
        description="Detailed repository structure analysis",
    )
    current_tech_stack: TechStack = Field(
        ...,
        description="Detected current tech stack",
    )
    target_tech_stack: TechStack = Field(
        ...,
        description="Specified/proposed target tech stack",
    )
    tech_stack_pair: TechStackPair = Field(
        ...,
        description="Current and target stacks with migration difficulty",
    )

    # Quality and architecture
    code_quality_metrics: CodeQualityMetrics = Field(
        ...,
        description="Code quality metrics",
    )
    architecture_assessment: ArchitectureAssessment = Field(
        ...,
        description="Current and proposed architecture assessment",
    )

    # Planning
    migration_plan: MigrationPlan = Field(
        ...,
        description="Detailed migration plan and strategy",
    )
    migration_roadmap: MigrationRoadmap = Field(
        ...,
        description="Migration roadmap with timeline",
    )

    # Standards and compliance
    compliance_assessment: ComplianceAndStandards = Field(
        ...,
        description="Compliance and standards assessment",
    )

    # Learning
    learning_recommendations: LearningAndTraining = Field(
        ...,
        description="Learning resources and training recommendations",
    )

    # Success metrics
    success_definition: List[str] = Field(
        default_factory=list,
        description="How success will be measured",
    )

    # Executive summary
    executive_summary: Optional[str] = Field(
        None,
        description="Executive-level summary suitable for leadership",
    )

    # Risk summary
    top_risks: List[str] = Field(
        default_factory=list,
        description="Top 3-5 risks identified in migration",
    )

    # Assumptions
    assumptions_made: List[str] = Field(
        default_factory=list,
        description="Assumptions made during analysis",
    )

    # Limitations
    analysis_limitations: List[str] = Field(
        default_factory=list,
        description="Limitations of this analysis",
    )

    # Next steps
    recommended_next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next steps after analysis",
    )

    # Metadata
    analysis_performed_by: Optional[str] = Field(
        None,
        description="Who/what performed the analysis",
    )
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    confidence_level: str = Field(
        default="medium",
        description="Overall confidence in this analysis: low, medium, high",
    )


class AnalysisResultSummaryForExport(BaseModel):
    """Simplified summary version of analysis for export/sharing."""

    repository_name: str
    repository_url: str
    current_stack: str
    target_stack: str
    migration_difficulty: str
    estimated_effort_weeks: float
    key_findings: List[str]
    critical_issues: List[str]
    immediate_actions: List[str]
    success_criteria: List[str]
    top_risks: List[str]
    recommended_next_steps: List[str]
    analysis_timestamp: datetime


class BatchAnalysisResults(BaseModel):
    """Results from analyzing multiple repositories."""

    batch_id: str = Field(..., description="Unique batch identifier")
    total_repositories: int = Field(..., description="Total repositories analyzed")
    successful_analyses: int = Field(..., description="Number of successful analyses")
    failed_analyses: int = Field(..., description="Number of failed analyses")
    results: List[ComprehensiveAnalysisResult] = Field(
        default_factory=list,
        description="Individual analysis results",
    )
    errors: List[dict] = Field(
        default_factory=list,
        description="Errors encountered",
    )
    batch_summary: Optional[str] = Field(
        None,
        description="Summary of batch analysis",
    )
    batch_timestamp: datetime = Field(default_factory=datetime.now)
