"""
Parser Factory - Creates appropriate parser for detected language.
Uses file extensions and content analysis to detect programming language.
Provides graceful fallbacks for unsupported languages.
"""

from pathlib import Path
from typing import Optional

from src.parsers.base_parser import BaseParser, UnsupportedLanguageError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ParserFactory:
    """
    Factory for creating language-specific parsers.

    Maps file extensions and content patterns to parser classes.
    Supports:
    - Java (via tree-sitter + javalang)
    - Python (via tree-sitter + ast module)
    - JavaScript/TypeScript (via tree-sitter + esprima)
    - Graceful fallback for unsupported languages
    """

    # Language extensions mapping
    LANGUAGE_EXTENSIONS = {
        ".java": "java",
        ".py": "python",
        ".pyx": "python",
        ".pyi": "python",
        ".js": "javascript",
        ".ts": "javascript",
        ".jsx": "javascript",
        ".tsx": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".r": "r",
    }

    # Supported parsers (will expand as parsers are implemented)
    SUPPORTED_LANGUAGES = {
        "java",
        "python",
        "javascript",
    }

    def __init__(self):
        """Initialize parser factory."""
        logger.debug("Parser factory initialized")
        self._parser_cache = {}  # Cache instantiated parsers

    def detect_language_from_path(self, file_path: str) -> Optional[str]:
        """
        Detect language from file extension.

        Args:
            file_path: Path to source file

        Returns:
            Language name or None if not recognized
        """
        ext = Path(file_path).suffix.lower()
        language = self.LANGUAGE_EXTENSIONS.get(ext)

        if language:
            logger.debug(f"Detected language '{language}' from extension '{ext}'")
        else:
            logger.debug(f"Unknown file extension: {ext}")

        return language

    def detect_language_from_content(self, content: str, file_path: str = "") -> Optional[str]:
        """
        Detect language from file content patterns.

        Args:
            content: Source code content
            file_path: Optional file path (used as fallback)

        Returns:
            Language name or None if not detected
        """
        # Try extension first
        if file_path:
            language = self.detect_language_from_path(file_path)
            if language:
                return language

        # Pattern-based detection
        content_lower = content.lower()

        # Java patterns
        if any(pattern in content_lower for pattern in [
            "public class",
            "public interface",
            "import java.",
            "package ",
        ]):
            logger.debug("Detected Java from content patterns")
            return "java"

        # Python patterns
        if any(pattern in content_lower for pattern in [
            "import ",
            "from ",
            "def ",
            "class ",
            "if __name__",
            "#!/usr/bin/env python",
        ]):
            logger.debug("Detected Python from content patterns")
            return "python"

        # JavaScript patterns
        if any(pattern in content_lower for pattern in [
            "function ",
            "const ",
            "let ",
            "var ",
            "class ",
            "import ",
            "export ",
            "react",
            "vue",
            "angular",
        ]):
            logger.debug("Detected JavaScript from content patterns")
            return "javascript"

        logger.debug("Could not detect language from content")
        return None

    def get_parser(self, language: str) -> BaseParser:
        """
        Get parser instance for language.

        Args:
            language: Programming language name

        Returns:
            Parser instance

        Raises:
            UnsupportedLanguageError: If language not supported
        """
        language = language.lower().strip()

        # Check cache
        if language in self._parser_cache:
            logger.debug(f"Retrieved cached parser for {language}")
            return self._parser_cache[language]

        # Check if supported
        if language not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                f"Parser not yet implemented for language: {language}\n"
                f"Supported languages: {', '.join(sorted(self.SUPPORTED_LANGUAGES))}"
            )

        # Instantiate parser
        try:
            if language == "java":
                from src.parsers.java_parser import JavaParser
                parser = JavaParser()
            elif language == "python":
                from src.parsers.python_parser import PythonParser
                parser = PythonParser()
            elif language == "javascript":
                from src.parsers.javascript_parser import JavaScriptParser
                parser = JavaScriptParser()
            else:
                raise UnsupportedLanguageError(f"Unknown language: {language}")

            # Cache parser
            self._parser_cache[language] = parser
            logger.info(f"Created parser for {language}")
            return parser

        except ImportError as e:
            raise UnsupportedLanguageError(
                f"Parser for {language} not available: {str(e)}"
            ) from e

    def parse_file(self, file_path: str, content: str) -> "ParsedFile":  # noqa: F821
        """
        Parse file with automatic language detection.

        Args:
            file_path: Path to source file
            content: File contents

        Returns:
            ParsedFile with extracted structure

        Raises:
            UnsupportedLanguageError: If language not detected or supported
        """
        # Detect language
        language = self.detect_language_from_content(content, file_path)

        if not language:
            raise UnsupportedLanguageError(
                f"Could not detect language for file: {file_path}"
            )

        # Get parser and parse
        parser = self.get_parser(language)
        logger.info(f"Parsing {file_path} as {language}")

        return parser.parse(file_path, content)

    def is_supported(self, language: str) -> bool:
        """
        Check if language is supported.

        Args:
            language: Programming language name

        Returns:
            True if language is supported
        """
        return language.lower() in self.SUPPORTED_LANGUAGES

    def list_supported_languages(self) -> list:
        """
        Get list of supported languages.

        Returns:
            Sorted list of supported language names
        """
        return sorted(self.SUPPORTED_LANGUAGES)

    def get_supported_extensions(self) -> dict:
        """
        Get mapping of extensions to supported languages.

        Returns:
            Dictionary of {extension: language}
        """
        supported = {}
        for ext, lang in self.LANGUAGE_EXTENSIONS.items():
            if lang in self.SUPPORTED_LANGUAGES:
                supported[ext] = lang
        return supported


# Global parser factory instance
parser_factory = ParserFactory()
