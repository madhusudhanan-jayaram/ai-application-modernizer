"""
Base Parser - Abstract interface for code parsing.
Defines common interface for language-specific parsers.
Uses tree-sitter as primary parser with language-specific AST fallbacks.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ParsedFunction:
    """Parsed function/method definition."""

    name: str
    signature: str
    line_start: int
    line_end: int
    params: List[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    is_public: bool = True


@dataclass
class ParsedClass:
    """Parsed class definition."""

    name: str
    line_start: int
    line_end: int
    methods: List[ParsedFunction]
    parent_class: Optional[str] = None
    docstring: Optional[str] = None
    is_public: bool = True


@dataclass
class ParsedImport:
    """Parsed import statement."""

    module: str
    items: List[str]
    alias: Optional[str] = None
    is_relative: bool = False


@dataclass
class ParsedFile:
    """Complete parsed file structure."""

    file_path: str
    language: str
    content: str
    imports: List[ParsedImport]
    classes: List[ParsedClass]
    functions: List[ParsedFunction]
    total_lines: int
    docstring: Optional[str] = None
    errors: List[str] = None

    def __post_init__(self):
        """Initialize errors list if not provided."""
        if self.errors is None:
            self.errors = []


class BaseParser(ABC):
    """
    Abstract base class for code parsers.

    Subclasses implement language-specific parsing using:
    - tree-sitter for universal AST parsing
    - Language-specific AST modules for deeper analysis
    """

    def __init__(self, language: str):
        """
        Initialize parser for specific language.

        Args:
            language: Programming language (e.g., 'java', 'python')
        """
        self.language = language.lower()
        logger.debug(f"Initialized {self.__class__.__name__} for {self.language}")

    @abstractmethod
    def parse(self, file_path: str, content: str) -> ParsedFile:
        """
        Parse source code file.

        Args:
            file_path: Path to source file
            content: File contents as string

        Returns:
            ParsedFile with extracted structure
        """
        pass

    @abstractmethod
    def extract_imports(self, content: str) -> List[ParsedImport]:
        """
        Extract import statements from code.

        Args:
            content: Source code

        Returns:
            List of parsed imports
        """
        pass

    @abstractmethod
    def extract_classes(self, content: str) -> List[ParsedClass]:
        """
        Extract class definitions from code.

        Args:
            content: Source code

        Returns:
            List of parsed classes with methods
        """
        pass

    @abstractmethod
    def extract_functions(self, content: str) -> List[ParsedFunction]:
        """
        Extract top-level function definitions.

        Args:
            content: Source code

        Returns:
            List of parsed functions
        """
        pass

    def get_docstring(self, content: str, start_line: int) -> Optional[str]:
        """
        Extract docstring from code starting at given line.

        Args:
            content: Source code
            start_line: Line number where definition starts

        Returns:
            Docstring if found, None otherwise
        """
        lines = content.split("\n")
        if start_line >= len(lines):
            return None

        # Look for docstring after definition
        for i in range(start_line, min(start_line + 5, len(lines))):
            line = lines[i].strip()
            if '"""' in line or "'''" in line:
                return line
            if line and not line.startswith("#"):
                break

        return None

    def count_lines(self, content: str) -> int:
        """
        Count lines of code in content.

        Args:
            content: Source code

        Returns:
            Number of lines
        """
        return len(content.split("\n"))

    def validate_syntax(self, content: str) -> List[str]:
        """
        Validate source code syntax.

        Args:
            content: Source code

        Returns:
            List of syntax errors (empty if valid)
        """
        # Implement in subclasses
        return []


class ParsingError(Exception):
    """Raised when parsing fails."""

    pass


class UnsupportedLanguageError(ParsingError):
    """Raised when language is not supported."""

    pass
