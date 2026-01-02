"""
JavaScript/TypeScript Parser - Parses JS/TS files to extract structure.
Supports ES6+ syntax, classes, arrow functions, and TypeScript.
"""

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


class JavaScriptParser(BaseParser):
    """
    JavaScript/TypeScript code parser using regex-based analysis.

    Parses JavaScript/TypeScript source code to extract:
    - Import statements (ES6 import, require, dynamic import)
    - Class definitions (with methods)
    - Function definitions (regular, arrow, async)
    - Export statements
    - Type annotations (TypeScript)
    """

    def __init__(self):
        """Initialize JavaScript parser."""
        super().__init__("javascript")
        logger.debug("JavaScript/TypeScript parser initialized")

    def parse(self, file_path: str, content: str) -> ParsedFile:
        """
        Parse JavaScript/TypeScript source file.

        Args:
            file_path: Path to JS/TS file
            content: File contents

        Returns:
            ParsedFile with extracted structure

        Raises:
            ParsingError: If parsing fails
        """
        logger.debug(f"Parsing JavaScript file: {file_path}")

        try:
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
                language="javascript",
                content=content,
                imports=imports,
                classes=classes,
                functions=functions,
                total_lines=total_lines,
                errors=errors,
            )

            logger.debug(
                f"✓ Parsed JavaScript file: {len(classes)} classes, "
                f"{len(functions)} functions, {len(imports)} imports"
            )
            return parsed_file

        except Exception as e:
            logger.error(f"Error parsing JavaScript file: {str(e)}")
            raise ParsingError(f"JavaScript parsing error: {str(e)}") from e

    def extract_imports(self, content: str) -> List[ParsedImport]:
        """
        Extract import statements from JavaScript/TypeScript code.

        Args:
            content: Source code

        Returns:
            List of parsed imports
        """
        imports = []

        # Remove comments to avoid false matches
        content_no_comments = self._remove_comments(content)

        # Pattern 1: ES6 import - import { Item1, Item2 } from 'module';
        es6_pattern = r"import\s+(?:{([^}]+)}|\s*(\w+))\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(es6_pattern, content_no_comments):
            named_imports = match.group(1)
            default_import = match.group(2)
            module = match.group(3)

            if named_imports:
                items = [item.strip().split(" as ")[0] for item in named_imports.split(",")]
            elif default_import:
                items = [default_import]
            else:
                items = []

            imports.append(
                ParsedImport(
                    module=module,
                    items=items,
                    alias=None,
                    is_relative=module.startswith("."),
                )
            )

        # Pattern 2: ES6 import all - import * as namespace from 'module';
        import_all_pattern = r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(import_all_pattern, content_no_comments):
            alias = match.group(1)
            module = match.group(2)

            imports.append(
                ParsedImport(
                    module=module,
                    items=["*"],
                    alias=alias,
                    is_relative=module.startswith("."),
                )
            )

        # Pattern 3: CommonJS require - const module = require('module');
        require_pattern = r"(?:const|var|let)\s+(\w+)\s*=\s*require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
        for match in re.finditer(require_pattern, content_no_comments):
            alias = match.group(1)
            module = match.group(2)

            imports.append(
                ParsedImport(
                    module=module,
                    items=[alias],
                    alias=None,
                    is_relative=module.startswith("."),
                )
            )

        return imports

    def extract_classes(self, content: str) -> List[ParsedClass]:
        """
        Extract class definitions from JavaScript/TypeScript code.

        Args:
            content: Source code

        Returns:
            List of parsed classes with methods
        """
        classes = []

        # Remove comments
        content_no_comments = self._remove_comments(content)

        # Pattern: class ClassName [extends ParentClass]
        class_pattern = r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?"

        for match in re.finditer(class_pattern, content_no_comments):
            class_name = match.group(1)
            parent_class = match.group(2)
            line_num = content[: match.start()].count("\n") + 1

            # Find class body
            class_start = match.end()
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

                class_body = content[brace_pos + 1 : pos - 1]

                # Extract methods
                methods = self._extract_methods_from_class(class_body, line_num)
            else:
                methods = []

            classes.append(
                ParsedClass(
                    name=class_name,
                    line_start=line_num,
                    line_end=line_num + class_body.count("\n") if brace_pos != -1 else line_num,
                    methods=methods,
                    parent_class=parent_class,
                    docstring=None,
                    is_public="export" in content[max(0, match.start() - 10) : match.start()],
                )
            )

        return classes

    def extract_functions(self, content: str) -> List[ParsedFunction]:
        """
        Extract function definitions from JavaScript/TypeScript code.

        Args:
            content: Source code

        Returns:
            List of parsed functions
        """
        functions = []

        # Remove comments
        content_no_comments = self._remove_comments(content)

        # Pattern 1: Regular function - function name(params) or async function name(params)
        func_pattern = r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)"
        for match in re.finditer(func_pattern, content_no_comments):
            func_name = match.group(1)
            params_str = match.group(2)
            line_num = content[: match.start()].count("\n") + 1

            params = self._parse_params(params_str)

            functions.append(
                ParsedFunction(
                    name=func_name,
                    signature=f"function {func_name}({params_str})",
                    line_start=line_num,
                    line_end=line_num,
                    params=params,
                    return_type=None,  # TypeScript would have return type
                    docstring=None,
                    is_public="export" in content[max(0, match.start() - 20) : match.start()],
                )
            )

        # Pattern 2: Arrow functions - const name = (params) => or const name = async (params) =>
        arrow_pattern = r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>"
        for match in re.finditer(arrow_pattern, content_no_comments):
            func_name = match.group(1)
            params_str = match.group(2)
            line_num = content[: match.start()].count("\n") + 1

            params = self._parse_params(params_str)

            functions.append(
                ParsedFunction(
                    name=func_name,
                    signature=f"const {func_name} = ({params_str}) =>",
                    line_start=line_num,
                    line_end=line_num,
                    params=params,
                    return_type=None,
                    docstring=None,
                    is_public="export" in content[max(0, match.start() - 20) : match.start()],
                )
            )

        return functions

    def validate_syntax(self, content: str) -> List[str]:
        """
        Validate JavaScript/TypeScript syntax.

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

        # Check for unclosed strings (basic check)
        single_quotes = content.count("'") - content.count("\\'")
        double_quotes = content.count('"') - content.count('\\"')

        if single_quotes % 2 != 0:
            errors.append("Unclosed single quote string")

        if double_quotes % 2 != 0:
            errors.append("Unclosed double quote string")

        return errors

    def _remove_comments(self, content: str) -> str:
        """
        Remove comments from JavaScript/TypeScript code.

        Args:
            content: Source code

        Returns:
            Code without comments
        """
        # Remove // comments
        content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)

        # Remove /* */ comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        return content

    def _extract_methods_from_class(self, class_body: str, start_line: int) -> List[ParsedFunction]:
        """
        Extract methods from class body.

        Args:
            class_body: Class body content
            start_line: Starting line number

        Returns:
            List of parsed methods
        """
        methods = []

        # Remove comments
        body_no_comments = self._remove_comments(class_body)

        # Pattern: methodName(params) or async methodName(params)
        method_pattern = r"(?:async\s+)?(\w+)\s*\(([^)]*)\)"

        for match in re.finditer(method_pattern, body_no_comments):
            method_name = match.group(1)

            # Skip if it looks like a loop or conditional
            if method_name in ["if", "for", "while", "switch", "catch"]:
                continue

            params_str = match.group(2)
            line_num = start_line + class_body[: match.start()].count("\n")

            params = self._parse_params(params_str)

            methods.append(
                ParsedFunction(
                    name=method_name,
                    signature=f"{method_name}({params_str})",
                    line_start=line_num,
                    line_end=line_num,
                    params=params,
                    return_type=None,
                    docstring=None,
                    is_public=not method_name.startswith("_"),
                )
            )

        return methods

    def _parse_params(self, params_str: str) -> List[str]:
        """
        Parse parameter string to extract parameter names.

        Args:
            params_str: Parameter string like 'a, b, c' or 'a: Type, b: Type'

        Returns:
            List of parameter names
        """
        params = []

        if not params_str.strip():
            return params

        for param in params_str.split(","):
            param = param.strip()
            if not param:
                continue

            # Handle TypeScript type annotations (name: Type)
            if ":" in param:
                name = param.split(":")[0].strip()
            else:
                name = param

            # Handle default values (name = value)
            if "=" in name:
                name = name.split("=")[0].strip()

            # Handle destructuring (not parsing internal structure)
            if name.startswith("{") or name.startswith("["):
                name = "destructured"

            if name:
                params.append(name)

        return params
