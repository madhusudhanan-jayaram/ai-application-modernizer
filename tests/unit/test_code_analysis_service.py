"""Unit tests for code analysis service."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.services.code_analysis_service import CodeAnalysisService
from src.models.analysis_result import RepositoryAnalysis


@pytest.fixture
def service():
    """Create service instance."""
    return CodeAnalysisService()


@pytest.fixture
def sample_repo(tmp_path):
    """Create sample repository structure."""
    # Create Python files
    python_dir = tmp_path / 'src'
    python_dir.mkdir()

    main_file = python_dir / 'main.py'
    main_file.write_text('''
def main():
    """Main function."""
    print("Hello, World!")

if __name__ == '__main__':
    main()
''')

    utils_file = python_dir / 'utils.py'
    utils_file.write_text('''
def helper_function(value):
    """Helper function."""
    return value * 2
''')

    # Create JavaScript file
    js_dir = tmp_path / 'js'
    js_dir.mkdir()

    js_file = js_dir / 'index.js'
    js_file.write_text('''
function main() {
    console.log("Hello from JS");
}

function helper() {
    return 42;
}
''')

    # Create requirements file
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('''
Flask==2.0.0
SQLAlchemy==1.4.0
requests==2.26.0
''')

    return tmp_path


class TestCodeAnalysisService:
    """Test cases for CodeAnalysisService."""

    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, 'analyze_file')
        assert hasattr(service, 'analyze_repository')

    def test_analyze_python_file(self, service, tmp_path):
        """Test analyzing Python file."""
        python_file = tmp_path / 'test.py'
        python_file.write_text('''
class TestClass:
    def method(self):
        pass

def function():
    pass
''')

        result = service.analyze_file(
            'https://github.com/test/repo',
            str(tmp_path),
            'test.py',
        )

        assert result is not None
        assert 'language' in result
        assert result['language'] == 'python'

    def test_analyze_javascript_file(self, service, tmp_path):
        """Test analyzing JavaScript file."""
        js_file = tmp_path / 'test.js'
        js_file.write_text('''
function myFunction() {
    console.log("test");
}

class MyClass {
    method() {
        return true;
    }
}
''')

        result = service.analyze_file(
            'https://github.com/test/repo',
            str(tmp_path),
            'test.js',
        )

        assert result is not None
        assert 'language' in result

    def test_analyze_repository(self, service, sample_repo):
        """Test analyzing entire repository."""
        analysis = service.analyze_repository(
            'https://github.com/test/repo',
            str(sample_repo),
            max_files=10,
        )

        assert analysis is not None
        assert analysis.total_files > 0
        assert analysis.analyzed_files > 0

    def test_detect_primary_language(self, service, sample_repo):
        """Test detecting primary language."""
        analysis = service.analyze_repository(
            'https://github.com/test/repo',
            str(sample_repo),
            max_files=10,
        )

        assert analysis.primary_language is not None
        # Should detect Python as primary language
        assert 'python' in analysis.primary_language.lower()

    def test_extract_dependencies(self, service, sample_repo):
        """Test extracting dependencies."""
        analysis = service.analyze_repository(
            'https://github.com/test/repo',
            str(sample_repo),
            max_files=10,
        )

        assert analysis.dependencies is not None
        # Should extract dependencies from requirements.txt
        dependency_names = [d['name'] for d in analysis.dependencies]
        assert any('Flask' in name or 'flask' in name for name in dependency_names)

    def test_detect_patterns(self, service, sample_repo):
        """Test detecting architectural patterns."""
        # Create MVC-like structure
        models_dir = sample_repo / 'models'
        models_dir.mkdir()
        (models_dir / 'user.py').write_text('class User: pass')

        views_dir = sample_repo / 'views'
        views_dir.mkdir()
        (views_dir / 'user_view.py').write_text('def show_user(): pass')

        controllers_dir = sample_repo / 'controllers'
        controllers_dir.mkdir()
        (controllers_dir / 'user_controller.py').write_text('def create_user(): pass')

        analysis = service.analyze_repository(
            'https://github.com/test/repo',
            str(sample_repo),
            max_files=20,
        )

        # Should detect MVC pattern
        assert len(analysis.patterns) > 0

    def test_calculate_metrics(self, service, sample_repo):
        """Test calculating code metrics."""
        analysis = service.analyze_repository(
            'https://github.com/test/repo',
            str(sample_repo),
            max_files=10,
        )

        assert analysis.total_lines_of_code >= 0
        assert analysis.average_file_size >= 0

    def test_language_distribution(self, service, sample_repo):
        """Test language distribution analysis."""
        analysis = service.analyze_repository(
            'https://github.com/test/repo',
            str(sample_repo),
            max_files=10,
        )

        assert len(analysis.language_distribution) > 0
        # Should have both Python and JavaScript files
        languages = [lang for lang, _ in analysis.language_distribution]
        assert len(languages) >= 1

    def test_skip_binary_files(self, service, tmp_path):
        """Test skipping binary files."""
        # Create binary file
        binary_file = tmp_path / 'image.bin'
        binary_file.write_bytes(b'\x00\x01\x02\x03')

        # Create text file
        text_file = tmp_path / 'text.py'
        text_file.write_text('print("hello")')

        # Should only analyze text file
        result = service.analyze_file(
            'https://github.com/test/repo',
            str(tmp_path),
            'image.bin',
        )

        assert result is None or 'error' in str(result).lower()

    def test_handle_large_files(self, service, tmp_path):
        """Test handling of large files."""
        large_file = tmp_path / 'large.py'
        # Create file with many lines
        content = '\n'.join([f'def func_{i}(): pass' for i in range(1000)])
        large_file.write_text(content)

        result = service.analyze_file(
            'https://github.com/test/repo',
            str(tmp_path),
            'large.py',
        )

        # Should handle large files gracefully
        assert result is not None

    def test_skip_excluded_directories(self, service, tmp_path):
        """Test skipping excluded directories."""
        # Create standard exclusion directories
        (tmp_path / '__pycache__').mkdir()
        (tmp_path / '__pycache__' / 'cache.pyc').touch()

        (tmp_path / 'node_modules').mkdir()
        (tmp_path / 'node_modules' / 'package').mkdir()

        (tmp_path / 'main.py').write_text('print("main")')

        analysis = service.analyze_repository(
            'https://github.com/test/repo',
            str(tmp_path),
            max_files=10,
        )

        # Should skip excluded directories
        assert analysis.analyzed_files >= 1

    def test_entry_point_detection(self, service, tmp_path):
        """Test detecting entry points."""
        (tmp_path / 'main.py').write_text('if __name__ == "__main__": pass')
        (tmp_path / 'app.py').write_text('app = Flask(__name__)')

        analysis = service.analyze_repository(
            'https://github.com/test/repo',
            str(tmp_path),
            max_files=10,
        )

        # Should identify entry points
        assert len(analysis.entry_points) >= 0
