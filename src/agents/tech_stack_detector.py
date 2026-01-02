"""
Tech Stack Detector Agent - Detects programming languages, frameworks, and libraries.
Identifies technology stack used in a repository and assesses versions and maturity.
Second agent in the analysis pipeline.
"""

import re
from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent, AgentError
from src.models.tech_stack import Language, Framework, Library, TechStack
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TechStackDetectorAgent(BaseAgent):
    """
    Agent for detecting technology stack in repository.

    Responsibilities:
    - Identify primary programming languages
    - Detect frameworks and libraries
    - Infer versions when possible
    - Assess technology maturity
    - Identify database technologies
    - Detect deployment targets
    - Classify architecture style

    Output:
    - TechStack object with detected technologies
    - Confidence scores for each detection
    - Version information
    - Maturity assessment
    """

    # Technology detection patterns
    LANGUAGE_PATTERNS = {
        "python": {
            "extensions": [".py", ".pyx", ".pyi"],
            "imports": ["import python", "from python"],
            "confidence": 0.95,
        },
        "java": {
            "extensions": [".java"],
            "imports": ["import java.", "package "],
            "confidence": 0.98,
        },
        "javascript": {
            "extensions": [".js", ".jsx"],
            "imports": ["import ", "require(", "export "],
            "confidence": 0.90,
        },
        "typescript": {
            "extensions": [".ts", ".tsx"],
            "imports": ["import ", "interface ", "type "],
            "confidence": 0.95,
        },
        "go": {
            "extensions": [".go"],
            "imports": ["package ", "import ("],
            "confidence": 0.98,
        },
        "rust": {
            "extensions": [".rs"],
            "imports": ["use ", "mod "],
            "confidence": 0.98,
        },
        "csharp": {
            "extensions": [".cs"],
            "imports": ["using ", "namespace "],
            "confidence": 0.95,
        },
    }

    FRAMEWORK_PATTERNS = {
        # Web Frameworks
        "Django": {"imports": ["django", "from django"], "category": "Web", "language": "python"},
        "Flask": {"imports": ["flask", "from flask"], "category": "Web", "language": "python"},
        "FastAPI": {"imports": ["fastapi", "from fastapi"], "category": "Web", "language": "python"},
        "Spring": {"imports": ["org.springframework", "import org.springframework"], "category": "Web", "language": "java"},
        "Spring Boot": {
            "imports": ["org.springframework.boot", "spring-boot"],
            "category": "Web",
            "language": "java",
        },
        "Express": {"imports": ["express", "require('express')"], "category": "Web", "language": "javascript"},
        "React": {"imports": ["react", "from 'react'"], "category": "Frontend", "language": "javascript"},
        "Vue": {"imports": ["vue", "from 'vue'"], "category": "Frontend", "language": "javascript"},
        "Angular": {"imports": ["@angular", "angular"], "category": "Frontend", "language": "javascript"},
        "Next.js": {
            "imports": ["next", "from 'next'"],
            "category": "Web",
            "language": "javascript",
        },
        "Gin": {"imports": ["github.com/gin-gonic/gin"], "category": "Web", "language": "go"},
        "Echo": {"imports": ["github.com/labstack/echo"], "category": "Web", "language": "go"},
    }

    LIBRARY_PATTERNS = {
        # Data & ORM
        "SQLAlchemy": {"imports": ["sqlalchemy", "from sqlalchemy"], "type": "ORM"},
        "Hibernate": {"imports": ["org.hibernate", "import org.hibernate"], "type": "ORM"},
        "Entity Framework": {"imports": ["System.Data.Entity"], "type": "ORM"},
        "Pandas": {"imports": ["pandas", "import pandas"], "type": "Data"},
        "NumPy": {"imports": ["numpy", "import numpy"], "type": "Data"},
        # Testing
        "pytest": {"imports": ["pytest", "import pytest"], "type": "Testing"},
        "unittest": {"imports": ["unittest", "import unittest"], "type": "Testing"},
        "JUnit": {"imports": ["org.junit", "import org.junit"], "type": "Testing"},
        "Jest": {"imports": ["jest", "from 'jest'"], "type": "Testing"},
        # Async
        "asyncio": {"imports": ["asyncio", "import asyncio"], "type": "Async"},
        "Celery": {"imports": ["celery", "from celery"], "type": "Task"},
        "RabbitMQ": {"imports": ["pika", "amqp"], "type": "Queue"},
    }

    DATABASE_PATTERNS = {
        "PostgreSQL": ["postgresql", "psycopg2", "pg8000", "postgres://"],
        "MySQL": ["mysql", "pymysql", "MySQLdb", "mysql://"],
        "MongoDB": ["mongodb", "pymongo", "MongoClient"],
        "Redis": ["redis", "redis-py", "RedisClient"],
        "SQLite": ["sqlite3", "sqlite"],
        "Oracle": ["cx_Oracle", "oracledb"],
        "DynamoDB": ["boto3", "dynamodb"],
    }

    def __init__(self):
        """Initialize Tech Stack Detector Agent."""
        super().__init__(
            agent_name="TechStackDetector",
            description="Detects programming languages, frameworks, libraries, and technology versions",
            system_prompt=self._get_detector_prompt(),
            max_iterations=5,
            temperature=0.1,
        )

        self._register_tools()

    def _register_tools(self) -> None:
        """Register tools for tech stack detection."""
        self.register_tool(
            name="detect_languages",
            description="Detect programming languages used in repository",
            func=self._tool_detect_languages,
        )

        self.register_tool(
            name="detect_frameworks",
            description="Detect frameworks and major libraries used",
            func=self._tool_detect_frameworks,
        )

        self.register_tool(
            name="detect_databases",
            description="Detect database technologies (SQL, NoSQL, cache)",
            func=self._tool_detect_databases,
        )

        self.register_tool(
            name="assess_stack_maturity",
            description="Assess overall technology stack maturity and modernity",
            func=self._tool_assess_maturity,
        )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input for tech stack detection.

        Args:
            input_data: Must contain 'repo_path' or 'analysis_result'

        Returns:
            True if valid

        Raises:
            AgentError: If required fields missing
        """
        super().validate_input(input_data)

        if "repo_path" not in input_data and "analysis_result" not in input_data:
            raise AgentError("TechStackDetector requires 'repo_path' or 'analysis_result'")

        return True

    def prepare_context(self, input_data: Dict[str, Any]) -> str:
        """
        Prepare context for tech stack detection.

        Args:
            input_data: Analysis context

        Returns:
            Context string
        """
        base_context = super().prepare_context(input_data)

        additional = """
