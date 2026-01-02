"""
Repository Analyzer Agent - Analyzes repository structure and architecture.
Identifies entry points, dependencies, patterns, and provides comprehensive overview.
First agent in the analysis pipeline.
"""

from typing import Any, Dict

from src.agents.base_agent import BaseAgent, AgentError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RepositoryAnalyzerAgent(BaseAgent):
    """
    Agent for analyzing repository structure and architecture.

    Responsibilities:
    - Scan repository file structure
    - Identify entry points (main files, entry scripts)
    - Detect architecture patterns (MVC, microservices, layered)
    - Extract dependencies and imports
    - Identify configuration files
    - Calculate code metrics (LOC, complexity, maintainability)
    - Provide comprehensive repository overview

    Output:
    - Repository structure analysis
    - Entry points identification
    - Architecture pattern detection
    - Code quality metrics
    """

    def __init__(self):
        """Initialize Repository Analyzer Agent."""
        super().__init__(
            agent_name="RepositoryAnalyzer",
            description="Analyzes repository structure, architecture patterns, and code organization",
            system_prompt=self._get_repo_analyzer_prompt(),
            max_iterations=5,
            temperature=0.1,
        )

        # Register tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register tools for repository analysis."""
        self.register_tool(
            name="analyze_repository",
            description="Analyze complete repository structure, metrics, and patterns",
            func=self._tool_analyze_repository,
        )

        self.register_tool(
            name="identify_entry_points",
            description="Identify main entry points and executable files in repository",
            func=self._tool_identify_entry_points,
        )

        self.register_tool(
            name="detect_architecture",
            description="Detect architecture patterns (MVC, microservices, layered, etc.)",
            func=self._tool_detect_architecture,
        )

        self.register_tool(
            name="extract_dependencies",
            description="Extract external dependencies and imports from codebase",
            func=self._tool_extract_dependencies,
        )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input for repository analysis.

        Args:
            input_data: Must contain 'repo_url' and 'repo_path'

        Returns:
            True if valid

        Raises:
            AgentError: If required fields missing
        """
        super().validate_input(input_data)

        required_fields = ["repo_url", "repo_path"]
        for field in required_fields:
            if field not in input_data:
                raise AgentError(f"Repository Analyzer requires '{field}' in input")

        return True

    def prepare_context(self, input_data: Dict[str, Any]) -> str:
        """
        Prepare context for repository analysis.

        Args:
            input_data: Repository information

        Returns:
            Context string
        """
        base_context = super().prepare_context(input_data)

        additional = f"""
Available Actions:
1. Analyze the repository structure and code metrics
2. Identify main entry points and executable files
3. Detect architectural patterns and organization style
4. Extract external dependencies and imports

