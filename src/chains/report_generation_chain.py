"""
Report Generation Chain - Orchestrates comprehensive report generation.
Coordinates: DocumentationGenerator → Report Assembly
Produces final comprehensive report with all analysis and migration data.
"""

from typing import Any, Dict, List
from datetime import datetime

from src.agents.documentation_generator import DocumentationGeneratorAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ReportGenerationChainError(Exception):
    """Exception for report generation chain errors."""

    pass


class ReportGenerationChain:
    """
    Chain for generating comprehensive modernization reports.

    Workflow:
    1. DocumentationGenerator: Generate guides, API docs, troubleshooting
    2. Report Assembly: Compile all results into unified report

    Input:
    - analysis_result: Results from analysis chain
    - migration_result: Results from migration chain
    - (Optional) generated_code: Code generation results

    Output:
    - Comprehensive markdown report
    - Code file list with locations
    - Executive summary
    - Migration roadmap
    - Technical documentation
    """

    def __init__(self):
        """Initialize report generation chain."""
        self.docs_generator = DocumentationGeneratorAgent()

        self.execution_history = []

        logger.info("✓ Report generation chain initialized")

    def run(
        self,
        analysis_result: Dict[str, Any] = None,
        migration_result: Dict[str, Any] = None,
        repo_url: str = "unknown",
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute report generation chain.

        Args:
            analysis_result: Results from analysis chain
            migration_result: Results from migration chain
            repo_url: Repository URL
            use_cache: Whether to use cached results

        Returns:
            Complete modernization report
        """
        logger.info(f"[ReportChain] Starting report generation for {repo_url}")

        try:
            # Extract key data
            current_stack = migration_result.get("current_tech_stack", "Unknown") if migration_result else "Unknown"
            target_stack = migration_result.get("target_tech_stack", "Unknown") if migration_result else "Unknown"

            # ===== Step 1: Documentation Generation =====
            logger.info("[ReportChain] Step 1: Generating comprehensive documentation")

            docs_input = {
                "current_tech_stack": current_stack,
                "target_tech_stack": target_stack,
                "migration_plan": migration_result.get("migration_strategy") if migration_result else None,
                "analysis_result": analysis_result,
                "code_changes": migration_result.get("generated_code") if migration_result else None,
                "task": "Generate comprehensive migration documentation and guides",
                "context": f"Create complete documentation for {current_stack} → {target_stack} migration",
            }

            generated_docs = self.docs_generator.execute(docs_input, use_cache=use_cache)

            logger.info("[ReportChain] Documentation generated")

            # ===== Step 2: Report Assembly =====
            logger.info("[ReportChain] Step 2: Assembling comprehensive report")

            report = self._assemble_report(
                repo_url,
                analysis_result,
                migration_result,
                generated_docs,
            )

            # Log execution
            self.execution_history.append(
                {
                    "repo_url": repo_url,
                    "success": True,
                    "steps": ["Documentation Generation", "Report Assembly"],
                    "report_sections": len(report.get("sections", [])),
                }
            )

            logger.info(f"[ReportChain] ✓ Report generation complete for {repo_url}")
            return report

        except Exception as e:
            logger.error(f"[ReportChain] Report generation failed: {str(e)}")

            self.execution_history.append(
                {
                    "repo_url": repo_url,
                    "success": False,
                    "error": str(e),
                }
            )

            raise ReportGenerationChainError(
                f"Report generation failed: {str(e)}"
            ) from e

    def _assemble_report(
        self,
        repo_url: str,
        analysis_result: Dict[str, Any],
        migration_result: Dict[str, Any],
        generated_docs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assemble comprehensive report from all sources.

        Args:
            repo_url: Repository URL
            analysis_result: Analysis chain results
            migration_result: Migration chain results
            generated_docs: Generated documentation

        Returns:
            Comprehensive report
        """
        report = {
            "report_type": "LLM-Powered Modernization Report",
            "repository_url": repo_url,
            "generated_at": datetime.now().isoformat(),
            "status": "complete",
            # ===== Executive Summary =====
            "executive_summary": self._create_executive_summary(
                analysis_result, migration_result
            ),
            # ===== Sections =====
            "sections": [],
        }

        # Add sections in order
        sections = []

        # 1. Repository Analysis
        if analysis_result:
            sections.append(
                {
                    "title": "1. Repository Analysis",
                    "content": self._format_analysis_section(analysis_result),
                }
            )

        # 2. Current Technology Stack
        if analysis_result:
            sections.append(
                {
                    "title": "2. Current Technology Stack",
                    "content": self._format_tech_stack_section(analysis_result),
                }
            )

        # 3. Migration Strategy
        if migration_result:
            sections.append(
                {
                    "title": "3. Migration Strategy & Roadmap",
                    "content": self._format_migration_strategy_section(migration_result),
                }
            )

        # 4. Breaking Changes
        if migration_result and migration_result.get("breaking_changes"):
            sections.append(
                {
                    "title": "4. Breaking Changes & Solutions",
                    "content": self._format_breaking_changes_section(
                        migration_result.get("breaking_changes", [])
                    ),
                }
            )

        # 5. Migration Phases
        if migration_result and migration_result.get("migration_phases"):
            sections.append(
                {
                    "title": "5. Detailed Migration Phases",
                    "content": self._format_phases_section(
                        migration_result.get("migration_phases", [])
                    ),
                }
            )

        # 6. Generated Code Samples
        if migration_result and migration_result.get("generated_code"):
            sections.append(
                {
                    "title": "6. Generated Code Samples",
                    "content": self._format_code_section(
                        migration_result.get("generated_code", {})
                    ),
                }
            )

        # 7. Risk Assessment
        if migration_result and migration_result.get("risks"):
            sections.append(
                {
                    "title": "7. Risk Assessment & Mitigation",
                    "content": self._format_risks_section(migration_result.get("risks", {})),
                }
            )

        # 8. Migration Documentation
        doc_content = generated_docs.get("generated_documentation", {})
        if doc_content:
            sections.append(
                {
                    "title": "8. Migration Guide",
                    "content": doc_content.get("migration_guide", {}).get("content", ""),
                }
            )

            sections.append(
                {
                    "title": "9. API Documentation",
                    "content": doc_content.get("api_docs", {}).get("content", ""),
                }
            )

            sections.append(
                {
                    "title": "10. Troubleshooting Guide",
                    "content": doc_content.get("troubleshooting", {}).get("content", ""),
                }
            )

        # 9. Recommendations
        if migration_result and migration_result.get("recommendations"):
            sections.append(
                {
                    "title": "11. Key Recommendations",
                    "content": self._format_recommendations_section(
                        migration_result.get("recommendations", [])
                    ),
                }
            )

        report["sections"] = sections

        # Add file manifest
        report["generated_files"] = self._create_file_manifest(
            migration_result, generated_docs
        )

        # Add document list
        report["documentation_files"] = self._create_documentation_list(generated_docs)

        return report

    def _create_executive_summary(
        self,
        analysis_result: Dict[str, Any],
        migration_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create executive summary."""
        return {
            "overview": "Comprehensive analysis and modernization roadmap",
            "repository": analysis_result.get("repository_url") if analysis_result else "Unknown",
            "current_stack": migration_result.get("current_tech_stack") if migration_result else "Unknown",
            "target_stack": migration_result.get("target_tech_stack") if migration_result else "Unknown",
            "difficulty": (
                migration_result.get("migration_strategy", {}).get("overall_difficulty", "Unknown")
                if migration_result
                else "Unknown"
            ),
            "effort": (
                f"{migration_result.get('migration_strategy', {}).get('estimated_effort_hours', 0)} hours"
                if migration_result
                else "Unknown"
            ),
            "duration": (
                f"{migration_result.get('migration_strategy', {}).get('estimated_duration_weeks', 0)} weeks"
                if migration_result
                else "Unknown"
            ),
            "next_steps": [
                "Review this modernization report",
                "Validate technology stack recommendations",
                "Plan migration phases with team",
                "Set up development environment",
                "Begin phased migration",
            ],
        }

    def _format_analysis_section(self, analysis_result: Dict[str, Any]) -> str:
        """Format repository analysis section."""
        repo_analysis = analysis_result.get("repository_analysis", {})

        return f"""
## Repository Structure & Metrics

### Overview
- **Total Files**: {repo_analysis.get('total_files', 0)}
- **Analyzed Files**: {repo_analysis.get('analyzed_files', 0)}
- **Primary Language**: {repo_analysis.get('primary_language', 'Unknown')}

### Code Quality
{self._format_metrics(repo_analysis.get('metrics', {}))}

### Architecture
{self._format_architecture(repo_analysis.get('structure', {}))}
"""

    def _format_tech_stack_section(self, analysis_result: Dict[str, Any]) -> str:
        """Format technology stack section."""
        tech_stack = analysis_result.get("technology_stack", {})

        languages = tech_stack.get("languages", [])
        frameworks = tech_stack.get("frameworks", [])

        content = "## Detected Technology Stack\n\n"

        if languages:
            content += "### Languages\n"
            for lang in languages:
                content += f"- {lang.get('language', 'Unknown')} (v{lang.get('version', 'Unknown')})\n"

        if frameworks:
            content += "\n### Frameworks\n"
            for fw in frameworks:
                content += f"- {fw.get('name', 'Unknown')} ({fw.get('category', 'Unknown')})\n"

        content += f"\n### Maturity\n{tech_stack.get('maturity', 'Unknown')}\n"

        return content

    def _format_migration_strategy_section(self, migration_result: Dict[str, Any]) -> str:
        """Format migration strategy section."""
        strategy = migration_result.get("migration_strategy", {})

        return f"""
## Migration Overview

- **Difficulty**: {strategy.get('overall_difficulty', 'Unknown')}
- **Estimated Effort**: {strategy.get('estimated_effort_hours', 0)} hours
- **Estimated Duration**: {strategy.get('estimated_duration_weeks', 0)} weeks
- **Migration Phases**: {strategy.get('total_phases', 0)}
- **Breaking Changes**: {strategy.get('breaking_changes_count', 0)}

## Approach
- Use phased migration approach to minimize risk
- Maintain parallel systems during transition
- Implement feature flags for gradual rollout
- Comprehensive testing at each phase
- Prepared rollback plan at all times
"""

    def _format_breaking_changes_section(self, breaking_changes: List[Dict]) -> str:
        """Format breaking changes section."""
        if not breaking_changes:
            return "No significant breaking changes identified.\n"

        content = ""
        for change in breaking_changes:
            content += f"""
### {change.get('area', 'Unknown')}
- **Description**: {change.get('description', '')}
- **Impact**: {change.get('impact', '')}
- **Severity**: {change.get('severity', '')}
- **Mitigation**: {change.get('mitigation', '')}
"""

        return content

    def _format_phases_section(self, phases: List[Dict]) -> str:
        """Format migration phases section."""
        content = ""

        for phase in phases:
            content += f"""
### Phase {phase.get('phase', 0)}: {phase.get('name', 'Unknown')}
- **Tasks**: {', '.join(phase.get('tasks', []))}
- **Effort**: {phase.get('effort_hours', 0)} hours
- **Risk Level**: {phase.get('risk_level', 'Unknown')}
- **Dependencies**: {', '.join(phase.get('dependencies', [])) or 'None'}
"""

        return content

    def _format_code_section(self, generated_code: Dict[str, Any]) -> str:
        """Format generated code section."""
        files = generated_code.get("files_generated", [])

        content = f"## Code Files Generated\n\nTotal: {len(files)} files\n\n"

        for file_path in files:
            content += f"- {file_path}\n"

        return content

    def _format_risks_section(self, risks: Dict[str, Any]) -> str:
        """Format risks section."""
        risk_list = risks.get("risk_details", [])

        content = f"## Identified Risks\n\nTotal: {risks.get('total_identified', 0)} risks\n\n"

        for risk in risk_list:
            content += f"""
### {risk.get('risk', 'Unknown')}
- **Probability**: {risk.get('probability', 'Unknown')}
- **Impact**: {risk.get('impact', 'Unknown')}
- **Mitigation**: {risk.get('mitigation', 'Unknown')}
"""

        return content

    def _format_recommendations_section(self, recommendations: List[str]) -> str:
        """Format recommendations section."""
        content = "## Key Recommendations\n\n"

        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"

        return content

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format code metrics."""
        return f"""
- **Lines of Code**: {metrics.get('total_lines_of_code', 0)}
- **Avg File Size**: {metrics.get('average_file_size', 0)} LOC
- **Classes**: {metrics.get('total_classes', 0)}
- **Functions**: {metrics.get('total_functions', 0)}
- **Complexity Score**: {metrics.get('complexity', 5)}/10
- **Maintainability**: {metrics.get('maintainability', 5)}/10
"""

    def _format_architecture(self, structure: Dict[str, Any]) -> str:
        """Format architecture information."""
        patterns = structure.get("architecture_patterns", [])

        content = "- **Detected Patterns**: "
        if patterns:
            content += ", ".join(patterns)
        else:
            content += "No specific patterns"

        entry_points = structure.get("entry_points", [])
        if entry_points:
            content += f"\n- **Entry Points**: {', '.join(entry_points[:3])}"

        return content + "\n"

    def _create_file_manifest(
        self,
        migration_result: Dict[str, Any],
        generated_docs: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Create manifest of generated files."""
        files = []

        if migration_result:
            generated_files = migration_result.get("generated_code", {}).get("files_generated", [])
            for file_path in generated_files:
                files.append(
                    {
                        "path": file_path,
                        "type": "generated_code",
                        "status": "ready",
                    }
                )

        if generated_docs:
            doc_files = (
                generated_docs.get("generated_documentation", {}).get("generated_files", [])
            )
            for file_path in doc_files:
                files.append(
                    {
                        "path": file_path,
                        "type": "documentation",
                        "status": "ready",
                    }
                )

        return files

    def _create_documentation_list(self, generated_docs: Dict[str, Any]) -> List[str]:
        """Create list of generated documentation files."""
        docs = generated_docs.get("generated_documentation", {})

        files = [
            "MIGRATION_GUIDE.md",
            "BREAKING_CHANGES.md",
            "API_DOCUMENTATION.md",
            "TROUBLESHOOTING.md",
            "BEST_PRACTICES.md",
            "FAQ.md",
        ]

        return files

    def get_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_history

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history = []

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ReportGenerationChain("
            f"stages=[DocumentationGenerator, ReportAssembly], "
            f"executions={len(self.execution_history)})"
        )


# Global report generation chain instance
report_generation_chain = ReportGenerationChain()
