"""Modernization orchestrator.

Coordinates the end-to-end flow:
1. Validate and clone the GitHub repository.
2. Analyze the repository.
3. Generate documentation.
4. Plan the modernization.
5. Generate starter code artifacts.
6. Package everything into a ZIP under /output.
"""

from pathlib import Path
from typing import Any, Callable, Dict

from modernizer.agents.code_generator_agent import CodeGeneratorAgent
from modernizer.agents.document_generator_agent import DocumentGeneratorAgent
from modernizer.agents.modernization_planner_agent import ModernizationPlannerAgent
from modernizer.agents.repo_analyzer_agent import RepoAnalyzerAgent
from modernizer.utils.files import create_output_zip, ensure_output_dirs
from modernizer.utils.github import clone_public_repo, validate_github_url
from modernizer.utils.ollama import get_llm


ProgressCallback = Callable[[str], None]


class ModernizationOrchestrator:
    """High-level orchestrator for the GitHub modernizer MVP."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.output_root = project_root / "output"
        self.prompts_dir = project_root / "modernizer" / "prompts"

    def run(
        self,
        repo_url: str,
        backend_stack: str,
        frontend_stack: str,
        database: str,
        progress_callback: ProgressCallback,
    ) -> Dict[str, Any]:
        """Execute the full modernization workflow.

        Returns a dictionary containing the project_context and the path to
        the generated ZIP file.
        """

        progress_callback("Validating GitHub URL...")
        is_valid, error = validate_github_url(repo_url)
        if not is_valid:
            raise ValueError(error or "Invalid GitHub URL.")

        progress_callback("Cloning repository (shallow clone)...")
        clone_info = clone_public_repo(repo_url, depth=1)

        output_dirs = ensure_output_dirs(self.output_root)
        docs_dir = output_dirs["docs"]
        artifacts_dir = output_dirs["artifacts"]

        llm = get_llm()

        project_context: Dict[str, Any] = {
            "repo_url": repo_url,
            "repo_path": clone_info["repo_path"],
            "owner": clone_info["owner"],
            "name": clone_info["name"],
            "backend_stack": backend_stack,
            "frontend_stack": frontend_stack,
            "database": database,
        }

        progress_callback("Analyzing repository structure...")
        RepoAnalyzerAgent(llm, self.prompts_dir).run(project_context)

        progress_callback("Generating modernization documentation...")
        DocumentGeneratorAgent(llm, self.prompts_dir, docs_dir).run(project_context)

        progress_callback("Designing target architecture and migration plan...")
        ModernizationPlannerAgent(llm, self.prompts_dir).run(project_context)

        progress_callback("Generating starter backend scaffolding...")
        CodeGeneratorAgent(llm, self.prompts_dir, artifacts_dir).run(project_context)

        progress_callback("Packaging outputs into ZIP archive...")
        zip_path = self.output_root / "modernization_output.zip"
        create_output_zip(self.output_root, zip_path)

        progress_callback("Modernization workflow complete.")

        project_context["zip_path"] = str(zip_path)
        return project_context
