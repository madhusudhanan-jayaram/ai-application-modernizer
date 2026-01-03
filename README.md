# LLM-Powered GitHub Modernizer

This MVP is a Streamlit application that clones a GitHub repository and uses
local LLM agents (via LangChain + Ollama) to analyze, document, and propose a
modernized backend starter scaffold.

- **UI**: Streamlit
- **LLM**: Local Ollama model `qwen2.5-coder:7b` (no cloud LLMs)
- **Orchestration**: LangChain agents with a shared LLM instance

## Features

- Validate and shallow-clone a public GitHub repository.
- Analyze the repository structure and key artifacts.
- Generate modernization-focused documentation:
  - EXECUTIVE_SUMMARY.md
  - FUNCTIONAL_OVERVIEW.md
  - NON_FUNCTIONAL_REQUIREMENTS.md
  - CURRENT_ARCHITECTURE.md
  - TARGET_ARCHITECTURE.md
  - API_CONTRACTS.md
  - RISKS_AND_ASSUMPTIONS.md
  - MIGRATION_PLAN.md
- Propose a target architecture and migration plan.
- Generate starter backend scaffolding as code templates.
- Package all outputs under `output/` into a downloadable ZIP.

## Local LLM Requirements

- Install and run [Ollama](https://ollama.com/).
- Pull the model:

  ```bash
  ollama pull qwen2.5-coder:7b
  ```

- Ensure the Ollama server is running (default `http://localhost:11434`).

The app uses a single shared LangChain `ChatOllama` instance configured with:

- Base URL: `http://localhost:11434`
- Model: `qwen2.5-coder:7b`
- Low temperature (≈0.1)
- Conservative max tokens to avoid context overflow

## Installation

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Running the App

From the project root, with Ollama running locally:

```bash
streamlit run app.py
```

Then open the provided URL in your browser.

## Usage

1. Enter a **GitHub Repository URL** (public repo preferred for the MVP).
2. Choose:
   - Backend Target Stack: `FastAPI`, `Spring Boot`, or `Node.js`.
   - Frontend Target Stack (logical output only): `React`, `Angular`, or `Next.js`.
   - Database: `PostgreSQL`, `MySQL`, or `MongoDB`.
3. Click **"🚀 Modernize Application"**.
4. Watch the step-by-step progress log.
5. When complete, download the generated ZIP containing:
   - Documentation under `output/docs/`.
   - Starter backend scaffolding under `output/artifacts/`.

## Project Structure

- `app.py` – Streamlit UI entrypoint.
- `modernizer/orchestrator.py` – Sequential orchestration of agents.
- `modernizer/agents/` – Four agents:
  - `repo_analyzer_agent.py`
  - `document_generator_agent.py`
  - `modernization_planner_agent.py`
  - `code_generator_agent.py`
- `modernizer/utils/` – Utilities:
  - `github.py` – GitHub URL validation and shallow clone helpers.
  - `files.py` – File tree inspection and output/ZIP helpers.
  - `ollama.py` – Shared Ollama + LangChain LLM configuration.
- `modernizer/prompts/` – Prompt templates for each agent.
- `output/` – Generated docs, code artifacts, and ZIP packages.

## Notes

- The MVP is designed to work fully offline from an LLM perspective; only
  Git operations require network access to GitHub.
- Generated code is intentionally skeletal and heavily commented, intended as
  a starting point for manual refinement rather than a full migration.
