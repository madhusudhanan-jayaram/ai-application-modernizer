"""
Migration Chain - Orchestrates migration strategy and code generation.
Coordinates: MigrationPlanner → CodeGenerator
Produces migration strategy with modernized code samples.
"""

from typing import Any, Dict, List

from src.agents.migration_planner import MigrationPlannerAgent
from src.agents.code_generator import CodeGeneratorAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MigrationChainError(Exception):
    """Exception for migration chain errors."""

    pass


class MigrationChain:
    """
    Chain for planning migration and generating modernized code.

    Workflow:
    1. MigrationPlanner: Create strategy, phases, identify breaking changes
    2. CodeGenerator: Generate modernized code samples for target stack

    Input:
    - current_tech_stack: Current technology (e.g., "Python 2 + Flask")
    - target_tech_stack: Target technology (e.g., "Python 3 + FastAPI")
    - analysis_result: (Optional) Results from analysis chain

    Output:
    - MigrationPlan with phases and risks
    - Generated code samples
    - Code transformation examples
    - Configuration templates
    """

    def __init__(self):
        """Initialize migration chain."""
        self.migration_planner = MigrationPlannerAgent()
        self.code_generator = CodeGeneratorAgent()

        self.execution_history = []

        logger.info("✓ Migration chain initialized")

    def run(
        self,
        current_tech_stack: str,
        target_tech_stack: str,
        analysis_result: Dict[str, Any] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute migration chain.

        Args:
            current_tech_stack: Current technology stack
            target_tech_stack: Target technology stack
            analysis_result: Results from analysis chain (optional)
            use_cache: Whether to use cached results

        Returns:
            Complete migration plan with generated code
        """
        logger.info(
            f"[MigrationChain] Starting migration from {current_tech_stack} to {target_tech_stack}"
        )

        try:
            # ===== Step 1: Migration Planning =====
            logger.info("[MigrationChain] Step 1: Planning migration strategy")

            migration_input = {
                "current_tech_stack": current_tech_stack,
                "target_tech_stack": target_tech_stack,
                "analysis_result": analysis_result,
                "task": "Plan migration strategy with phases, risks, and recommendations",
                "context": f"Create detailed migration roadmap from {current_tech_stack} to {target_tech_stack}",
            }

            migration_plan = self.migration_planner.execute(migration_input, use_cache=use_cache)

            logger.info("[MigrationChain] Migration plan created")
            logger.debug(
                f"Plan details: {migration_plan.get('migration_plan', {}).get('overall_difficulty')}"
            )

            # ===== Step 2: Code Generation =====
            logger.info("[MigrationChain] Step 2: Generating modernized code")

            code_generation_input = {
                "target_tech_stack": target_tech_stack,
                "current_tech_stack": current_tech_stack,
                "migration_plan": migration_plan.get("migration_plan"),  # Pass migration plan
                "task": "Generate modernized code samples for target technology stack",
                "context": f"Create working code examples for {target_tech_stack} to guide migration",
            }

            generated_code = self.code_generator.execute(
                code_generation_input, use_cache=use_cache
            )

            logger.info("[MigrationChain] Code generation complete")
            logger.debug(f"Generated files: {len(generated_code.get('generated_files', []))}")

            # ===== Compile Results =====
            result = self._compile_migration_result(
                current_tech_stack,
                target_tech_stack,
                migration_plan,
                generated_code,
                analysis_result,
            )

            # Log execution
            self.execution_history.append(
                {
                    "current_stack": current_tech_stack,
                    "target_stack": target_tech_stack,
                    "success": True,
                    "steps": ["Migration Planning", "Code Generation"],
                    "result": result,
                }
            )

            logger.info(
                f"[MigrationChain] ✓ Migration chain complete: "
                f"{current_tech_stack} → {target_tech_stack}"
            )
            return result

        except Exception as e:
            logger.error(f"[MigrationChain] Migration failed: {str(e)}")

            self.execution_history.append(
                {
                    "current_stack": current_tech_stack,
                    "target_stack": target_tech_stack,
                    "success": False,
                    "error": str(e),
                }
            )

            raise MigrationChainError(f"Migration chain failed: {str(e)}") from e

    def _compile_migration_result(
        self,
        current_stack: str,
        target_stack: str,
        migration_plan: Dict[str, Any],
        generated_code: Dict[str, Any],
        analysis_result: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Compile migration results from both agents.

        Args:
            current_stack: Current technology
            target_stack: Target technology
            migration_plan: Results from MigrationPlanner
            generated_code: Results from CodeGenerator
            analysis_result: Optional analysis results

        Returns:
            Compiled migration result
        """
        plan_data = migration_plan.get("migration_plan", {})

        return {
            "migration_type": "Technology Stack Migration",
            "current_tech_stack": current_stack,
            "target_tech_stack": target_stack,
            "status": "complete",
            # ===== Migration Strategy =====
            "migration_strategy": {
                "overall_difficulty": plan_data.get("overall_difficulty", "unknown"),
                "estimated_effort_hours": plan_data.get("estimated_effort_hours", 0),
                "estimated_duration_weeks": plan_data.get("estimated_duration_weeks", 0),
                "total_phases": len(plan_data.get("migration_phases", [])),
                "breaking_changes_count": len(plan_data.get("breaking_changes", [])),
            },
            # ===== Detailed Phases =====
            "migration_phases": plan_data.get("migration_phases", []),
            # ===== Breaking Changes =====
            "breaking_changes": plan_data.get("breaking_changes", []),
            # ===== Risk Assessment =====
            "risks": {
                "total_identified": len(plan_data.get("risks", [])),
                "risk_details": plan_data.get("risks", []),
            },
            # ===== Recommendations =====
            "recommendations": plan_data.get("recommendations", []),
            # ===== Generated Code =====
            "generated_code": {
                "files_generated": generated_code.get("generated_files", []),
                "target_framework": self._detect_target_framework(target_stack),
                "code_templates": self._extract_code_templates(generated_code),
            },
            # ===== Agent Insights =====
            "planner_insight": migration_plan.get("llm_analysis", ""),
            "generator_insight": generated_code.get("llm_analysis", ""),
            # ===== Summary =====
            "summary": self._create_migration_summary(
                current_stack, target_stack, plan_data, generated_code
            ),
        }

    def _detect_target_framework(self, target_stack: str) -> str:
        """Detect primary framework from target stack."""
        target_lower = target_stack.lower()

        if "fastapi" in target_lower:
            return "FastAPI"
        elif "flask" in target_lower:
            return "Flask"
        elif "django" in target_lower:
            return "Django"
        elif "spring" in target_lower:
            return "Spring Boot"
        elif "react" in target_lower:
            return "React"
        elif "vue" in target_lower:
            return "Vue.js"
        elif "angular" in target_lower:
            return "Angular"
        else:
            return "Custom"

    def _extract_code_templates(self, generated_code: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract code templates from generation result."""
        templates = []

        # This would extract actual templates if generated by LLM
        # For now, return list of file types that should be generated
        file_list = generated_code.get("generated_files", [])

        for file_path in file_list:
            templates.append(
                {
                    "file": file_path,
                    "type": self._infer_file_type(file_path),
                    "status": "generated",
                }
            )

        return templates

    def _infer_file_type(self, file_path: str) -> str:
        """Infer file type from path."""
        if "model" in file_path.lower():
            return "data_model"
        elif "controller" in file_path.lower() or "route" in file_path.lower():
            return "api_endpoint"
        elif "service" in file_path.lower():
            return "service_logic"
        elif "config" in file_path.lower():
            return "configuration"
        elif "docker" in file_path.lower():
            return "deployment"
        elif "test" in file_path.lower():
            return "test_code"
        else:
            return "other"

    def _create_migration_summary(
        self,
        current_stack: str,
        target_stack: str,
        plan_data: Dict[str, Any],
        generated_code: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create executive summary of migration.

        Args:
            current_stack: Current technology
            target_stack: Target technology
            plan_data: Migration plan data
            generated_code: Generated code data

        Returns:
            Summary dictionary
        """
        difficulty = plan_data.get("overall_difficulty", "medium")
        effort = plan_data.get("estimated_effort_hours", 160)
        duration = plan_data.get("estimated_duration_weeks", 4)
        phases = len(plan_data.get("migration_phases", []))
        breaking_changes = len(plan_data.get("breaking_changes", []))
        files_generated = len(generated_code.get("generated_files", []))

        difficulty_emoji = {
            "easy": "✓ Easy",
            "medium": "⚠ Moderate",
            "hard": "⚠⚠ Challenging",
            "very_hard": "⚠⚠⚠ Very Challenging",
        }.get(difficulty, "Unknown")

        return {
            "from": current_stack,
            "to": target_stack,
            "difficulty": difficulty_emoji,
            "effort_estimate": f"{effort} hours (~{duration} weeks)",
            "migration_phases": phases,
            "breaking_changes": breaking_changes,
            "code_files_generated": files_generated,
            "migration_approach": self._suggest_approach(difficulty),
            "key_success_factors": [
                "Comprehensive testing at each phase",
                "Clear communication with stakeholders",
                "Parallel development alongside legacy system",
                "Automated schema/data migrations",
                "Robust monitoring and alerting",
                "Prepared rollback plan",
            ],
        }

    def _suggest_approach(self, difficulty: str) -> str:
        """Suggest migration approach based on difficulty."""
        suggestions = {
            "easy": "Big-bang migration possible, plan thorough testing",
            "medium": "Phased migration recommended, parallel deployment strategy",
            "hard": "Definitely phased, consider feature flags for gradual rollout",
            "very_hard": "Extended parallel running, feature flags essential, gradual cutover",
        }
        return suggestions.get(difficulty, "Phased approach with thorough planning required")

    def get_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_history

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history = []

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"MigrationChain("
            f"stages=[MigrationPlanner, CodeGenerator], "
            f"executions={len(self.execution_history)})"
        )


# Global migration chain instance
migration_chain = MigrationChain()
