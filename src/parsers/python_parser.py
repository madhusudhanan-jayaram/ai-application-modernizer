"""
Python Parser - Parses Python source files using AST module and tree-sitter.
Extracts functions, classes, imports, and provides code structure analysis.
"""

import ast
import re
from typing import List, Optional

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


class PythonParser(BaseParser):
    """
    Python code parser using AST module.

    Parses Python source code to extract:
    - Import statements
    - Class definitions (with methods)
    - Function definitions
    - Docstrings
    - Type hints
    """

    def __init__(self):
        """Initialize Python parser."""
        super().__init__("python")
        logger.debug("Python parser initialized")

    def parse(self, file_path: str, content: str) -> ParsedFile:
        """
        Parse Python source file.

        Args:
            file_path: Path to Python file
            content: File contents

        Returns:
            ParsedFile with extracted structure

        Raises:
            ParsingError: If parsing fails
        """
        logger.debug(f"Parsing Python file: {file_path}")

        try:
            # Parse AST
            tree = ast.parse(content)

            # Extract structure
            imports = self.extract_imports(content)
            classes = self.extract_classes(content)
            functions = self.extract_functions(content)

            # Count lines
            total_lines = self.count_lines(content)

            # Get module docstring
            docstring = self._get_module_docstring(tree)

            # Collect any errors
            errors = self.validate_syntax(content)

            parsed_file = ParsedFile(
                file_path=file_path,
                language="python",
                content=content,
                imports=imports,
                classes=classes,
                functions=functions,
                total_lines=total_lines,
                docstring=docstring,
                errors=errors,
            )

            logger.debug(
                f"✓ Parsed Python file: {len(classes)} classes, "
                f"{len(functions)} functions, {len(imports)} imports"
            )
            return parsed_file

        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {str(e)}")
            raise ParsingError(f"Python syntax error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Error parsing Python file: {str(e)}")
            raise ParsingError(f"Python parsing error: {str(e)}") from e

    def extract_imports(self, content: str) -> List[ParsedImport]:
        """
        Extract import statements from Python code.

        Args:
            content: Source code

        Returns:
            List of parsed imports
        """
        imports = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            ParsedImport(
                                module=alias.name,
                                items=[alias.name],
                                alias=alias.asname,
                                is_relative=False,
                            )
                        )

                elif isinstance(node, ast.ImportFrom):
                    items = []
                    for alias in node.names:
                        items.append(alias.name)

                    imports.append(
                        ParsedImport(
                            module=node.module or "",
                            items=items,
                            alias=None,
                            is_relative=node.level > 0,
                        )
                    )

        except Exception as e:
            logger.warning(f"Error extracting imports: {str(e)}")

        return imports

    def extract_classes(self, content: str) -> List[ParsedClass]:
        """
        Extract class definitions from Python code.

        Args:
            content: Source code

        Returns:
            List of parsed classes with methods
        """
        classes = []

        try:
            tree = ast.parse(content)
            lines = content.split("\n")

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract methods
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(
                                self._function_from_ast(item, lines, node.lineno)
                            )

                    # Get docstring
                    docstring = ast.get_docstring(node)

                    # Get parent class
                    parent_class = None
                    if node.bases and len(node.bases) > 0:
                        parent_class = self._expr_to_str(node.bases[0])

                    classes.append(
                        ParsedClass(
                            name=node.name,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            methods=methods,
                            parent_class=parent_class,
                            docstring=docstring,
                            is_public=not node.name.startswith("_"),
                        )
                    )

        except Exception as e:
            logger.warning(f"Error extracting classes: {str(e)}")

        return classes

    def extract_functions(self, content: str) -> List[ParsedFunction]:
        """
        Extract top-level function definitions.

        Args:
            content: Source code

        Returns:
            List of parsed functions
        """
        functions = []

        try:
            tree = ast.parse(content)
            lines = content.split("\n")

            # Only get top-level functions (not methods)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    functions.append(self._function_from_ast(node, lines, 0))

        except Exception as e:
            logger.warning(f"Error extracting functions: {str(e)}")

        return functions

    def validate_syntax(self, content: str) -> List[str]:
        """
        Validate Python syntax.

        Args:
            content: Source code

        Returns:
            List of syntax errors (empty if valid)
        """
        errors = []

        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append(
                f"Syntax error at line {e.lineno}: {e.msg} (offset {e.offset})"
            )
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")

        return errors

    def _function_from_ast(
        self, node: ast.FunctionDef, lines: List[str], class_line: int = 0
    ) -> ParsedFunction:
        """
        Create ParsedFunction from AST FunctionDef node.

        Args:
            node: AST FunctionDef node
            lines: Source code lines
            class_line: Line number of parent class (0 for module-level)

        Returns:
            ParsedFunction
        """
        # Extract parameters
        params = []
        for arg in node.args.args:
            params.append(arg.arg)

        # Get return type annotation
        return_type = None
        if node.returns:
            return_type = self._expr_to_str(node.returns)

        # Get docstring
        docstring = ast.get_docstring(node)

        # Build signature
        signature = f"def {node.name}({', '.join(params)})"
        if return_type:
            signature += f" -> {return_type}"
        signature += ":"

        return ParsedFunction(
            name=node.name,
            signature=signature,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            params=params,
            return_type=return_type,
            docstring=docstring,
            is_public=not node.name.startswith("_"),
        )

    def _get_module_docstring(self, tree: ast.Module) -> Optional[str]:
        """
        Extract module-level docstring.

        Args:
            tree: AST module

        Returns:
            Module docstring or None
        """
        return ast.get_docstring(tree)

    def _expr_to_str(self, expr: ast.expr) -> str:
        """
        Convert AST expression to string representation.

        Args:
            expr: AST expression

        Returns:
            String representation
        """
        if isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.Constant):
            return repr(expr.value)
        elif isinstance(expr, ast.Attribute):
            return f"{self._expr_to_str(expr.value)}.{expr.attr}"
        elif isinstance(expr, ast.Subscript):
            return f"{self._expr_to_str(expr.value)}[{self._expr_to_str(expr.slice)}]"
        else:
            try:
                return ast.unparse(expr)
            except Exception:
                return "unknown"
