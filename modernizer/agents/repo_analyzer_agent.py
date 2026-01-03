"""Repository analysis agent.

This agent inspects the cloned repository structure, identifies key artifacts,
optionally samples a few files, and asks the local LLM to synthesize a
high-level summary suitable for downstream modernization tasks.
"""

from pathlib import Path
from typing import Any, Dict

from langchain_core.language_models.chat_models import BaseChatModel

from modernizer.utils.files import build_file_tree, find_key_artifacts


class RepoAnalyzerAgent:
    """Analyze the repository and populate project_context['analysis']."""

    def __init__(self, llm: BaseChatModel, prompts_dir: Path) -> None:
        self.llm = llm
        self.prompts_dir = prompts_dir

    def run(self, project_context: Dict[str, Any]) -> None:
        repo_path = Path(project_context["repo_path"]).resolve()
        backend_stack = project_context["backend_stack"]
        frontend_stack = project_context["frontend_stack"]
        database = project_context["database"]

        file_tree = build_file_tree(repo_path)
        artifacts = find_key_artifacts(repo_path)

        template_path = self.prompts_dir / "repo_analysis_prompt.md"
        template = template_path.read_text(encoding="utf-8")

        prompt = template.replace("{{ owner }}", project_context["owner"]).replace(
            "{{ name }}", project_context["name"]
        )
        prompt = prompt.replace("{{ backend_stack }}", backend_stack)
        prompt = prompt.replace("{{ frontend_stack }}", frontend_stack)
        prompt = prompt.replace("{{ database }}", database)
        prompt = prompt.replace("{{ file_tree }}", "\n".join(file_tree))
        prompt = prompt.replace(
            "{{ readme_paths }}",
            "\n".join(str(p.relative_to(repo_path)) for p in artifacts["readmes"]),
        )
        prompt = prompt.replace(
            "{{ build_files }}",
            "\n".join(str(p.relative_to(repo_path)) for p in artifacts["build_files"]),
        )
        prompt = prompt.replace(
            "{{ configs }}",
            "\n".join(str(p.relative_to(repo_path)) for p in artifacts["configs"]),
        )
        prompt = prompt.replace(
            "{{ entrypoints }}",
            "\n".join(str(p.relative_to(repo_path)) for p in artifacts["entrypoints"]),
        )

        response = self.llm.invoke(prompt)
        project_context["analysis"] = {
            "summary_markdown": str(getattr(response, "content", response)),
            "file_tree": file_tree,
            "artifacts": {
                "readmes": [str(p) for p in artifacts["readmes"]],
                "build_files": [str(p) for p in artifacts["build_files"]],
                "configs": [str(p) for p in artifacts["configs"]],
                "entrypoints": [str(p) for p in artifacts["entrypoints"]],
            },
        }
