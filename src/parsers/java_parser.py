"""
Java Parser - Parses Java source files using javalang library.
Extracts classes, methods, imports, and provides code structure analysis.
"""

import re
from typing import List, Optional

try:
    import javalang
except ImportError:
    javalang = None

from src.parsers.base_parser import (
    BaseParser,
    ParsedClass,
    ParsedFile,
    ParsedFunction,
    ParsedImport,
    ParsingError,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class JavaParser(BaseParser):
    """
    Java code parser using javalang library.

    Parses Java source code to extract:
    - Import statements
    - Class definitions (with methods)
    - Method definitions
    - Visibility modifiers
    - Type information
    """

    def __init__(self):
        """Initialize Java parser."""
        super().__init__("java")
        if javalang is None:
            logger.warning("javalang not installed, falling back to regex parsing")
        logger.debug("Java parser initialized")

    def parse(self, file_path: str, content: str) -> ParsedFile:
        """
        Parse Java source file.

        Args:
            file_path: Path to Java file
            content: File contents

        Returns:
            ParsedFile with extracted structure

        Raises:
            ParsingError: If parsing fails
        """
        logger.debug(f"Parsing Java file: {file_path}")

        try:
            # Try parsing with javalang if available
            if javalang:
                tree = javalang.parse.parse(content)
            else:
                logger.debug("Using regex-based Java parsing (javalang not available)")
                tree = None

            # Extract structure
            imports = self.extract_imports(content)
            classes = self.extract_classes(content)
            functions = self.extract_functions(content)

            # Count lines
            total_lines = self.count_lines(content)

            # Collect any errors
            errors = self.validate_syntax(content)

            parsed_file = ParsedFile(
                file_path=file_path,
                language="java",
                content=content,
                imports=imports,
                classes=classes,
                functions=functions,
                total_lines=total_lines,
                errors=errors,
            )

            logger.debug(
                f"✓ Parsed Java file: {len(classes)} classes, "
                f"{len(functions)} functions, {len(imports)} imports"
            )
            return parsed_file

        except Exception as e:
            logger.error(f"Error parsing Java file: {str(e)}")
            raise ParsingError(f"Java parsing error: {str(e)}") from e

    def extract_imports(self, content: str) -> List[ParsedImport]:
        """
        Extract import statements from Java code.

        Args:
            content: Source code

        Returns:
            List of parsed imports
        """
        imports = []

        # Regex pattern for import statements
        # Matches: import java.util.List; or import static java.lang.Math.*;
        pattern = r"^(?:import\s+(?:static\s+)?)([\w\.]+(?:\.\*)?)\s*;?$"

        for line in content.split("\n"):
            line = line.strip()
            match = re.match(pattern, line)
            if match:
                import_path = match.group(1)

                # Check if it's a wildcard import
                is_wildcard = import_path.endswith(".*")
                if is_wildcard:
                    import_path = import_path[:-2]

                # Parse module and items
                parts = import_path.split(".")
                if is_wildcard:
                    items = ["*"]
                    module = import_path
                else:
                    items = [parts[-1]] if parts else []
                    module = ".".join(parts[:-1]) if len(parts) > 1 else parts[0]

                imports.append(
                    ParsedImport(
                        module=module,
                        items=items,
                        alias=None,
                        is_relative=False,
                    )
                )

        return imports

    def extract_classes(self, content: str) -> List[ParsedClass]:
        """
        Extract class definitions from Java code.

        Args:
            content: Source code

        Returns:
            List of parsed classes with methods
        """
        classes = []

        if javalang:
            try:
                tree = javalang.parse.parse(content)

                for class_node in tree.types:
                    if hasattr(class_node, "name"):
                        # Extract methods
                        methods = []
                        if hasattr(class_node, "methods"):
                            for method in class_node.methods:
                                methods.append(
                                    self._method_from_javalang(method, content)
                                )

                        # Get parent class
                        parent_class = None
                        if hasattr(class_node, "superclass") and class_node.superclass:
                            parent_class = str(class_node.superclass)

                        classes.append(
                            ParsedClass(
                                name=class_node.name,
                                line_start=getattr(class_node, "position", (1, 0))[0],
                                line_end=getattr(class_node, "position", (1, 0))[0],
                                methods=methods,
                                parent_class=parent_class,
                                docstring=None,  # Would need javadoc parsing
                                is_public="public" in class_node.modifiers,
                            )
                        )

            except Exception as e:
                logger.warning(f"Error parsing with javalang: {str(e)}, using regex")
                classes = self._extract_classes_regex(content)
        else:
            classes = self._extract_classes_regex(content)

        return classes

    def extract_functions(self, content: str) -> List[ParsedFunction]:
        """
        Extract top-level method definitions.

        Args:
            content: Source code

        Returns:
            List of parsed functions
        """
        # Java is class-based, so we return empty for "top-level" functions
        # All methods are part of classes
        return []

    def validate_syntax(self, content: str) -> List[str]:
        """
        Validate Java syntax.

        Args:
            content: Source code

        Returns:
            List of syntax errors (empty if valid)
        """
        errors = []

        # Check for common syntax issues
        if content.count("{") != content.count("}"):
            errors.append("Mismatched braces { }")

        if content.count("[") != content.count("]"):
            errors.append("Mismatched brackets [ ]")

        if content.count("(") != content.count(")"):
            errors.append("Mismatched parentheses ( )")

        # If javalang available, do full parse validation
        if javalang:
            try:
                javalang.parse.parse(content)
            except Exception as e:
                errors.append(f"Parse error: {str(e)}")

        return errors

    def _extract_classes_regex(self, content: str) -> List[ParsedClass]:
        """
        Extract classes using regex (fallback when javalang unavailable).

        Args:
            content: Source code

        Returns:
            List of parsed classes
        """
        classes = []

        # Pattern: [modifiers] class ClassName [extends SuperClass]
        class_pattern = r"(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?"

        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            parent_class = match.group(2)
            line_num = content[: match.start()].count("\n") + 1

            # Extract methods in this class
            class_start = match.start()
            # Find the opening brace
            brace_pos = content.find("{", class_start)
            if brace_pos != -1:
                # Find matching closing brace
                brace_count = 1
                pos = brace_pos + 1
                while pos < len(content) and brace_count > 0:
                    if content[pos] == "{":
                        brace_count += 1
                    elif content[pos] == "}":
                        brace_count -= 1
                    pos += 1

                class_content = content[brace_pos + 1 : pos - 1]
                methods = self._extract_methods_regex(class_content, line_num)
            else:
                methods = []

            classes.append(
                ParsedClass(
                    name=class_name,
                    line_start=line_num,
                    line_end=line_num,
                    methods=methods,
                    parent_class=parent_class,
                    docstring=None,
                    is_public="public" in content[max(0, match.start() - 50) : match.start()],
                )
            )

        return classes

    def _extract_methods_regex(self, content: str, start_line: int) -> List[ParsedFunction]:
        """
        Extract methods from class content using regex.

        Args:
            content: Class body content
            start_line: Starting line number

        Returns:
            List of parsed methods
        """
        methods = []

        # Pattern: [modifiers] returnType methodName(params)
        method_pattern = r"(?:public|private|protected)?\s+(?:static\s+)?(\w[\w\[\]]*)\s+(\w+)\s*\(([^)]*)\)"

        for match in re.finditer(method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)

            # Parse parameters
            params = []
            if params_str.strip():
                for param in params_str.split(","):
                    # Extract parameter name (last token)
                    parts = param.strip().split()
                    if parts:
                        params.append(parts[-1])

            methods.append(
                ParsedFunction(
                    name=method_name,
                    signature=f"{return_type} {method_name}({params_str})",
                    line_start=start_line + content[: match.start()].count("\n"),
                    line_end=start_line + content[: match.end()].count("\n"),
                    params=params,
                    return_type=return_type,
                    docstring=None,
                    is_public="public" in content[max(0, match.start() - 50) : match.start()],
                )
            )

        return methods

    def _method_from_javalang(
        self, method: "javalang.tree.MethodDeclaration", content: str
    ) -> ParsedFunction:
        """
        Create ParsedFunction from javalang MethodDeclaration.

        Args:
            method: javalang method node
            content: Source code

        Returns:
            ParsedFunction
        """
        params = []
        if hasattr(method, "parameters"):
            for param in method.parameters:
                if hasattr(param, "name"):
                    params.append(param.name)

        return_type = str(method.return_type) if hasattr(method, "return_type") else "void"

        return ParsedFunction(
            name=method.name,
            signature=f"{return_type} {method.name}({', '.join(params)})",
            line_start=getattr(method, "position", (1, 0))[0],
            line_end=getattr(method, "position", (1, 0))[0],
            params=params,
            return_type=return_type,
            docstring=None,
            is_public="public" in method.modifiers,
        )
