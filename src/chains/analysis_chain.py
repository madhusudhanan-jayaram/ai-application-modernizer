"""
Analysis Chain - Orchestrates repository analysis workflow.
Coordinates: RepositoryAnalyzer → TechStackDetector
Produces comprehensive repository analysis with detected tech stack.
"""

from typing import Any, Dict, List

from src.agents.repo_analyzer import RepositoryAnalyzerAgent
from src.agents.tech_stack_detector import TechStackDetectorAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AnalysisChainError(Exception):
    """Exception for analysis chain errors."""

    pass


class AnalysisChain:
    """
    Chain for analyzing repository and detecting technology stack.

    Workflow:
    1. RepositoryAnalyzer: Analyze structure, code metrics, patterns
    2. TechStackDetector: Detect languages, frameworks, libraries, maturity

    Input:
    - repo_url: GitHub repository URL
    - repo_path: Local cloned repository path

    Output:
    - RepositoryAnalysis with all findings
    - Detected TechStack
    - Comprehensive assessment
    """

    def __init__(self):
        """Initialize analysis chain."""
        self.repo_analyzer = RepositoryAnalyzerAgent()
        self.tech_detector = TechStackDetectorAgent()

        self.execution_history = []

        logger.info("✓ Analysis chain initialized")

    def run(
        self,
        repo_url: str,
        repo_path: str,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute analysis chain.

        Args:
            repo_url: Repository URL
            repo_path: Local cloned path
            use_cache: Whether to use cached results

        Returns:
            Complete analysis result
        """
        logger.info(f"[AnalysisChain] Starting analysis of {repo_url}")

        try:
            # ===== Step 1: Repository Analysis =====
            logger.info("[AnalysisChain] Step 1: Analyzing repository structure")

            repo_analysis_input = {
                "repo_url": repo_url,
                "repo_path": repo_path,
                "task": "Analyze repository structure, architecture patterns, and code organization",
                "context": "Initial repository scan to understand codebase organization and quality",
            }

            repo_analysis = self.repo_analyzer.execute(repo_analysis_input, use_cache=use_cache)

            logger.info(f"[AnalysisChain] Repository analysis complete")
            logger.debug(f"Repository metrics: {repo_analysis.get('actual_analysis', {}).get('metrics', {})}")

            # ===== Step 2: Technology Stack Detection =====
            logger.info("[AnalysisChain] Step 2: Detecting technology stack")

            tech_detection_input = {
                "repo_url": repo_url,
                "repo_path": repo_path,
                "analysis_result": repo_analysis.get("actual_analysis"),  # Pass repo analysis
                "task": "Detect programming languages, frameworks, libraries, and technology stack",
                "context": f"Analyze detected {repo_analysis.get('actual_analysis', {}).get('primary_language')} codebase",
            }

            tech_stack = self.tech_detector.execute(tech_detection_input, use_cache=use_cache)

            logger.info(f"[AnalysisChain] Tech stack detection complete")
            logger.debug(f"Detected stack: {tech_stack.get('detected_tech_stack', {})}")

            # ===== Compile Results =====
            result = self._compile_analysis_result(
                repo_url, repo_analysis, tech_stack, repo_path
            )

            # Log execution
            self.execution_history.append(
                {
                    "repo_url": repo_url,
                    "success": True,
                    "steps": ["Repository Analysis", "Tech Stack Detection"],
                    "result": result,
                }
            )

            logger.info(f"[AnalysisChain] ✓ Analysis complete for {repo_url}")
            return result

        except Exception as e:
            logger.error(f"[AnalysisChain] Analysis failed: {str(e)}")

            self.execution_history.append(
                {
                    "repo_url": repo_url,
                    "success": False,
                    "error": str(e),
                }
            )

            raise AnalysisChainError(f"Analysis chain failed: {str(e)}") from e

    def _compile_analysis_result(
        self,
        repo_url: str,
        repo_analysis: Dict[str, Any],
        tech_stack: Dict[str, Any],
        repo_path: str,
    ) -> Dict[str, Any]:
        """
        Compile analysis results from both agents.

        Args:
            repo_url: Repository URL
            repo_analysis: Results from RepositoryAnalyzer
            tech_stack: Results from TechStackDetector
            repo_path: Local repository path

        Returns:
            Compiled analysis result
        """
        actual_repo_analysis = repo_analysis.get("actual_analysis", {})
        detected_stack = tech_stack.get("detected_tech_stack", {})

        return {
            "analysis_type": "Repository + Technology Stack Analysis",
            "repository_url": repo_url,
            "repository_path": repo_path,
            "status": "complete",
            # ===== Repository Analysis =====
            "repository_analysis": {
                "total_files": actual_repo_analysis.get("total_files", 0),
                "analyzed_files": actual_repo_analysis.get("analyzed_files", 0),
                "primary_language": actual_repo_analysis.get("primary_language", "unknown"),
                "structure": actual_repo_analysis.get("structure", {}),
                "metrics": actual_repo_analysis.get("metrics", {}),
            },
            # ===== Tech Stack Detection =====
            "technology_stack": {
                "primary_language": detected_stack.get("primary_language"),
                "languages": detected_stack.get("languages", []),
                "frameworks": detected_stack.get("frameworks", []),
                "databases": detected_stack.get("databases", []),
                "maturity": detected_stack.get("maturity", "Unknown"),
            },
            # ===== Agent Analysis =====
            "repo_analyzer_insight": repo_analysis.get("llm_analysis", ""),
            "tech_detector_insight": tech_stack.get("llm_analysis", ""),
            # ===== Summary =====
            "summary": self._create_analysis_summary(
                actual_repo_analysis, detected_stack
            ),
        }

    def _create_analysis_summary(
        self,
        repo_analysis: Dict[str, Any],
        tech_stack: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create executive summary of analysis.

        Args:
            repo_analysis: Repository analysis data
            tech_stack: Technology stack data

        Returns:
            Summary dictionary
        """
        metrics = repo_analysis.get("metrics", {})
        structure = repo_analysis.get("structure", {})

        return {
            "codebase_size": f"{metrics.get('total_lines_of_code', 0)} LOC",
            "code_quality": {
                "complexity": metrics.get("complexity_score", 5),
                "maintainability": metrics.get("maintainability_index", 5),
            },
            "architecture_patterns": structure.get("architecture_patterns", []),
            "entry_points": structure.get("entry_points", []),
            "primary_language": repo_analysis.get("primary_language", "Unknown"),
            "technology_count": {
                "languages": len(tech_stack.get("languages", [])),
                "frameworks": len(tech_stack.get("frameworks", [])),
                "databases": len(tech_stack.get("databases", [])),
            },
            "key_dependencies": structure.get("dependencies", [])[:5],
            "assessment": self._generate_assessment(repo_analysis, tech_stack),
        }

    def _generate_assessment(
        self,
        repo_analysis: Dict[str, Any],
        tech_stack: Dict[str, Any],
    ) -> str:
        """
        Generate human-readable assessment.

        Args:
            repo_analysis: Repository data
            tech_stack: Technology stack data

        Returns:
            Assessment string
        """
        metrics = repo_analysis.get("metrics", {})
        primary_lang = repo_analysis.get("primary_language", "unknown")

        parts = []

        # Size assessment
        loc = metrics.get("total_lines_of_code", 0)
        if loc < 10000:
            parts.append("Small codebase")
        elif loc < 100000:
            parts.append("Medium-sized codebase")
        else:
            parts.append("Large codebase")

        # Quality assessment
        complexity = metrics.get("complexity_score", 5)
        maintainability = metrics.get("maintainability_index", 5)

        if maintainability < 4:
            parts.append("low code maintainability")
        elif maintainability < 7:
            parts.append("moderate code quality")
        else:
            parts.append("good code quality")

        # Language assessment
        if primary_lang:
            parts.append(f"primarily {primary_lang}")

        # Architecture assessment
        patterns = repo_analysis.get("structure", {}).get("architecture_patterns", [])
        if patterns:
            parts.append(f"using {', '.join(patterns)} pattern")

        assessment = "This is a " + ", ".join(parts) + "."

        return assessment

    def get_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_history

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history = []

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"AnalysisChain("
            f"stages=[RepositoryAnalyzer, TechStackDetector], "
            f"executions={len(self.execution_history)})"
        )


# Global analysis chain instance
analysis_chain = AnalysisChain()
