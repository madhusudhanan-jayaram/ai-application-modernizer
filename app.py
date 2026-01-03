"""Streamlit UI for the LLM-Powered GitHub Modernizer MVP.

Run with:
    streamlit run app.py

The app expects a local Ollama server with the model `qwen2.5-coder:7b`
available and pulled, listening on http://localhost:11434.
"""

from pathlib import Path

import streamlit as st

from modernizer.orchestrator import ModernizationOrchestrator


PROJECT_ROOT = Path(__file__).parent.resolve()


TEXT_FILE_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
}


def _safe_read_text(path: Path) -> str:
    """Read text defensively, tolerating non-UTF8 content.

    Falls back to latin-1 with errors ignored if UTF-8 decoding fails.
    """

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="ignore")


def _list_text_code_files(base_dir: Path) -> list[Path]:
    """Return only human-readable code/config files from base_dir.

    Skips hidden files like .DS_Store and anything without a known text
    extension.
    """

    return sorted(
        p
        for p in base_dir.rglob("*")
        if p.is_file()
        and not p.name.startswith(".")
        and p.suffix.lower() in TEXT_FILE_EXTENSIONS
    )


def main() -> None:
    st.set_page_config(page_title="LLM-Powered GitHub Modernizer", layout="wide")

    st.title("LLM-Powered GitHub Modernizer")
    st.markdown(
        "Modernize legacy GitHub repositories using local LLM agents powered by "
        "LangChain + Ollama (qwen2.5-coder:7b)."
    )

    st.sidebar.header("Configuration")

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/owner/repo or owner/repo",
    )

    backend_stack = st.selectbox(
        "Backend Target Stack",
        ["FastAPI", "Spring Boot", "Node.js"],
        index=0,
    )

    frontend_stack = st.selectbox(
        "Frontend Target Stack (logical output only)",
        ["React", "Angular", "Next.js"],
        index=0,
    )

    database = st.selectbox(
        "Database",
        ["PostgreSQL", "MySQL", "MongoDB"],
        index=0,
    )

    st.divider()

    if "logs" not in st.session_state:
        st.session_state["logs"] = []
    if "last_run_output" not in st.session_state:
        st.session_state["last_run_output"] = None

    progress_tab, docs_tab, code_tab = st.tabs([
        "Progress & Download",
        "Business Docs",
        "Modernized Code",
    ])

    with progress_tab:
        logs_container = st.container()
        result_container = st.container()

    def log(message: str) -> None:
        st.session_state["logs"].append(message)
        with logs_container:
            st.subheader("Progress")
            for line in st.session_state["logs"]:
                st.write(line)

    orchestrator = ModernizationOrchestrator(PROJECT_ROOT)

    with progress_tab:
        if st.button("🚀 Modernize Application"):
            st.session_state["logs"] = []
            st.session_state["last_run_output"] = None
            if not repo_url.strip():
                st.error("Please enter a GitHub repository URL.")
            else:
                try:
                    with st.spinner("Running modernization workflow..."):
                        project_context = orchestrator.run(
                            repo_url=repo_url.strip(),
                            backend_stack=backend_stack,
                            frontend_stack=frontend_stack,
                            database=database,
                            progress_callback=log,
                        )

                    zip_path = Path(project_context["zip_path"]).resolve()
                    zip_bytes = zip_path.read_bytes()

                    st.session_state["last_run_output"] = {
                        "zip_path": str(zip_path),
                        "docs_dir": str(PROJECT_ROOT / "output" / "docs"),
                        "artifacts_dir": str(PROJECT_ROOT / "output" / "artifacts"),
                    }

                    with result_container:
                        st.success("Modernization completed successfully!")
                        st.download_button(
                            label="⬇️ Download Modernization ZIP",
                            data=zip_bytes,
                            file_name="modernization_output.zip",
                            mime="application/zip",
                        )

                except Exception as exc:  # pragma: no cover - UI-focused
                    st.error(f"Error during modernization: {exc}")

    with docs_tab:
        st.subheader("Business-Friendly Documentation")
        info = st.session_state.get("last_run_output")
        if not info:
            st.info("Run a modernization first to view generated documents.")
        else:
            docs_dir = Path(info["docs_dir"])
            exec_path = docs_dir / "EXECUTIVE_SUMMARY.md"
            bizreq_path = docs_dir / "BUSINESS_REQUIREMENTS.md"
            func_path = docs_dir / "FUNCTIONAL_OVERVIEW.md"
            mig_path = docs_dir / "MIGRATION_PLAN.md"

            def render_doc(path: Path, title: str) -> None:
                if path.exists():
                    st.markdown(f"### {title}")
                    st.markdown(_safe_read_text(path))
                else:
                    st.markdown(f"### {title}")
                    st.warning("Document not found in the latest run.")

            render_doc(exec_path, "Executive Summary")
            render_doc(bizreq_path, "Business Requirements")
            render_doc(func_path, "Functional Overview")
            render_doc(mig_path, "Migration Plan")

    with code_tab:
        st.subheader("Modernized Backend Starter Code")
        info = st.session_state.get("last_run_output")
        if not info:
            st.info("Run a modernization first to view generated code.")
        else:
            artifacts_dir = Path(info["artifacts_dir"])
            if not artifacts_dir.exists():
                st.warning("No code artifacts were generated in the latest run.")
            else:
                # Collect a simple list of text/code files under artifacts_dir
                files = [p.relative_to(artifacts_dir) for p in _list_text_code_files(artifacts_dir)]
                if not files:
                    st.warning("No code files found under output/artifacts.")
                else:
                    selected = st.selectbox(
                        "Select a generated file to view",
                        options=[str(f) for f in files],
                    )
                    file_path = artifacts_dir / selected
                    st.markdown(f"#### {selected}")
                    st.code(
                        _safe_read_text(file_path),
                        language="python",
                    )


if __name__ == "__main__":
    main()
