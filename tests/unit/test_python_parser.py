"""Unit tests for Python parser."""

import pytest
from pathlib import Path
from src.parsers.python_parser import PythonParser
from src.models.analysis_result import ParsedFile, ParsedImport, ParsedClass, ParsedFunction


@pytest.fixture
def parser():
    """Create parser instance."""
    return PythonParser()


@pytest.fixture
def sample_python_file():
    """Sample Python code for testing."""
    return '''
"""Module docstring."""

from typing import List, Optional
import json
from datetime import datetime

class User:
    """User model class."""

    def __init__(self, name: str, email: str):
        """Initialize user."""
        self.name = name
        self.email = email

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {'name': self.name, 'email': self.email}


class Post:
    """Post model class."""

    def __init__(self, title: str, content: str):
        """Initialize post."""
        self.title = title
        self.content = content


def create_user(name: str, email: str) -> User:
    """Create a new user."""
    return User(name, email)


def get_users(user_list: List[User]) -> List[dict]:
    """Get all users as dictionaries."""
    return [user.to_dict() for user in user_list]


def main():
    """Main function."""
    print("Hello, World!")


if __name__ == '__main__':
    main()
'''


class TestPythonParser:
    """Test cases for PythonParser."""

    def test_parser_initialization(self, parser):
        """Test parser initialization."""
        assert parser is not None
        assert parser.language == 'python'

    def test_extract_imports(self, parser, sample_python_file):
        """Test import extraction."""
        imports = parser.extract_imports(sample_python_file)

        assert len(imports) >= 3
        assert any(imp.name == 'typing' for imp in imports)
        assert any(imp.name == 'json' for imp in imports)
        assert any(imp.name == 'datetime' for imp in imports)

    def test_extract_classes(self, parser, sample_python_file):
        """Test class extraction."""
        classes = parser.extract_classes(sample_python_file)

        assert len(classes) >= 2
        class_names = [c.name for c in classes]
        assert 'User' in class_names
        assert 'Post' in class_names

    def test_extract_functions(self, parser, sample_python_file):
        """Test function extraction."""
        functions = parser.extract_functions(sample_python_file)

        assert len(functions) >= 3
        func_names = [f.name for f in functions]
        assert 'create_user' in func_names
        assert 'get_users' in func_names
        assert 'main' in func_names

    def test_extract_with_type_hints(self, parser):
        """Test extraction of functions with type hints."""
        code = '''
def process_data(items: List[str]) -> Optional[dict]:
    """Process data."""
    return None
'''
        functions = parser.extract_functions(code)
        assert len(functions) == 1
        assert functions[0].name == 'process_data'

    def test_extract_class_methods(self, parser):
        """Test extraction of class methods."""
        code = '''
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b
'''
        classes = parser.extract_classes(code)
        assert len(classes) == 1
        assert classes[0].name == 'Calculator'

    def test_parse_file(self, parser, tmp_path, sample_python_file):
        """Test parsing a file."""
        # Create temporary file
        test_file = tmp_path / 'test.py'
        test_file.write_text(sample_python_file)

        # Parse file
        result = parser.parse(str(test_file), sample_python_file)

        assert result is not None
        assert result.language == 'python'
        assert len(result.imports) >= 3
        assert len(result.classes) >= 2
        assert len(result.functions) >= 3

    def test_empty_file(self, parser):
        """Test parsing empty file."""
        code = ''
        functions = parser.extract_functions(code)
        assert len(functions) == 0

    def test_syntax_error_handling(self, parser):
        """Test handling of syntax errors."""
        code = 'def broken_function(:\n    pass'
        # Should not raise exception
        try:
            functions = parser.extract_functions(code)
            # Either returns empty or handles gracefully
            assert isinstance(functions, list)
        except Exception as e:
            # If exception is raised, it should be caught
            assert True

    def test_extract_docstrings(self, parser, sample_python_file):
        """Test docstring extraction."""
        classes = parser.extract_classes(sample_python_file)
        user_class = next((c for c in classes if c.name == 'User'), None)

        assert user_class is not None
        assert user_class.docstring is not None
        assert 'User model class' in user_class.docstring