Focus Areas:
- Code organization and structure
- Architecture and design patterns
- Entry points and execution flow
- External dependencies and libraries
- Configuration files and setup
"""

        return f"{base_context}\n{additional}"

    def _process_result(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process repository analysis result.

        Args:
            response: LLM response from analysis
            input_data: Original input

        Returns:
            Structured result
        """
        # Try to run actual analysis
        repo_url = input_data.get("repo_url")
        repo_path = input_data.get("repo_path")

        analysis_result = {
            "agent": self.agent_name,
            "repository_url": repo_url,
            "llm_analysis": response,
            "success": True,
        }

        try:
            # Run actual code analysis
            actual_analysis = self.code_analysis_service.analyze_repository(
                repo_url=repo_url,
                repo_path=repo_path,
                max_files=50,
                use_cache=True,
            )

            analysis_result["actual_analysis"] = {
                "total_files": actual_analysis.total_files,
                "analyzed_files": actual_analysis.analyzed_files,
                "primary_language": actual_analysis.primary_language,
                "structure": {
                    "entry_points": actual_analysis.structure.entry_points,
                    "config_files": actual_analysis.structure.config_files,
                    "dependencies": actual_analysis.structure.dependencies,
                    "architecture_patterns": actual_analysis.structure.architecture_patterns,
                    "language_distribution": actual_analysis.structure.language_distribution,
                },
                "metrics": {
                    "total_lines_of_code": actual_analysis.code_quality.total_lines_of_code,
                    "average_file_size": actual_analysis.code_quality.average_file_size,
                    "total_classes": actual_analysis.code_quality.total_classes,
                    "total_functions": actual_analysis.code_quality.total_functions,
                    "complexity_score": actual_analysis.code_quality.code_complexity_score,
                    "maintainability_index": actual_analysis.code_quality.maintainability_index,
                },
            }

            logger.debug(f"Repository analysis complete: {actual_analysis.analyzed_files} files analyzed")

        except Exception as e:
            logger.warning(f"Actual analysis failed, using LLM response only: {str(e)}")
            analysis_result["actual_analysis_error"] = str(e)

        return analysis_result

    def _get_repo_analyzer_prompt(self) -> str:
        """Get system prompt for repository analyzer."""
        return """You are RepositoryAnalyzer, an expert code structure analyst.

Your expertise:
- Understanding software architecture and code organization
- Identifying design patterns and architectural styles
- Analyzing code structure and dependencies
- Assessing code quality and complexity
- Finding entry points and main execution flows

When analyzing a repository, you should:
1. Examine the overall structure and organization
2. Identify primary entry points and executable files
3. Detect architectural patterns (MVC, microservices, layered, etc.)
4. Analyze external dependencies and imports
5. Assess code quality metrics (LOC, complexity, maintainability)
6. Identify configuration and setup files
7. Determine primary programming language(s)

Provide clear, structured analysis with specific findings."""

    # ===== Tool Implementations =====

    def _tool_analyze_repository(self, repo_path: str = None) -> Dict[str, Any]:
        """
        Analyze complete repository.

        Args:
            repo_path: Path to repository (from current input)

        Returns:
            Analysis results
        """
        if not repo_path and self.current_input:
            repo_path = self.current_input.get("repo_path")

        if not repo_path:
            return {"error": "No repository path provided"}

        try:
            repo_url = self.current_input.get("repo_url", "unknown") if self.current_input else "unknown"

            analysis = self.code_analysis_service.analyze_repository(
                repo_url=repo_url,
                repo_path=repo_path,
                max_files=50,
                use_cache=True,
            )

            return {
                "total_files": analysis.total_files,
                "analyzed_files": analysis.analyzed_files,
                "primary_language": analysis.primary_language,
                "languages": analysis.structure.language_distribution,
                "total_lines": analysis.code_quality.total_lines_of_code,
                "avg_file_size": analysis.code_quality.average_file_size,
                "total_classes": analysis.code_quality.total_classes,
                "total_functions": analysis.code_quality.total_functions,
                "complexity_score": analysis.code_quality.code_complexity_score,
                "maintainability": analysis.code_quality.maintainability_index,
            }

        except Exception as e:
            logger.error(f"Repository analysis failed: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}

    def _tool_identify_entry_points(self, repo_path: str = None) -> Dict[str, Any]:
        """
        Identify entry points in repository.

        Args:
            repo_path: Path to repository

        Returns:
            Entry points and executable files
        """
        if not repo_path and self.current_input:
            repo_path = self.current_input.get("repo_path")

        if not repo_path:
            return {"error": "No repository path provided"}

        try:
            repo_url = self.current_input.get("repo_url", "unknown") if self.current_input else "unknown"

            analysis = self.code_analysis_service.analyze_repository(
                repo_url=repo_url,
                repo_path=repo_path,
                max_files=50,
                use_cache=True,
            )

            return {
                "entry_points": analysis.structure.entry_points,
                "config_files": analysis.structure.config_files,
                "total_identified": len(analysis.structure.entry_points),
            }

        except Exception as e:
            logger.error(f"Entry point identification failed: {str(e)}")
            return {"error": f"Identification failed: {str(e)}"}

    def _tool_detect_architecture(self, repo_path: str = None) -> Dict[str, Any]:
        """
        Detect architecture patterns.

        Args:
            repo_path: Path to repository

        Returns:
            Detected patterns and architecture style
        """
        if not repo_path and self.current_input:
            repo_path = self.current_input.get("repo_path")

        if not repo_path:
            return {"error": "No repository path provided"}

        try:
            repo_url = self.current_input.get("repo_url", "unknown") if self.current_input else "unknown"

            analysis = self.code_analysis_service.analyze_repository(
                repo_url=repo_url,
                repo_path=repo_path,
                max_files=50,
                use_cache=True,
            )

            return {
                "patterns": analysis.structure.architecture_patterns,
                "description": self._describe_architecture(analysis.structure.architecture_patterns),
            }

        except Exception as e:
            logger.error(f"Architecture detection failed: {str(e)}")
            return {"error": f"Detection failed: {str(e)}"}

    def _tool_extract_dependencies(self, repo_path: str = None) -> Dict[str, Any]:
        """
        Extract external dependencies.

        Args:
            repo_path: Path to repository

        Returns:
            Dependencies and imports
        """
        if not repo_path and self.current_input:
            repo_path = self.current_input.get("repo_path")

        if not repo_path:
            return {"error": "No repository path provided"}

        try:
            repo_url = self.current_input.get("repo_url", "unknown") if self.current_input else "unknown"

            analysis = self.code_analysis_service.analyze_repository(
                repo_url=repo_url,
                repo_path=repo_path,
                max_files=50,
                use_cache=True,
            )

            return {
                "total_dependencies": len(analysis.structure.dependencies),
                "top_dependencies": analysis.structure.dependencies[:10],
                "dependency_count": {
                    dep["module"]: dep["count"] for dep in analysis.structure.dependencies[:10]
                },
            }

        except Exception as e:
            logger.error(f"Dependency extraction failed: {str(e)}")
            return {"error": f"Extraction failed: {str(e)}"}

    def _describe_architecture(self, patterns: list) -> str:
        """
        Create description of detected architecture.

        Args:
            patterns: Detected patterns

        Returns:
            Description string
        """
        if not patterns:
            return "No specific patterns detected - appears to be a simple or custom architecture"

        descriptions = {
            "MVC": "Model-View-Controller pattern - organized with models, views, and controllers",
            "Microservices": "Microservices architecture - decomposed into multiple independent services",
            "Layered Architecture": "Layered/N-tier architecture - organized in distinct horizontal layers",
        }

        return "; ".join([descriptions.get(p, p) for p in patterns])
