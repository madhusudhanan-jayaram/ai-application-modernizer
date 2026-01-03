"""Modernization planner agent.

This agent reads the analysis summary and produces a structured JSON
representation of the target architecture and migration plan.
"""

import json
from pathlib import Path
from typing import Any, Dict

from langchain_core.language_models.chat_models import BaseChatModel


def _extract_json_block(text: str) -> str:
    """Extract a JSON object from an LLM response.

    Many models wrap JSON in Markdown code fences (```json ... ```).
    This helper strips those fences and, as a fallback, slices the
    substring between the first '{' and the last '}' if present.
    """

    stripped = text.strip()

    # Handle ```json ... ``` or ``` ... ``` style fences
    if stripped.startswith("```"):
        # Drop the first line (``` or ```json)
        first_newline = stripped.find("\n")
        if first_newline != -1:
            inner = stripped[first_newline + 1 :]
        else:
            inner = stripped

        # Remove trailing fence if present
        if inner.endswith("```"):
            inner = inner[: -3]

        return inner.strip()

    # Fallback: best-effort slice between outermost braces
    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return stripped[first_brace : last_brace + 1]

    return stripped


class ModernizationPlannerAgent:
    """Design a target architecture and migration plan."""

    def __init__(self, llm: BaseChatModel, prompts_dir: Path) -> None:
        self.llm = llm
        self.prompts_dir = prompts_dir

    def run(self, project_context: Dict[str, Any]) -> None:
        analysis_summary = project_context["analysis"]["summary_markdown"]
        backend_stack = project_context["backend_stack"]
        frontend_stack = project_context["frontend_stack"]
        database = project_context["database"]

        # For simplicity we do not currently feed full docs; we could extend
        # this by sampling key sections from the generated docs.
        docs_highlights = "Generated docs are available but omitted for brevity."

        template_path = self.prompts_dir / "planner_prompt.md"
        template = template_path.read_text(encoding="utf-8")

        prompt = template.replace("{{ backend_stack }}", backend_stack)
        prompt = prompt.replace("{{ frontend_stack }}", frontend_stack)
        prompt = prompt.replace("{{ database }}", database)
        prompt = prompt.replace("{{ analysis_summary }}", analysis_summary)
        prompt = prompt.replace("{{ docs_highlights }}", docs_highlights)

        response = self.llm.invoke(prompt)
        raw_text = str(getattr(response, "content", response))
        json_text = _extract_json_block(raw_text)

        try:
            plan = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback: wrap raw text in a simple plan structure.
            plan = {
                "target_architecture_summary": raw_text,
                "services": [],
                "migration_steps": [],
                "cross_cutting_concerns": [],
            }

        project_context["plan"] = plan
