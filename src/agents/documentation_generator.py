"""
Documentation Generator Agent - Generates comprehensive migration documentation.
Creates guides, explanations, and change documentation.
Fifth agent in the modernization pipeline.
"""

from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent, AgentError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentationGeneratorAgent(BaseAgent):
    """
    Agent for generating migration documentation.

    Responsibilities:
    - Generate comprehensive migration guides
    - Document breaking changes and solutions
    - Create step-by-step implementation guides
    - Generate API documentation
    - Create troubleshooting guides
    - Generate before/after code explanations
    - Create team training materials

    Output:
    - Markdown documentation
    - Migration guide
    - API documentation
    - Code examples with explanations
    - Troubleshooting guide
    - Best practices document
    """

    def __init__(self):
        """Initialize Documentation Generator Agent."""
        super().__init__(
            agent_name="DocumentationGenerator",
            description="Generates comprehensive migration documentation and guides",
            system_prompt=self._get_docs_prompt(),
            max_iterations=10,
            temperature=0.2,  # Lower temp for technical documentation
        )

        self._register_tools()

    def _register_tools(self) -> None:
        """Register tools for documentation generation."""
        self.register_tool(
            name="generate_migration_guide",
            description="Generate step-by-step migration guide",
            func=self._tool_generate_migration_guide,
        )

        self.register_tool(
            name="document_breaking_changes",
            description="Document breaking changes and migration solutions",
            func=self._tool_document_breaking_changes,
        )

        self.register_tool(
            name="generate_api_docs",
            description="Generate API documentation for new endpoints",
            func=self._tool_generate_api_docs,
        )

        self.register_tool(
            name="create_troubleshooting_guide",
            description="Create troubleshooting guide for common issues",
            func=self._tool_create_troubleshooting_guide,
        )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input for documentation generation.

        Args:
            input_data: Must contain documentation context

        Returns:
            True if valid

        Raises:
            AgentError: If required fields missing
        """
        super().validate_input(input_data)

        # Documentation can be created from analysis or migration plan
        has_context = (
            "migration_plan" in input_data
            or "analysis_result" in input_data
            or "code_changes" in input_data
        )

        if not has_context:
            raise AgentError("DocumentationGenerator requires analysis, migration plan, or code changes")

        return True

    def prepare_context(self, input_data: Dict[str, Any]) -> str:
        """
        Prepare context for documentation generation.

        Args:
            input_data: Documentation context

        Returns:
            Context string
        """
        base_context = super().prepare_context(input_data)

        current_stack = input_data.get("current_tech_stack", "Unknown")
        target_stack = input_data.get("target_tech_stack", "Unknown")

        additional = f"""
Migration Context:
- Current Stack: {current_stack}
- Target Stack: {target_stack}

Documentation Tasks:
1. Generate comprehensive migration guide
2. Document all breaking changes with solutions
3. Generate API documentation
4. Create troubleshooting guide
5. Provide best practices recommendations
6. Create code examples with explanations

