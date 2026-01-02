# Product Requirements Document (PRD)

## Overview

Develop a self‑hosted application generator that uses a Streamlit web interface and a LangChain-based orchestrator to convert a GitHub repository (or a standalone product requirements document) into a complete, modernised code scaffold. The system runs entirely offline on a local large language model (LLM) such as Ollama and outputs backend and frontend scaffolds, comprehensive documentation, and a downloadable ZIP archive.

## Goals & Objectives

* Enable developers to instantly transform legacy codebases or high-level specifications into clean, modern application scaffolds without relying on cloud services.
* Provide a simple Streamlit-based UI where users can supply a repository URL or a PRD and select a target technology stack.
* Orchestrate a sequence of local LLM agents via LangChain to analyze the input, plan the work, generate code, and assemble documentation.
* Deliver ready-to-run backend and frontend code, along with a README and other docs, packaged together as a ZIP file.

## Inputs

- **Repository URL**: Optional GitHub link to analyze and modernize. If omitted, the system relies solely on the provided PRD.
- **Standalone PRD**: A markdown document placed in `inputs/input_prd.md` that describes the desired functionality and constraints when no repository is supplied.
- **Target Stack**: A selection of the desired technology stack (e.g., React + FastAPI, Next.js + Node).
- **Additional Parameters**: Optional configuration details such as authentication type, database choice, API style, or deployment target.

## Outputs

- **Backend Scaffold**: Generated backend source code for the selected stack.
- **Frontend Scaffold**: Generated frontend source code, including API integrations and basic UI components.
- **Documentation**: A generated `README.md` and supplementary documentation describing the application architecture, setup, and usage.
- **Repo Map / Risk Register**: Analysis artifacts summarizing the input repository (if provided) and highlighting potential modernization risks.
- **ZIP Bundle**: A compressed archive containing all generated code, documentation, and artifacts for download.

## Agent Workflow

1. **PRD Pathfinder** – Reads the PRD (or analyzes the repository) and produces `repo_map.md` and `risk_register.md`.
2. **PRD Architect** – Converts the analysis into a structured `PRD.md` describing scope, constraints, and system goals.
3. **Task Planner** – Breaks down the PRD into an ordered list of tasks with dependencies, outputting `tasks.json`.
4. **Backend Builder** – Generates the backend scaffolding according to the tasks and target stack.
5. **Frontend Builder** – Generates the frontend scaffolding and integrates API calls as defined in the tasks.
6. **Docs Packager** – Creates user-facing documentation such as `README.md` and additional docs.
7. **Integrator QA Gate** – Validates that the generated backend and frontend align correctly and that the app can run; produces a QA report.

## Success Criteria

- The generated application scaffolding matches the selected technology stack and can run locally without modification.
- The documentation clearly explains how to set up and run the generated application.
- All artifacts—including code, docs, and analysis—are packaged into a downloadable ZIP file.