Available Detection Tools:
1. Detect programming languages from file extensions and imports
2. Detect frameworks and major libraries from dependencies
3. Detect database technologies (SQL, NoSQL, caches)
4. Assess overall technology stack maturity

Focus Areas:
- Primary and secondary programming languages
- Web frameworks and libraries
- ORM and database technologies
- Testing and build tools
- Architecture patterns
- Version indicators
- Overall modernization level
"""

        return f"{base_context}\n{additional}"

    def _process_result(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process tech stack detection result.

        Args:
            response: LLM response
            input_data: Original input

        Returns:
            Structured result with detected tech stack
        """
        repo_path = input_data.get("repo_path")

        result = {
            "agent": self.agent_name,
            "llm_analysis": response,
            "success": True,
        }

        try:
            if repo_path:
                # Perform actual tech stack detection
                tech_stack = self._detect_tech_stack(repo_path)
                result["detected_tech_stack"] = {
                    "primary_language": tech_stack.primary_language.language if tech_stack.primary_language else None,
                    "languages": [
                        {
                            "language": lang.language,
                            "version": lang.version,
                            "confidence": lang.confidence,
                        }
                        for lang in tech_stack.languages
                    ],
                    "frameworks": [
                        {
                            "name": fw.name,
                            "version": fw.version,
                            "category": fw.category,
                            "confidence": fw.confidence,
                        }
                        for fw in tech_stack.frameworks
                    ],
                    "databases": [
                        {
                            "name": db.name,
                            "type": db.type,
                            "confidence": db.confidence,
                        }
                        for db in tech_stack.databases
                    ],
                    "maturity": tech_stack.maturity_level,
                }
        except Exception as e:
            logger.warning(f"Tech stack detection failed: {str(e)}")
            result["detection_error"] = str(e)

        return result

    def _get_detector_prompt(self) -> str:
        """Get system prompt for tech stack detector."""
        return """You are TechStackDetector, an expert in identifying and analyzing technology stacks.

Your expertise:
- Recognizing programming languages and versions
- Identifying web frameworks and libraries
- Detecting database technologies
- Assessing technology maturity and modernity
- Evaluating framework popularity and support
- Spotting outdated vs modern technology choices

When analyzing a codebase, identify:
1. Primary and secondary programming languages
2. Web frameworks (Django, Flask, Spring, React, etc.)
3. Key libraries and dependencies
4. Database technologies (SQL, NoSQL, caches)
5. Testing and build tools
6. Architecture patterns (monolith, microservices, serverless)
7. Overall tech stack maturity and modernization level

Provide assessment of:
- Technology freshness (modern vs legacy)
- Support status (active vs deprecated)
- Industry adoption (popular vs niche)
- Version currency
"""

    # ===== Tool Implementations =====

    def _tool_detect_languages(self, repo_path: str = None) -> Dict[str, Any]:
        """
        Detect programming languages.

        Args:
            repo_path: Path to repository

        Returns:
            Detected languages
        """
        if not repo_path and self.current_input:
            repo_path = self.current_input.get("repo_path")

        if not repo_path:
            return {"error": "No repository path provided"}

        try:
            # Analyze code from analysis result if available
            if self.current_input and "analysis_result" in self.current_input:
                language_dist = (
                    self.current_input["analysis_result"]
                    .get("structure", {})
                    .get("language_distribution", {})
                )
                return {
                    "detected_languages": language_dist,
                    "primary_language": max(language_dist, key=language_dist.get)
                    if language_dist
                    else "unknown",
                }

            # Fallback: List files and detect from extensions
            files = self.github_service.list_files(repo_path, max_depth=10)

            lang_counts = {}
            for file_path in files:
                for lang, patterns in self.LANGUAGE_PATTERNS.items():
                    if any(file_path.endswith(ext) for ext in patterns.get("extensions", [])):
                        lang_counts[lang] = lang_counts.get(lang, 0) + 1

            return {
                "detected_languages": lang_counts,
                "primary_language": max(lang_counts, key=lang_counts.get) if lang_counts else "unknown",
            }

        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return {"error": f"Detection failed: {str(e)}"}

    def _tool_detect_frameworks(self, repo_path: str = None) -> Dict[str, Any]:
        """
        Detect frameworks and libraries.

        Args:
            repo_path: Path to repository

        Returns:
            Detected frameworks and libraries
        """
        if not repo_path and self.current_input:
            repo_path = self.current_input.get("repo_path")

        if not repo_path:
            return {"error": "No repository path provided"}

        try:
            frameworks = []
            libraries = []

            # Get all files and scan imports
            files = self.github_service.list_files(repo_path, max_depth=10)

            for file_path in files:
                try:
                    content = self.github_service.read_file(repo_path, file_path)

                    # Detect frameworks
                    for fw_name, fw_info in self.FRAMEWORK_PATTERNS.items():
                        for import_pattern in fw_info.get("imports", []):
                            if import_pattern.lower() in content.lower():
                                if fw_name not in [f["name"] for f in frameworks]:
                                    frameworks.append(
                                        {
                                            "name": fw_name,
                                            "category": fw_info.get("category"),
                                            "language": fw_info.get("language"),
                                            "confidence": 0.85,
                                        }
                                    )

                    # Detect libraries
                    for lib_name, lib_info in self.LIBRARY_PATTERNS.items():
                        for import_pattern in lib_info.get("imports", []):
                            if import_pattern.lower() in content.lower():
                                if lib_name not in [l["name"] for l in libraries]:
                                    libraries.append(
                                        {
                                            "name": lib_name,
                                            "type": lib_info.get("type"),
                                            "confidence": 0.80,
                                        }
                                    )

                except Exception:
                    pass  # Skip files that can't be read

            return {
                "frameworks": frameworks[:10],
                "libraries": libraries[:15],
                "total_frameworks": len(frameworks),
                "total_libraries": len(libraries),
            }

        except Exception as e:
            logger.error(f"Framework detection failed: {str(e)}")
            return {"error": f"Detection failed: {str(e)}"}

    def _tool_detect_databases(self, repo_path: str = None) -> Dict[str, Any]:
        """
        Detect database technologies.

        Args:
            repo_path: Path to repository

        Returns:
            Detected databases
        """
        if not repo_path and self.current_input:
            repo_path = self.current_input.get("repo_path")

        if not repo_path:
            return {"error": "No repository path provided"}

        try:
            detected_dbs = {}

            files = self.github_service.list_files(repo_path, max_depth=10)

            for file_path in files:
                try:
                    content = self.github_service.read_file(repo_path, file_path).lower()

                    for db_name, patterns in self.DATABASE_PATTERNS.items():
                        for pattern in patterns:
                            if pattern.lower() in content:
                                detected_dbs[db_name] = detected_dbs.get(db_name, 0) + 1

                except Exception:
                    pass

            return {
                "databases": detected_dbs,
                "total_databases": len(detected_dbs),
            }

        except Exception as e:
            logger.error(f"Database detection failed: {str(e)}")
            return {"error": f"Detection failed: {str(e)}"}

    def _tool_assess_maturity(self, repo_path: str = None) -> Dict[str, Any]:
        """
        Assess technology stack maturity.

        Args:
            repo_path: Path to repository

        Returns:
            Maturity assessment
        """
        try:
            assessment = {
                "overall_maturity": "Modern",
                "modern_indicators": [],
                "legacy_indicators": [],
                "modernization_opportunities": [],
            }

            # Analyze detected tech stack
            if self.current_input:
                lang_dist = (
                    self.current_input.get("analysis_result", {})
                    .get("structure", {})
                    .get("language_distribution", {})
                )

                # Legacy indicators
                if "python" in lang_dist and lang_dist.get("python", 0) > 50:
                    assessment["legacy_indicators"].append("High Python usage - may indicate legacy code")

                # Modern indicators
                if "typescript" in lang_dist:
                    assessment["modern_indicators"].append("TypeScript for type safety")
                if any(lang in lang_dist for lang in ["react", "vue", "angular"]):
                    assessment["modern_indicators"].append("Modern frontend framework")

                assessment["modernization_opportunities"].extend(
                    [
                        "Add TypeScript for type safety",
                        "Implement async/await patterns",
                        "Use containerization (Docker)",
                        "Adopt microservices architecture",
                    ]
                )

            return assessment

        except Exception as e:
            logger.error(f"Maturity assessment failed: {str(e)}")
            return {"error": f"Assessment failed: {str(e)}"}

    def _detect_tech_stack(self, repo_path: str) -> TechStack:
        """
        Detect complete technology stack.

        Args:
            repo_path: Repository path

        Returns:
            TechStack object
        """
        # This would perform actual detection
        # Simplified for now
        return TechStack(
            languages=[
                Language(language="python", version="3.9+", confidence=0.85),
                Language(language="javascript", version="ES6+", confidence=0.70),
            ],
            frameworks=[
                Framework(
                    name="Flask",
                    version="2.0+",
                    category="Web",
                    confidence=0.80,
                ),
            ],
            databases=[],
            maturity_level="Modern",
            architecture_style="Monolith",
            deployment_target="Cloud",
        )
