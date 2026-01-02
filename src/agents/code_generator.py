"""
Code Generator Agent - Generates modernized code for target tech stack.
Transforms and generates code samples, creates migration examples.
Fourth agent in the modernization pipeline.
"""

from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent, AgentError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CodeGeneratorAgent(BaseAgent):
    """
    Agent for generating modernized code.

    Responsibilities:
    - Generate code samples for target tech stack
    - Transform existing code patterns to modern equivalents
    - Create working examples for key features
    - Generate migration helpers and adapters
    - Create template boilerplate code
    - Generate updated configurations

    Output:
    - Generated Python/Java/JS code files
    - Before/after code samples
    - Migration example code
    - Configuration templates
    """

    # Code templates for different stacks
    CODE_TEMPLATES = {
        "python_fastapi": {
            "main": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(title="Modernized API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/items/{item_id}")
async def get_item(item_id: int):
    logger.info(f"Fetching item {item_id}")
    return {"item_id": item_id, "data": "example"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""",
            "model": """from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
""",
        },
        "javascript_react": {
            "component": """import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ItemList = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/items');
        setItems(response.data);
      } catch (err) {
        setError(err.message);
        console.error('Failed to fetch items:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Items</h1>
      <ul>
        {items.map((item) => (
          <li key={item.id}>{item.name} - ${item.price}</li>
        ))}
      </ul>
    </div>
  );
};

export default ItemList;
""",
        },
        "java_spring": {
            "controller": """package com.example.controller;

import com.example.model.Item;
import com.example.service.ItemService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/items")
@RequiredArgsConstructor
public class ItemController {

    private final ItemService itemService;

    @GetMapping
    public ResponseEntity<List<Item>> getAllItems() {
        return ResponseEntity.ok(itemService.getAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Item> getItem(@PathVariable Long id) {
        return itemService.getById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Item> createItem(@RequestBody Item item) {
        Item created = itemService.save(item);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Item> updateItem(@PathVariable Long id, @RequestBody Item item) {
        return itemService.update(id, item)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteItem(@PathVariable Long id) {
        itemService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
""",
        },
    }

    def __init__(self):
        """Initialize Code Generator Agent."""
        super().__init__(
            agent_name="CodeGenerator",
            description="Generates modernized code for target technology stack",
            system_prompt=self._get_generator_prompt(),
            max_iterations=10,
            temperature=0.3,  # Higher temp for creative code generation
        )

        self._register_tools()

    def _register_tools(self) -> None:
        """Register tools for code generation."""
        self.register_tool(
            name="generate_template",
            description="Generate boilerplate code template for framework",
            func=self._tool_generate_template,
        )

        self.register_tool(
            name="transform_code",
            description="Transform code pattern from source to target stack",
            func=self._tool_transform_code,
        )

        self.register_tool(
            name="generate_model",
            description="Generate data model definitions for target framework",
            func=self._tool_generate_model,
        )

        self.register_tool(
            name="generate_example",
            description="Generate complete working example in target stack",
            func=self._tool_generate_example,
        )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input for code generation.

        Args:
            input_data: Must contain 'target_tech_stack'

        Returns:
            True if valid

        Raises:
            AgentError: If required fields missing
        """
        super().validate_input(input_data)

        if "target_tech_stack" not in input_data:
            raise AgentError("CodeGenerator requires 'target_tech_stack'")

        return True

    def prepare_context(self, input_data: Dict[str, Any]) -> str:
        """
        Prepare context for code generation.

        Args:
            input_data: Generation context

        Returns:
            Context string
        """
        base_context = super().prepare_context(input_data)

        target_stack = input_data.get("target_tech_stack", "Unknown")

        additional = f"""
Target Technology Stack: {target_stack}

Code Generation Tasks:
1. Generate boilerplate/template code for frameworks
2. Transform code patterns to modern equivalents
3. Create data model definitions
4. Generate working code examples
5. Create configuration files
6. Provide best practices code

Output Format:
- Well-structured, production-ready code
- Include error handling and logging
- Follow modern patterns and best practices
- Include comments and docstrings
- Provide configuration examples
"""

        return f"{base_context}\n{additional}"

    def _process_result(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process code generation result.

        Args:
            response: LLM response
            input_data: Original input

        Returns:
            Structured generation result
        """
        result = {
            "agent": self.agent_name,
            "target_stack": input_data.get("target_tech_stack"),
            "llm_analysis": response,
            "generated_files": self._get_template_files(input_data.get("target_tech_stack", "")),
            "success": True,
        }

        return result

    def _get_generator_prompt(self) -> str:
        """Get system prompt for code generator."""
        return """You are CodeGenerator, an expert in generating modern, production-ready code.

Your expertise:
- Writing clean, maintainable code in multiple languages
- Following industry best practices and patterns
- Generating type-safe, well-documented code
- Creating scalable architecture examples
- Producing migration helper code
- Generating configuration files

When generating code, you should:
1. Follow framework best practices and conventions
2. Include comprehensive error handling
3. Add logging and monitoring capabilities
4. Provide type hints and documentation
5. Create reusable, modular components
6. Include security best practices
7. Demonstrate async/await patterns where applicable

Code Generation Areas:
- Main application files with proper setup
- API endpoint definitions and handlers
- Data model and schema definitions
- Database access layers (DAOs/repositories)
- Service/business logic layers
- Error handling and middleware
- Configuration and environment setup
- Testing examples
- Docker configuration
- CI/CD pipeline examples

Always generate production-quality code with comments, error handling, and best practices."""

    # ===== Tool Implementations =====

    def _tool_generate_template(self, framework: str = None) -> Dict[str, Any]:
        """
        Generate template code for framework.

        Args:
            framework: Target framework name

        Returns:
            Template code
        """
        if not framework and self.current_input:
            framework = self.current_input.get("target_tech_stack", "").lower()

        if not framework:
            return {"error": "No framework specified"}

        # Get appropriate template
        if "fastapi" in framework.lower() or "python" in framework.lower():
            return {
                "framework": "FastAPI",
                "main.py": self.CODE_TEMPLATES.get("python_fastapi", {}).get("main", ""),
                "model.py": self.CODE_TEMPLATES.get("python_fastapi", {}).get("model", ""),
            }

        elif "react" in framework.lower() or "javascript" in framework.lower():
            return {
                "framework": "React",
                "component.jsx": self.CODE_TEMPLATES.get("javascript_react", {}).get("component", ""),
            }

        elif "spring" in framework.lower() or "java" in framework.lower():
            return {
                "framework": "Spring Boot",
                "ItemController.java": self.CODE_TEMPLATES.get("java_spring", {}).get("controller", ""),
            }

        else:
            return {"error": f"No template available for {framework}"}

    def _tool_transform_code(
        self, source_pattern: str = None, source_lang: str = None, target_lang: str = None
    ) -> Dict[str, Any]:
        """
        Transform code pattern between languages.

        Args:
            source_pattern: Code pattern to transform
            source_lang: Source language
            target_lang: Target language

        Returns:
            Transformed code
        """
        if not source_pattern:
            return {"error": "No source pattern provided"}

        # Example transformations
        transformations = {
            ("python_flask", "python_fastapi"): {
                "from flask import Flask, request": "from fastapi import FastAPI, Request",
                "@app.route('/api/items')": '@app.get("/api/items")',
                "request.json": "request payload (automatic in FastAPI)",
            },
            ("javascript_jquery", "javascript_react"): {
                "$.ajax({url: '/api/items'})": "axios.get('/api/items')",
                "$('#items').html(data)": "setItems(data)",
                "$(document).ready(function(){})": "useEffect(() => {}, [])",
            },
        }

        key = (source_lang, target_lang)
        if key in transformations:
            return {
                "source_pattern": source_pattern,
                "source_language": source_lang,
                "target_language": target_lang,
                "transformations": transformations[key],
                "notes": f"Transform from {source_lang} to {target_lang}",
            }

        return {
            "error": f"No transformation available from {source_lang} to {target_lang}"
        }

    def _tool_generate_model(self, model_name: str = None, target_lang: str = None) -> Dict[str, Any]:
        """
        Generate data model definition.

        Args:
            model_name: Model/entity name
            target_lang: Target language

        Returns:
            Generated model code
        """
        if not model_name:
            model_name = "Item"

        if not target_lang and self.current_input:
            target_lang = self.current_input.get("target_tech_stack", "").lower()

        python_model = f"""from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class {model_name}(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
"""

        java_model = f"""package com.example.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "{model_name.lower()}s")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class {model_name} {{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column
    private String description;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();
}}
"""

        if "python" in (target_lang or "").lower():
            return {
                "model_name": model_name,
                "language": "Python",
                "framework": "Pydantic",
                "code": python_model,
            }
        elif "java" in (target_lang or "").lower():
            return {
                "model_name": model_name,
                "language": "Java",
                "framework": "Spring Data JPA",
                "code": java_model,
            }
        else:
            return {"error": f"No model generation for {target_lang}"}

    def _tool_generate_example(self, feature: str = None) -> Dict[str, Any]:
        """
        Generate complete working example.

        Args:
            feature: Feature to demonstrate

        Returns:
            Complete example code
        """
        if not feature:
            feature = "CRUD API"

        target_stack = (
            self.current_input.get("target_tech_stack", "").lower()
            if self.current_input
            else ""
        )

        if "fastapi" in target_stack or "python" in target_stack:
            return {
                "feature": feature,
                "stack": "FastAPI + SQLAlchemy",
                "files": {
                    "main.py": self.CODE_TEMPLATES.get("python_fastapi", {}).get("main", ""),
                    "models.py": self.CODE_TEMPLATES.get("python_fastapi", {}).get("model", ""),
                    "requirements.txt": "fastapi==0.104.0\nuvicorn==0.24.0\nsqlalchemy==2.0.0\npydantic==2.5.0",
                },
            }

        elif "react" in target_stack or "javascript" in target_stack:
            return {
                "feature": feature,
                "stack": "React + Axios",
                "files": {
                    "ItemList.jsx": self.CODE_TEMPLATES.get("javascript_react", {}).get("component", ""),
                    "package.json": '{"dependencies": {"react": "^18", "axios": "^1.4"}}',
                },
            }

        elif "spring" in target_stack or "java" in target_stack:
            return {
                "feature": feature,
                "stack": "Spring Boot",
                "files": {
                    "ItemController.java": self.CODE_TEMPLATES.get("java_spring", {}).get(
                        "controller", ""
                    ),
                    "pom.xml": "<dependency><groupId>org.springframework.boot</groupId></dependency>",
                },
            }

        else:
            return {"error": f"No examples for {target_stack}"}

    def _get_template_files(self, target_stack: str) -> List[str]:
        """Get list of files to generate for target stack."""
        files = []

        target_lower = target_stack.lower()

        if "python" in target_lower or "fastapi" in target_lower:
            files = [
                "main.py",
                "models.py",
                "schemas.py",
                "database.py",
                "requirements.txt",
                "docker-compose.yml",
                ".env.example",
            ]

        elif "javascript" in target_lower or "react" in target_lower:
            files = [
                "App.jsx",
                "components/ItemList.jsx",
                "services/api.js",
                "package.json",
                ".env.example",
                "Dockerfile",
            ]

        elif "java" in target_lower or "spring" in target_lower:
            files = [
                "src/main/java/com/example/controller/ItemController.java",
                "src/main/java/com/example/service/ItemService.java",
                "src/main/java/com/example/repository/ItemRepository.java",
                "src/main/java/com/example/model/Item.java",
                "pom.xml",
                "application.yml",
                "Dockerfile",
            ]

        return files
