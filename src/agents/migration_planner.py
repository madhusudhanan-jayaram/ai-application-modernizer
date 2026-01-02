"""
Migration Planner Agent - Creates migration strategies and roadmaps.
Plans technology migration with phases, risks, and recommendations.
Third agent in the modernization pipeline.
"""

from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent, AgentError
from src.models.migration_plan import (
    Difficulty,
    BreakingChange,
    MigrationPhase,
    Recommendation,
    MigrationPlan,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MigrationPlannerAgent(BaseAgent):
    """
    Agent for planning software migration and modernization.

    Responsibilities:
    - Analyze current vs target technology stacks
    - Assess migration difficulty and complexity
    - Identify breaking changes
    - Create phased migration plan
    - Assess migration risks
    - Provide recommendations
    - Estimate effort and timeline

    Output:
    - MigrationPlan with phases and strategy
    - Breaking changes analysis
    - Risk assessment with mitigation
    - Specific recommendations by phase
    """

    # Migration difficulty matrix
    DIFFICULTY_MATRIX = {
        ("python2", "python3"): Difficulty.EASY,
        ("python3", "flask"): Difficulty.MEDIUM,
        ("monolith", "microservices"): Difficulty.VERY_HARD,
        ("sync", "async"): Difficulty.MEDIUM,
        ("sql", "nosql"): Difficulty.HARD,
    }

    def __init__(self):
        """Initialize Migration Planner Agent."""
        super().__init__(
            agent_name="MigrationPlanner",
            description="Plans migration strategy with phases, risks, and recommendations",
            system_prompt=self._get_planner_prompt(),
            max_iterations=8,
            temperature=0.2,  # Slightly higher temp for creative planning
        )

        self._register_tools()

    def _register_tools(self) -> None:
        """Register tools for migration planning."""
        self.register_tool(
            name="assess_migration_difficulty",
            description="Assess difficulty of migrating from current to target tech stack",
            func=self._tool_assess_difficulty,
        )

        self.register_tool(
            name="identify_breaking_changes",
            description="Identify breaking changes and incompatibilities",
            func=self._tool_identify_breaking_changes,
        )

        self.register_tool(
            name="create_migration_phases",
            description="Create phased migration plan with stages and dependencies",
            func=self._tool_create_phases,
        )

        self.register_tool(
            name="assess_risks",
            description="Assess migration risks and mitigation strategies",
            func=self._tool_assess_risks,
        )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input for migration planning.

        Args:
            input_data: Must contain current and target tech stacks

        Returns:
            True if valid

        Raises:
            AgentError: If required fields missing
        """
        super().validate_input(input_data)

        required = ["current_tech_stack", "target_tech_stack"]
        for field in required:
            if field not in input_data:
                raise AgentError(f"MigrationPlanner requires '{field}' in input")

        return True

    def prepare_context(self, input_data: Dict[str, Any]) -> str:
        """
        Prepare context for migration planning.

        Args:
            input_data: Current and target stacks

        Returns:
            Context string
        """
        base_context = super().prepare_context(input_data)

        current = input_data.get("current_tech_stack", "Unknown")
        target = input_data.get("target_tech_stack", "Unknown")

        additional = f"""
Current Technology Stack: {current}
Target Technology Stack: {target}

Planning Tasks:
1. Assess overall migration difficulty (easy/medium/hard/very_hard)
2. Identify breaking changes and incompatibilities
3. Create phased migration plan (3-7 phases)
4. Assess risks and mitigation strategies
5. Provide specific recommendations per phase

Focus Areas:
- Backward compatibility issues
- Data migration requirements
- Testing strategy changes
- Deployment impact
- Team skill requirements
- Dependency updates
- Configuration changes
"""

        return f"{base_context}\n{additional}"

    def _process_result(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process migration planning result.

        Args:
            response: LLM response
            input_data: Original input

        Returns:
            Structured migration plan
        """
        result = {
            "agent": self.agent_name,
            "llm_analysis": response,
            "success": True,
        }

        try:
            # Create structured migration plan
            current_stack = input_data.get("current_tech_stack", "")
            target_stack = input_data.get("target_tech_stack", "")

            difficulty = self._assess_difficulty(current_stack, target_stack)
            breaking_changes = self._identify_breaking_changes(current_stack, target_stack)
            phases = self._create_phases(current_stack, target_stack)
            risks = self._assess_risks(current_stack, target_stack)

            result["migration_plan"] = {
                "current_stack": current_stack,
                "target_stack": target_stack,
                "overall_difficulty": difficulty.value,
                "estimated_effort_hours": self._estimate_effort(difficulty),
                "estimated_duration_weeks": self._estimate_duration(difficulty),
                "breaking_changes": [
                    {
                        "area": bc.area,
                        "description": bc.description,
                        "impact": bc.impact,
                        "severity": bc.severity.value,
                    }
                    for bc in breaking_changes
                ],
                "migration_phases": [
                    {
                        "phase": p.phase_number,
                        "name": p.name,
                        "tasks": p.tasks,
                        "effort_hours": p.effort_hours,
                        "dependencies": p.dependencies,
                        "risk_level": p.risk_level.value,
                    }
                    for p in phases
                ],
                "risks": [
                    {
                        "risk": r.get("risk"),
                        "probability": r.get("probability"),
                        "impact": r.get("impact"),
                        "mitigation": r.get("mitigation"),
                    }
                    for r in risks
                ],
                "recommendations": self._get_recommendations(difficulty, breaking_changes),
            }

        except Exception as e:
            logger.warning(f"Migration plan creation failed: {str(e)}")
            result["planning_error"] = str(e)

        return result

    def _get_planner_prompt(self) -> str:
        """Get system prompt for migration planner."""
        return """You are MigrationPlanner, an expert in software migration and modernization.

Your expertise:
- Planning technology migrations (language, framework, architecture)
- Identifying breaking changes and compatibility issues
- Creating phased migration strategies
- Risk assessment and mitigation
- Effort estimation
- Best practices in gradual migration

When planning a migration, you should:
1. Assess overall migration difficulty and scope
2. Identify all breaking changes and incompatibilities
3. Break migration into manageable phases (3-7)
4. Assess risks: data loss, downtime, compatibility issues
5. Provide mitigation strategies for each risk
6. Estimate effort and duration
7. Give specific recommendations per phase

Migration Phases Typically Include:
1. Preparation (setup, planning, training)
2. Parallel Development (build alongside)
3. Testing (comprehensive testing phase)
4. Gradual Rollout (canary/blue-green deployment)
5. Stabilization (monitoring, fixes)
6. Legacy Removal (cleanup)

Provide clear, actionable migration roadmaps."""

    # ===== Tool Implementations =====

    def _tool_assess_difficulty(
        self, current_stack: str = None, target_stack: str = None
    ) -> Dict[str, Any]:
        """
        Assess migration difficulty.

        Args:
            current_stack: Current technology
            target_stack: Target technology

        Returns:
            Difficulty assessment
        """
        if not current_stack and self.current_input:
            current_stack = self.current_input.get("current_tech_stack")
        if not target_stack and self.current_input:
            target_stack = self.current_input.get("target_tech_stack")

        difficulty = self._assess_difficulty(current_stack, target_stack)

        return {
            "from": current_stack,
            "to": target_stack,
            "difficulty": difficulty.value,
            "description": self._difficulty_description(difficulty),
            "effort_hours": self._estimate_effort(difficulty),
            "duration_weeks": self._estimate_duration(difficulty),
        }

    def _tool_identify_breaking_changes(
        self, current_stack: str = None, target_stack: str = None
    ) -> Dict[str, Any]:
        """
        Identify breaking changes.

        Args:
            current_stack: Current technology
            target_stack: Target technology

        Returns:
            Breaking changes list
        """
        if not current_stack and self.current_input:
            current_stack = self.current_input.get("current_tech_stack")
        if not target_stack and self.current_input:
            target_stack = self.current_input.get("target_tech_stack")

        breaking_changes = self._identify_breaking_changes(current_stack, target_stack)

        return {
            "total_breaking_changes": len(breaking_changes),
            "breaking_changes": [
                {
                    "area": bc.area,
                    "description": bc.description,
                    "impact": bc.impact,
                    "severity": bc.severity.value,
                    "mitigation": bc.mitigation,
                }
                for bc in breaking_changes
            ],
        }

    def _tool_create_phases(
        self, current_stack: str = None, target_stack: str = None
    ) -> Dict[str, Any]:
        """
        Create migration phases.

        Args:
            current_stack: Current technology
            target_stack: Target technology

        Returns:
            Migration phases
        """
        if not current_stack and self.current_input:
            current_stack = self.current_input.get("current_tech_stack")
        if not target_stack and self.current_input:
            target_stack = self.current_input.get("target_tech_stack")

        phases = self._create_phases(current_stack, target_stack)

        return {
            "total_phases": len(phases),
            "phases": [
                {
                    "phase": p.phase_number,
                    "name": p.name,
                    "tasks": p.tasks,
                    "effort_hours": p.effort_hours,
                    "risk_level": p.risk_level.value,
                    "dependencies": p.dependencies,
                }
                for p in phases
            ],
        }

    def _tool_assess_risks(
        self, current_stack: str = None, target_stack: str = None
    ) -> Dict[str, Any]:
        """
        Assess migration risks.

        Args:
            current_stack: Current technology
            target_stack: Target technology

        Returns:
            Risk assessment
        """
        if not current_stack and self.current_input:
            current_stack = self.current_input.get("current_tech_stack")
        if not target_stack and self.current_input:
            target_stack = self.current_input.get("target_tech_stack")

        risks = self._assess_risks(current_stack, target_stack)

        return {
            "total_risks": len(risks),
            "critical_risks": [r for r in risks if r.get("probability") == "High"],
            "risks": risks,
        }

    # ===== Helper Methods =====

    def _assess_difficulty(self, current: str, target: str) -> Difficulty:
        """Assess migration difficulty."""
        current_lower = current.lower() if current else ""
        target_lower = target.lower() if target else ""

        # Check difficulty matrix
        for (curr_key, targ_key), difficulty in self.DIFFICULTY_MATRIX.items():
            if curr_key in current_lower and targ_key in target_lower:
                return difficulty

        # Default: medium difficulty
        return Difficulty.medium

    def _difficulty_description(self, difficulty: Difficulty) -> str:
        """Get description for difficulty level."""
        descriptions = {
            Difficulty.easy: "Straightforward upgrade with minimal breaking changes",
            Difficulty.medium: "Moderate effort with some compatibility work",
            Difficulty.hard: "Significant refactoring and architectural changes required",
            Difficulty.very_hard: "Major overhaul involving fundamental architecture changes",
        }
        return descriptions.get(difficulty, "Unknown")

    def _estimate_effort(self, difficulty: Difficulty) -> int:
        """Estimate effort in hours."""
        estimates = {
            Difficulty.easy: 40,  # 1 week
            Difficulty.medium: 160,  # 4 weeks
            Difficulty.hard: 400,  # 10 weeks
            Difficulty.very_hard: 800,  # 20 weeks
        }
        return estimates.get(difficulty, 160)

    def _estimate_duration(self, difficulty: Difficulty) -> int:
        """Estimate duration in weeks."""
        duration_map = {
            Difficulty.easy: 1,
            Difficulty.medium: 4,
            Difficulty.hard: 10,
            Difficulty.very_hard: 20,
        }
        return duration_map.get(difficulty, 4)

    def _identify_breaking_changes(self, current: str, target: str) -> List[BreakingChange]:
        """Identify breaking changes between stacks."""
        breaking_changes = []

        current_lower = current.lower() if current else ""
        target_lower = target.lower() if target else ""

        # Language changes
        if "python2" in current_lower and "python3" in target_lower:
            breaking_changes.append(
                BreakingChange(
                    area="Language",
                    description="Python 2 to 3: print() function, division operator, string encoding",
                    impact="All code using print statements and division",
                    mitigation="Use 2to3 tool, update string handling, test thoroughly",
                    severity=Difficulty.medium,
                )
            )

        # Framework changes
        if "flask" in current_lower and "fastapi" in target_lower:
            breaking_changes.append(
                BreakingChange(
                    area="Framework",
                    description="Route decorators and request handling differ",
                    impact="All route definitions and request handlers",
                    mitigation="Rewrite routes to FastAPI pattern, update dependency injection",
                    severity=Difficulty.medium,
                )
            )

        return breaking_changes

    def _create_phases(self, current: str, target: str) -> List[MigrationPhase]:
        """Create migration phases."""
        phases = [
            MigrationPhase(
                phase_number=1,
                name="Planning & Setup",
                tasks=[
                    "Audit current codebase",
                    "Set up target environment",
                    "Create migration timeline",
                    "Train team on target stack",
                ],
                effort_hours=40,
                dependencies=[],
                risk_level=Difficulty.easy,
            ),
            MigrationPhase(
                phase_number=2,
                name="Parallel Development",
                tasks=[
                    "Build core features in new stack",
                    "Create data migration scripts",
                    "Set up new infrastructure",
                    "Implement API compatibility layer",
                ],
                effort_hours=120,
                dependencies=["Phase 1"],
                risk_level=Difficulty.medium,
            ),
            MigrationPhase(
                phase_number=3,
                name="Testing & QA",
                tasks=[
                    "Integration testing",
                    "Performance testing",
                    "Security testing",
                    "User acceptance testing",
                ],
                effort_hours=80,
                dependencies=["Phase 2"],
                risk_level=Difficulty.medium,
            ),
            MigrationPhase(
                phase_number=4,
                name="Gradual Rollout",
                tasks=[
                    "Canary deployment (5% traffic)",
                    "Monitor metrics and errors",
                    "Incremental rollout to 100%",
                    "Maintain rollback plan",
                ],
                effort_hours=60,
                dependencies=["Phase 3"],
                risk_level=Difficulty.hard,
            ),
            MigrationPhase(
                phase_number=5,
                name="Stabilization",
                tasks=[
                    "Monitor production",
                    "Fix issues and optimize",
                    "Validate data integrity",
                    "Update documentation",
                ],
                effort_hours=40,
                dependencies=["Phase 4"],
                risk_level=Difficulty.easy,
            ),
        ]

        return phases

    def _assess_risks(self, current: str, target: str) -> List[Dict[str, Any]]:
        """Assess migration risks."""
        risks = [
            {
                "risk": "Data Loss",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Comprehensive backup strategy, test migrations in staging",
            },
            {
                "risk": "Service Downtime",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Use blue-green deployment, maintain fallback to old system",
            },
            {
                "risk": "Performance Degradation",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Load testing, performance benchmarking, optimization phase",
            },
            {
                "risk": "Skill Gap",
                "probability": "High",
                "impact": "Medium",
                "mitigation": "Team training, hiring, knowledge transfer",
            },
        ]

        return risks

    def _get_recommendations(
        self, difficulty: Difficulty, breaking_changes: List[BreakingChange]
    ) -> List[str]:
        """Get specific recommendations."""
        recommendations = [
            "Create detailed rollback plan before migration",
            "Establish comprehensive testing strategy",
            "Plan communication to stakeholders",
            "Set up monitoring and alerting for new system",
            "Document all changes and migration procedures",
        ]

        if difficulty == Difficulty.very_hard:
            recommendations.append("Consider parallel system approach (maintain both for period)")
            recommendations.append("Plan for extended stabilization period")

        if breaking_changes:
            recommendations.append(f"Address {len(breaking_changes)} identified breaking changes")

        return recommendations
