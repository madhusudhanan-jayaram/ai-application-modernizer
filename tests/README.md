# Testing Suite for AI Application Modernizer

This directory contains comprehensive tests for the AI Application Modernizer project.

## Test Structure

```
tests/
├── unit/                          # Unit tests
│   ├── test_python_parser.py      # Python parser tests
│   ├── test_java_parser.py        # Java parser tests
│   ├── test_github_service.py     # GitHub service tests
│   ├── test_cache_manager.py      # Cache manager tests
│   ├── test_code_analysis_service.py  # Code analysis tests
│   └── test_base_agent.py         # Base agent tests
│
├── integration/                    # Integration tests
│   └── test_analysis_chain.py     # Analysis chain tests
│
├── fixtures/                       # Test fixtures and sample repos
│   └── sample_repos/
│       ├── python_flask/          # Sample Flask app
│       ├── java_spring/           # Sample Spring Boot app
│       └── javascript_node/       # Sample Express.js app
│
├── conftest.py                    # Pytest configuration and shared fixtures
└── README.md                      # This file
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/unit/test_python_parser.py
```

### Run tests with coverage
```bash
pytest --cov=src --cov-report=html
```

### Run specific test marker
```bash
pytest -m unit              # Run unit tests only
pytest -m integration       # Run integration tests only
pytest -m slow              # Run slow tests only
```

### Run tests in verbose mode
```bash
pytest -v
```

### Run tests with detailed output
```bash
pytest -vv -s
```

## Test Categories

### Unit Tests
Tests for individual components in isolation:
- **Parsers**: Python, Java, JavaScript
- **Services**: GitHub, Cache Manager, Code Analysis
- **Agents**: Base Agent
- **Models**: Data structures and validation

Run with: `pytest -m unit`

### Integration Tests
Tests for component interactions and chains:
- **Analysis Chain**: Repository analyzer + tech stack detector
- **Migration Chain**: Migration planner + code generator
- **Report Generation Chain**: Documentation generator + report assembly

Run with: `pytest -m integration`

### End-to-End Tests
Tests for complete workflows (manual testing recommended):
- Full workflow from GitHub URL to report generation
- Real repository analysis
- Code generation validation
- Report generation and export

## Test Fixtures

The `tests/fixtures/` directory contains sample repositories for testing:

1. **python_flask/** - Flask application with database models and REST API
   - Language: Python
   - Framework: Flask
   - Database: SQLAlchemy
   - Files: app.py, requirements.txt

2. **java_spring/** - Spring Boot REST API with controllers and services
   - Language: Java
   - Framework: Spring Boot
   - Architecture: MVC pattern
   - Files: UserController.java, UserService.java

3. **javascript_node/** - Express.js REST API server
   - Language: JavaScript/Node.js
   - Framework: Express
   - Files: server.js, package.json

### Using Fixtures in Tests
```python
def test_with_fixture(temp_repository):
    """Test using temporary repository fixture."""
    files = list(temp_repository.glob('**/*.py'))
    assert len(files) > 0
```

## Shared Fixtures (conftest.py)

Available fixtures for all tests:

- **mock_llm_service**: Mocked LLM service
- **mock_github_service**: Mocked GitHub service
- **mock_cache_manager**: Mocked cache manager
- **temp_repository**: Temporary Python project structure
- **test_python_code**: Sample Python code snippets
- **test_java_code**: Sample Java code snippets
- **test_javascript_code**: Sample JavaScript code snippets
- **test_repository_url**: Test GitHub URL
- **test_target_stack**: Test technology stack

## Test Configuration

### pytest.ini equivalent
Key configurations in conftest.py:
- Auto-marking tests by location (unit/integration/e2e)
- Shared fixture definitions
- Mock services for isolation

### Running with Options
```bash
# Run with pytest.ini settings
pytest --maxfail=1           # Stop after first failure
pytest -x                    # Exit on first error
pytest --lf                  # Run last failed
pytest --ff                  # Run failed first
```

## Coverage Reports

Generate and view coverage:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

Target coverage:
- Unit tests: >80%
- Integration tests: >70%
- Overall: >75%

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mocking**: Use mocks for external dependencies (GitHub, LLM)
3. **Fixtures**: Use conftest fixtures for common setup
4. **Naming**: Use descriptive test names (`test_feature_under_condition`)
5. **Assertions**: Use clear assertions with meaningful messages

## Common Test Patterns

### Testing with mocked services
```python
@patch('src.services.github_service.GitHubService')
def test_with_mock(mock_github):
    mock_github.parse_github_url.return_value = ('owner', 'repo')
    # Test code here
```

### Testing with temporary files
```python
def test_with_temp_file(tmp_path):
    test_file = tmp_path / 'test.py'
    test_file.write_text('code here')
    # Test code here
```

### Testing async code
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: pytest --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v2
```

## Troubleshooting

### Import errors
- Ensure `src/` is in Python path
- Check that all imports use absolute paths
- Verify `__init__.py` files exist in all packages

### Fixture issues
- Confirm fixture is defined in conftest.py
- Check fixture is in scope (module/session/function)
- Verify fixture parameter names match definition

### Mock issues
- Use `patch` decorator or context manager
- Verify mock return values are configured
- Check that mocked function is called

## Future Test Coverage

Planned test additions:
- [ ] LLM service integration tests
- [ ] Complete migration chain tests
- [ ] Report generation tests
- [ ] Streamlit component tests
- [ ] End-to-end workflow tests
- [ ] Performance benchmarks
- [ ] Error scenario tests

## Contributing Tests

When adding new features:
1. Write unit tests first
2. Add integration tests for component interactions
3. Include fixtures for sample data
4. Document test purpose and assumptions
5. Maintain >75% coverage
6. Run full test suite before submitting