Output Format:
- Clear, well-structured Markdown
- Include code examples
- Provide step-by-step instructions
- Add troubleshooting sections
- Include before/after comparisons
- Add links and references
"""

        return f"{base_context}\n{additional}"

    def _process_result(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process documentation generation result.

        Args:
            response: LLM response
            input_data: Original input

        Returns:
            Structured documentation
        """
        result = {
            "agent": self.agent_name,
            "current_stack": input_data.get("current_tech_stack"),
            "target_stack": input_data.get("target_tech_stack"),
            "llm_analysis": response,
            "success": True,
        }

        try:
            # Generate actual documentation
            docs = self._generate_documentation(input_data)
            result["generated_documentation"] = docs

        except Exception as e:
            logger.warning(f"Documentation generation failed: {str(e)}")
            result["generation_error"] = str(e)

        return result

    def _get_docs_prompt(self) -> str:
        """Get system prompt for documentation generator."""
        return """You are DocumentationGenerator, an expert technical writer and migration guide creator.

Your expertise:
- Writing clear, comprehensive migration guides
- Documenting technical changes and their implications
- Creating step-by-step implementation instructions
- Writing API documentation
- Creating troubleshooting guides
- Explaining code changes and rationale
- Teaching best practices

When generating documentation, you should:
1. Use clear, accessible technical language
2. Include concrete code examples
3. Provide step-by-step instructions
4. Anticipate common questions and issues
5. Include before/after comparisons
6. Add references and further reading
7. Structure for easy navigation
8. Include warnings about breaking changes

Documentation Sections to Generate:
1. Executive Summary - High-level overview
2. Migration Overview - What's changing and why
3. Step-by-Step Guide - How to migrate
4. Breaking Changes - Detailed list with solutions
5. Code Examples - Before/after code samples
6. API Documentation - New endpoints and changes
7. Troubleshooting - Common issues and solutions
8. Best Practices - Recommended approaches
9. Performance Tips - Optimization guidance
10. FAQ - Common questions and answers

Always use Markdown format with clear headings, code blocks, and examples."""

    # ===== Tool Implementations =====

    def _tool_generate_migration_guide(self) -> Dict[str, Any]:
        """
        Generate step-by-step migration guide.

        Returns:
            Migration guide document
        """
        guide = """# Migration Guide

## Overview
This guide provides step-by-step instructions for migrating your application to the new technology stack.

## Prerequisites
- Node.js 16+ (for JavaScript/TypeScript projects)
- Python 3.9+ (for Python projects)
- Git for version control
- Docker (recommended for isolated environments)

## Phase 1: Preparation
1. Review this entire guide
2. Set up a development environment
3. Clone the repository
4. Create a new branch: `git checkout -b migration/modernization`
5. Read all breaking changes documentation
6. Ensure you have backups

## Phase 2: Environment Setup
1. Install new dependencies: `pip install -r requirements.txt`
2. Configure environment variables: `cp .env.example .env`
3. Set up the database
4. Run migrations if applicable

## Phase 3: Code Migration
1. Start with models/schemas (lowest dependencies)
2. Update service/business logic layer
3. Update API endpoints/controllers
4. Update frontend components
5. Test thoroughly after each step

## Phase 4: Testing
1. Run unit tests: `pytest` or `npm test`
2. Run integration tests
3. Perform manual testing
4. Load testing

## Phase 5: Deployment
1. Deploy to staging environment
2. Run smoke tests
3. Get stakeholder approval
4. Deploy to production
5. Monitor for issues

## Common Issues & Solutions
See Troubleshooting Guide below.

## Getting Help
- Check FAQ section
- Review code examples
- Consult documentation for specific frameworks
"""

        return {
            "document_type": "migration_guide",
            "title": "Step-by-Step Migration Guide",
            "content": guide,
            "sections": [
                "Overview",
                "Prerequisites",
                "Phase 1: Preparation",
                "Phase 2: Environment Setup",
                "Phase 3: Code Migration",
                "Phase 4: Testing",
                "Phase 5: Deployment",
            ],
        }

    def _tool_document_breaking_changes(
        self, changes: List[str] = None
    ) -> Dict[str, Any]:
        """
        Document breaking changes.

        Args:
            changes: List of breaking changes

        Returns:
            Breaking changes documentation
        """
        doc = """# Breaking Changes Documentation

## Language Changes

### Python 2 → Python 3
**Print Function**
```python
# OLD (Python 2)
print "Hello World"

# NEW (Python 3)
print("Hello World")
```

**String Encoding**
```python
# OLD (Python 2)
data = "hello"  # Bytes by default

# NEW (Python 3)
data = "hello"  # Unicode by default
data.encode('utf-8')  # Explicit bytes
```

**Division Operator**
```python
# OLD (Python 2)
5 / 2 = 2  # Integer division

# NEW (Python 3)
5 / 2 = 2.5  # Float division
5 // 2 = 2  # Integer division
```

## Framework Changes

### Flask → FastAPI
**Route Definition**
```python
# OLD (Flask)
@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    return {'id': item_id}

# NEW (FastAPI)
@app.get('/api/items/{item_id}')
async def get_item(item_id: int):
    return {'id': item_id}
```

**Request Handling**
```python
# OLD (Flask)
from flask import request
data = request.json

# NEW (FastAPI)
from pydantic import BaseModel
class Item(BaseModel):
    name: str

async def create_item(item: Item):
    return item
```

## Migration Checklist
- [ ] Update all print statements
- [ ] Update string handling for Unicode
- [ ] Update division operators
- [ ] Update route definitions
- [ ] Update request/response handling
- [ ] Update dependency imports
- [ ] Test all changes
"""

        return {
            "document_type": "breaking_changes",
            "title": "Breaking Changes & Solutions",
            "content": doc,
            "categories": [
                "Language Changes",
                "Framework Changes",
                "Database Changes",
                "API Changes",
            ],
        }

    def _tool_generate_api_docs(self) -> Dict[str, Any]:
        """
        Generate API documentation.

        Returns:
            API documentation
        """
        docs = """# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All requests require authentication header:
```
Authorization: Bearer {token}
```

## Endpoints

### Get All Items
```
GET /items
```

**Response (200 OK)**
```json
[
  {
    "id": 1,
    "name": "Item 1",
    "description": "Description",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Item by ID
```
GET /items/{id}
```

**Parameters**
- `id` (path, required): Item ID

**Response (200 OK)**
```json
{
  "id": 1,
  "name": "Item 1",
  "description": "Description",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Create Item
```
POST /items
```

**Request Body**
```json
{
  "name": "New Item",
  "description": "Item description",
  "price": 99.99
}
```

**Response (201 Created)**
```json
{
  "id": 2,
  "name": "New Item",
  "description": "Item description",
  "price": 99.99,
  "created_at": "2024-01-02T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

### Update Item
```
PUT /items/{id}
```

**Parameters**
- `id` (path, required): Item ID

**Request Body** (all fields optional)
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "price": 149.99
}
```

**Response (200 OK)**
```json
{
  "id": 1,
  "name": "Updated Name",
  "description": "Updated description",
  "price": 149.99,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

### Delete Item
```
DELETE /items/{id}
```

**Parameters**
- `id` (path, required): Item ID

**Response (204 No Content)**
"""

        return {
            "document_type": "api_docs",
            "title": "API Reference Documentation",
            "content": docs,
            "endpoints": [
                "GET /items",
                "GET /items/{id}",
                "POST /items",
                "PUT /items/{id}",
                "DELETE /items/{id}",
            ],
        }

    def _tool_create_troubleshooting_guide(self) -> Dict[str, Any]:
        """
        Create troubleshooting guide.

        Returns:
            Troubleshooting documentation
        """
        guide = """# Troubleshooting Guide

## Common Issues & Solutions

### Issue: Import Errors
**Symptoms:** ModuleNotFoundError or ImportError

**Solutions:**
1. Check Python path: `echo $PYTHONPATH`
2. Verify package is installed: `pip list | grep package-name`
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Check for circular imports
5. Verify __init__.py files exist

### Issue: Database Connection Errors
**Symptoms:** Connection refused, timeout

**Solutions:**
1. Verify database is running: `docker ps` or `systemctl status postgresql`
2. Check connection string in .env file
3. Verify credentials are correct
4. Check firewall rules
5. Run migrations: `alembic upgrade head`

### Issue: Port Already in Use
**Symptoms:** "Address already in use"

**Solutions:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python -m uvicorn main:app --port 8001
```

### Issue: CORS Errors
**Symptoms:** Cross-Origin Request Blocked

**Solutions:**
1. Check CORS middleware is configured
2. Verify allowed origins in settings
3. Check request headers
4. Test with CORS browser extension

### Issue: Performance Degradation
**Symptoms:** Slow response times

**Solutions:**
1. Enable query logging
2. Check database indexes
3. Profile code with cProfile
4. Check for N+1 queries
5. Enable caching

## FAQ

**Q: Can I rollback the migration?**
A: Yes, keep the old system running in parallel during the canary phase.

**Q: What if something breaks in production?**
A: Follow the rollback plan - have previous version ready and traffic can be switched back.

**Q: How do I handle database migrations?**
A: Use database migration tools (Alembic for Python, Flyway for Java) to version control schema changes.

**Q: Should I migrate all code at once?**
A: No, use phased approach - migrate features incrementally and test thoroughly.

## Getting Help
- Check the main documentation
- Review code examples
- Check framework documentation
- Ask in team chat/issues
"""

        return {
            "document_type": "troubleshooting",
            "title": "Troubleshooting Guide & FAQ",
            "content": guide,
            "common_issues": [
                "Import Errors",
                "Database Connection Errors",
                "Port Already in Use",
                "CORS Errors",
                "Performance Degradation",
            ],
        }

    def _generate_documentation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all documentation.

        Args:
            input_data: Generation context

        Returns:
            Complete documentation package
        """
        return {
            "migration_guide": self._tool_generate_migration_guide(),
            "breaking_changes": self._tool_document_breaking_changes(),
            "api_docs": self._tool_generate_api_docs(),
            "troubleshooting": self._tool_create_troubleshooting_guide(),
            "generated_files": [
                "MIGRATION_GUIDE.md",
                "BREAKING_CHANGES.md",
                "API_DOCUMENTATION.md",
                "TROUBLESHOOTING.md",
                "FAQ.md",
                "BEST_PRACTICES.md",
            ],
        }
