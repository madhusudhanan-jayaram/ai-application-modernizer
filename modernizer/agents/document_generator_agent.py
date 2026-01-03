"""Agent responsible for generating modernization documentation.

This agent consumes the repository analysis summary and asks the LLM to
produce content for the required Markdown documents under /output/docs.
"""

from pathlib import Path
from typing import Any, Dict

from langchain_core.language_models.chat_models import BaseChatModel

from modernizer.utils.files import DOC_FILENAMES, write_markdown_doc


class DocumentGeneratorAgent:
    """Generate modernization-focused documentation into /output/docs."""

    def __init__(self, llm: BaseChatModel, prompts_dir: Path, docs_dir: Path) -> None:
        self.llm = llm
        self.prompts_dir = prompts_dir
        self.docs_dir = docs_dir

    def run(self, project_context: Dict[str, Any]) -> None:
        analysis_summary = project_context["analysis"]["summary_markdown"]
        backend_stack = project_context["backend_stack"]
        frontend_stack = project_context["frontend_stack"]
        database = project_context["database"]

        template_path = self.prompts_dir / "docs_prompt.md"
        template = template_path.read_text(encoding="utf-8")

        prompt = template.replace("{{ backend_stack }}", backend_stack)
        prompt = prompt.replace("{{ frontend_stack }}", frontend_stack)
        prompt = prompt.replace("{{ database }}", database)
        prompt = prompt.replace("{{ analysis_summary }}", analysis_summary)

        response = self.llm.invoke(prompt)
        text = str(getattr(response, "content", response))

        # Split the single markdown response into individual docs by headings.
        current_name = None
        current_lines = []
        docs_content: Dict[str, str] = {}

        for line in text.splitlines():
            if line.startswith("# ") and line.strip().endswith(".md"):
                # Flush previous
                if current_name is not None:
                    docs_content[current_name] = "\n".join(current_lines).strip()
                    current_lines = []
                current_name = line[2:].strip()
            else:
                current_lines.append(line)

        if current_name is not None:
            docs_content[current_name] = "\n".join(current_lines).strip()

        for name in DOC_FILENAMES:
            content = docs_content.get(name, f"TODO: {name} not provided by LLM.")
            write_markdown_doc(self.docs_dir, name, content)

        project_context["docs"] = {"generated": DOC_FILENAMES}
