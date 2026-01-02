"""
Code Analysis Service - Orchestrates code parsing and analysis across repository.
Coordinates between GitHub service, parsers, and cache manager.
Provides comprehensive code structure analysis and metrics.
"""

from typing import Dict, List, Optional, Tuple

from src.models.analysis_result import CodeQualityMetrics
from src.models.repository import RepositoryAnalysis, RepositoryStructure
from src.parsers.parser_factory import parser_factory
from src.services.github_service import github_service
from src.utils.cache_manager import cache_manager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CodeAnalysisError(Exception):
    """Base exception for code analysis errors."""

    pass


class CodeAnalysisService:
    """
    Service for analyzing code structure and quality.

    Handles:
    - Multi-file parsing across repository
    - Code metrics calculation (LOC, complexity, etc.)
    - Pattern detection (architecture, dependencies)
    - Cache management for analysis results
    - Graceful error handling for unsupported files
    """

    def __init__(self):
        """Initialize code analysis service."""
        logger.debug("Code analysis service initialized")

    def analyze_file(
        self,
        repo_url: str,
        repo_path: str,
        file_path: str,
        use_cache: bool = True,
    ) -> Optional[Dict]:
        """
        Analyze a single file and extract structure.

        Args:
            repo_url: Repository URL (for caching)
            repo_path: Path to cloned repository
            file_path: Relative path to file within repo
            use_cache: Whether to use cached results

        Returns:
            Analysis result dict or None if file unsupported
        """
        try:
            # Check cache first
            if use_cache:
                cached = cache_manager.get_file_analysis(repo_url, file_path, "auto")
                if cached:
                    logger.debug(f"Cache hit for {file_path}")
                    return cached

            # Read file
            content = github_service.read_file(repo_path, file_path)

            # Detect language and parse
            language = parser_factory.detect_language_from_content(content, file_path)

            if not language:
                logger.debug(f"Unsupported language: {file_path}")
                return None

            if not parser_factory.is_supported(language):
                logger.debug(f"Parser not available for {language}: {file_path}")
                return None

            # Parse file
            parser = parser_factory.get_parser(language)
            parsed_file = parser.parse(file_path, content)

            # Convert to dict for caching
            result = {
                "file_path": file_path,
                "language": language,
                "total_lines": parsed_file.total_lines,
                "imports_count": len(parsed_file.imports),
                "classes_count": len(parsed_file.classes),
                "functions_count": len(parsed_file.functions),
                "imports": [
                    {
                        "module": imp.module,
                        "items": imp.items,
                        "alias": imp.alias,
                        "is_relative": imp.is_relative,
                    }
                    for imp in parsed_file.imports
                ],
                "classes": [
                    {
                        "name": cls.name,
                        "line_start": cls.line_start,
                        "line_end": cls.line_end,
                        "methods_count": len(cls.methods),
                        "parent_class": cls.parent_class,
                        "is_public": cls.is_public,
                        "methods": [
                            {
                                "name": method.name,
                                "signature": method.signature,
                                "params": method.params,
                                "is_public": method.is_public,
                            }
                            for method in cls.methods
                        ],
                    }
                    for cls in parsed_file.classes
                ],
                "functions": [
                    {
                        "name": func.name,
                        "signature": func.signature,
                        "params": func.params,
                        "is_public": func.is_public,
                    }
                    for func in parsed_file.functions
                ],
                "errors": parsed_file.errors,
            }

            # Cache result
            if use_cache:
                cache_manager.cache_file_analysis(repo_url, file_path, language, result)

            logger.debug(f"Analyzed {file_path}: {len(parsed_file.classes)} classes, "
                        f"{len(parsed_file.functions)} functions")
            return result

        except Exception as e:
            logger.warning(f"Error analyzing {file_path}: {str(e)}")
            return None

    def analyze_repository(
        self,
        repo_url: str,
        repo_path: str,
        max_files: int = 50,
        use_cache: bool = True,
        file_pattern: Optional[str] = None,
    ) -> RepositoryAnalysis:
        """
        Analyze entire repository structure and code quality.

        Args:
            repo_url: Repository URL
            repo_path: Path to cloned repository
            max_files: Maximum files to analyze
            use_cache: Whether to use cached results
            file_pattern: Optional glob pattern to filter files

        Returns:
            RepositoryAnalysis with full repo structure
        """
        logger.info(f"Analyzing repository: {repo_url}")

        try:
            # Check cache first
            if use_cache:
                cached = cache_manager.get_repo_structure(repo_url)
                if cached:
                    logger.info("Repository analysis retrieved from cache")
                    # Reconstruct RepositoryAnalysis from cached dict
                    return self._dict_to_repo_analysis(cached)

            # List files in repository
            files = github_service.list_files(
                repo_path,
                pattern=file_pattern,
                max_depth=10,
            )

            # Limit files analyzed
            files_to_analyze = files[:max_files]
            logger.info(f"Analyzing {len(files_to_analyze)} files (total: {len(files)})")

            # Analyze each file
            analyzed_files = []
            language_counts = {}
            class_count = 0
            function_count = 0
            import_count = 0
            total_lines = 0
            errors = []

            for file_path in files_to_analyze:
                analysis = self.analyze_file(repo_url, repo_path, file_path, use_cache)

                if analysis:
                    analyzed_files.append(analysis)

                    # Aggregate metrics
                    language = analysis.get("language", "unknown")
                    language_counts[language] = language_counts.get(language, 0) + 1

                    class_count += analysis.get("classes_count", 0)
                    function_count += analysis.get("functions_count", 0)
                    import_count += analysis.get("imports_count", 0)
                    total_lines += analysis.get("total_lines", 0)

                    if analysis.get("errors"):
                        errors.extend(analysis["errors"])

            # Calculate code quality metrics
            metrics = self._calculate_metrics(
                analyzed_files, total_lines, class_count, function_count
            )

            # Build repository structure
            repo_structure = RepositoryStructure(
                files=analyzed_files,
                entry_points=self._identify_entry_points(analyzed_files),
                config_files=self._identify_config_files(files),
                dependencies=self._extract_dependencies(analyzed_files),
                architecture_patterns=self._detect_patterns(analyzed_files),
                language_distribution=language_counts,
            )

            # Build analysis result
            analysis_result = RepositoryAnalysis(
                repository_url=repo_url,
                structure=repo_structure,
                code_quality=metrics,
                total_files=len(files),
                analyzed_files=len(analyzed_files),
                primary_language=self._get_primary_language(language_counts),
                error_summary=errors,
            )

            # Cache result
            if use_cache:
                cache_manager.cache_repo_structure(repo_url, analysis_result.dict())

            logger.info(f"✓ Repository analysis complete: {class_count} classes, "
                       f"{function_count} functions, {import_count} imports")

            return analysis_result

        except Exception as e:
            logger.error(f"Error analyzing repository: {str(e)}")
            raise CodeAnalysisError(f"Repository analysis failed: {str(e)}") from e

    def _calculate_metrics(
        self,
        analyzed_files: List[Dict],
        total_lines: int,
        class_count: int,
        function_count: int,
    ) -> CodeQualityMetrics:
        """
        Calculate code quality metrics from analysis.

        Args:
            analyzed_files: List of analyzed files
            total_lines: Total lines of code
            class_count: Total classes
            function_count: Total functions

        Returns:
            CodeQualityMetrics
        """
        # Estimate complexity (oversimplified)
        avg_file_size = total_lines / len(analyzed_files) if analyzed_files else 0
        avg_class_size = total_lines / class_count if class_count > 0 else 0

        # Complexity score (1-10 scale)
        complexity_score = min(10, max(1, int(avg_file_size / 100)))

        # Maintainability score (1-10 scale)
        maintainability = 10
        if avg_class_size > 500:
            maintainability -= 3
        if avg_file_size > 2000:
            maintainability -= 2
        if len(analyzed_files) > 100:
            maintainability -= 1

        return CodeQualityMetrics(
            total_lines_of_code=total_lines,
            average_file_size=int(avg_file_size),
            average_function_length=int(avg_file_size / function_count) if function_count > 0 else 0,
            total_classes=class_count,
            total_functions=function_count,
            code_complexity_score=complexity_score,
            maintainability_index=max(1, min(10, maintainability)),
            code_duplication_percentage=0,  # Would need actual analysis
            test_coverage_percentage=0,  # Would need actual test analysis
            documentation_coverage_percentage=0,  # Would need docstring analysis
            technical_debt_score=10 - max(1, min(10, maintainability)),
        )

    def _identify_entry_points(self, analyzed_files: List[Dict]) -> List[str]:
        """
        Identify likely entry points in the codebase.

        Args:
            analyzed_files: List of analyzed files

        Returns:
            List of likely entry point file paths
        """
        entry_points = []

        # Common entry point patterns
        patterns = ["main.py", "index.js", "app.py", "server.py", "main.java", "Main.java"]

        for file_analysis in analyzed_files:
            file_path = file_analysis.get("file_path", "")

            # Check if filename matches pattern
            for pattern in patterns:
                if file_path.endswith(pattern):
                    entry_points.append(file_path)

            # Check for main/entry functions
            functions = file_analysis.get("functions", [])
            for func in functions:
                if func.get("name") in ["main", "execute", "run"]:
                    entry_points.append(file_path)

        return entry_points[:5]  # Return top 5

    def _identify_config_files(self, files: List[str]) -> List[str]:
        """
        Identify configuration files in repository.

        Args:
            files: List of all files

        Returns:
            List of configuration file paths
        """
        config_patterns = [
            "package.json",
            "requirements.txt",
            "pom.xml",
            "build.gradle",
            "setup.py",
            "pyproject.toml",
            ".env",
            "config.yaml",
            "config.yml",
            "docker-compose.yml",
            "Dockerfile",
        ]

        config_files = []
        for file_path in files:
            for pattern in config_patterns:
                if file_path.endswith(pattern):
                    config_files.append(file_path)

        return config_files

    def _extract_dependencies(self, analyzed_files: List[Dict]) -> List[Dict]:
        """
        Extract dependencies from analyzed files.

        Args:
            analyzed_files: List of analyzed files

        Returns:
            List of dependency dictionaries
        """
        dependencies = {}

        for file_analysis in analyzed_files:
            imports = file_analysis.get("imports", [])

            for imp in imports:
                module = imp.get("module", "")

                # Skip relative imports
                if imp.get("is_relative"):
                    continue

                # Skip standard library modules (heuristic)
                if module and not module.startswith("."):
                    if module not in dependencies:
                        dependencies[module] = {
                            "module": module,
                            "items": imp.get("items", []),
                            "count": 1,
                        }
                    else:
                        dependencies[module]["count"] += 1

        return list(dependencies.values())[:20]  # Top 20 dependencies

    def _detect_patterns(self, analyzed_files: List[Dict]) -> List[str]:
        """
        Detect architectural patterns in codebase.

        Args:
            analyzed_files: List of analyzed files

        Returns:
            List of detected patterns
        """
        patterns = []

        # Check for MVC pattern
        mvc_indicators = {"model": 0, "view": 0, "controller": 0}
        for file_analysis in analyzed_files:
            file_path = file_analysis.get("file_path", "").lower()
            if "model" in file_path:
                mvc_indicators["model"] += 1
            if "view" in file_path:
                mvc_indicators["view"] += 1
            if "controller" in file_path:
                mvc_indicators["controller"] += 1

        if sum(mvc_indicators.values()) > 3:
            patterns.append("MVC")

        # Check for microservices pattern
        service_files = 0
        for file_analysis in analyzed_files:
            file_path = file_analysis.get("file_path", "").lower()
            if "service" in file_path:
                service_files += 1

        if service_files > len(analyzed_files) * 0.3:
            patterns.append("Microservices")

        # Check for layered architecture
        layer_count = 0
        layer_names = ["api", "service", "repository", "domain"]
        for file_analysis in analyzed_files:
            file_path = file_analysis.get("file_path", "").lower()
            for layer in layer_names:
                if layer in file_path:
                    layer_count += 1
                    break

        if layer_count > len(analyzed_files) * 0.2:
            patterns.append("Layered Architecture")

        return patterns

    def _get_primary_language(self, language_counts: Dict[str, int]) -> str:
        """
        Determine primary language in repository.

        Args:
            language_counts: Language distribution dictionary

        Returns:
            Primary language name
        """
        if not language_counts:
            return "unknown"

        return max(language_counts, key=language_counts.get)

    def _dict_to_repo_analysis(self, cached_dict: Dict) -> RepositoryAnalysis:
        """
        Convert cached dictionary back to RepositoryAnalysis object.

        Args:
            cached_dict: Cached analysis dictionary

        Returns:
            RepositoryAnalysis object
        """
        # Simplified reconstruction (in production would fully validate)
        return RepositoryAnalysis(
            repository_url=cached_dict.get("repository_url"),
            structure=RepositoryStructure(
                files=cached_dict.get("structure", {}).get("files", []),
                entry_points=cached_dict.get("structure", {}).get("entry_points", []),
                config_files=cached_dict.get("structure", {}).get("config_files", []),
                dependencies=cached_dict.get("structure", {}).get("dependencies", []),
                architecture_patterns=cached_dict.get("structure", {}).get("architecture_patterns", []),
                language_distribution=cached_dict.get("structure", {}).get("language_distribution", {}),
            ),
            code_quality=CodeQualityMetrics(
                total_lines_of_code=cached_dict.get("code_quality", {}).get("total_lines_of_code", 0),
                average_file_size=cached_dict.get("code_quality", {}).get("average_file_size", 0),
                average_function_length=cached_dict.get("code_quality", {}).get("average_function_length", 0),
                total_classes=cached_dict.get("code_quality", {}).get("total_classes", 0),
                total_functions=cached_dict.get("code_quality", {}).get("total_functions", 0),
                code_complexity_score=cached_dict.get("code_quality", {}).get("code_complexity_score", 5),
                maintainability_index=cached_dict.get("code_quality", {}).get("maintainability_index", 5),
            ),
            total_files=cached_dict.get("total_files", 0),
            analyzed_files=cached_dict.get("analyzed_files", 0),
            primary_language=cached_dict.get("primary_language", "unknown"),
            error_summary=cached_dict.get("error_summary", []),
        )


# Global code analysis service instance
code_analysis_service = CodeAnalysisService()
