"""Code generator agent.

This agent consumes the modernization plan and asks the LLM to produce a
JSON description of folders and files, which are then materialized under
/output/artifacts.
"""

import json
from pathlib import Path
from typing import Any, Dict

from langchain_core.language_models.chat_models import BaseChatModel

from modernizer.utils.files import write_artifact_file


def _extract_json_block(text: str) -> str:
    """Extract a JSON object from an LLM response.

    Models often wrap JSON in Markdown code fences (```json ... ```).
    This helper strips those fences and, as a fallback, slices the
    substring between the first '{' and the last '}' if present.
    """

    stripped = text.strip()

    # Handle ```json ... ``` or ``` ... ``` style fences
    if stripped.startswith("```"):
        first_newline = stripped.find("\n")
        if first_newline != -1:
            inner = stripped[first_newline + 1 :]
        else:
            inner = stripped

        if inner.endswith("```"):
            inner = inner[: -3]

        return inner.strip()

    # Fallback: best-effort slice between outermost braces
    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return stripped[first_brace : last_brace + 1]

    return stripped


class CodeGeneratorAgent:
    """Generate starter backend scaffolding as code artifacts."""

    def __init__(self, llm: BaseChatModel, prompts_dir: Path, artifacts_dir: Path) -> None:
        self.llm = llm
        self.prompts_dir = prompts_dir
        self.artifacts_dir = artifacts_dir

    def run(self, project_context: Dict[str, Any]) -> None:
        plan = project_context["plan"]
        backend_stack = project_context["backend_stack"]
        frontend_stack = project_context["frontend_stack"]
        database = project_context["database"]

        template_path = self.prompts_dir / "code_gen_prompt.md"
        template = template_path.read_text(encoding="utf-8")

        prompt = template.replace("{{ backend_stack }}", backend_stack)
        prompt = prompt.replace("{{ frontend_stack }}", frontend_stack)
        prompt = prompt.replace("{{ database }}", database)
        prompt = prompt.replace(
            "{{ target_architecture_summary }}", plan.get("target_architecture_summary", "")
        )
        prompt = prompt.replace(
            "{{ services_json }}", json.dumps(plan.get("services", []), indent=2)
        )
        prompt = prompt.replace(
            "{{ migration_steps }}", json.dumps(plan.get("migration_steps", []), indent=2)
        )

        response = self.llm.invoke(prompt)
        raw_text = str(getattr(response, "content", response))
        json_text = _extract_json_block(raw_text)

        try:
            spec = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback: create a minimal spec.
            spec = {"folders": ["backend"], "files": []}

        folders = spec.get("folders", [])
        for folder in folders:
            (self.artifacts_dir / folder).mkdir(parents=True, exist_ok=True)

        files = spec.get("files", [])
        for file_desc in files:
            path = file_desc.get("path")
            contents = file_desc.get("contents", "")
            if not path:
                continue
            write_artifact_file(self.artifacts_dir, path, contents)

        project_context["generated_code"] = {
            "folders": folders,
            "files": [f.get("path") for f in files if f.get("path")],
        }
