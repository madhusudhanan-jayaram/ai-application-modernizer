# Product Requirements Document (PRD)

## Overview
This project aims to build a self‑hosted application generator that uses a Streamlit front‑end and a LangChain-driven orchestration layer. The tool accepts either a GitHub repository URL or a standalone product requirements document (PRD) as input and produces a complete, modern code scaffold—comprising backend and frontend components, supporting documentation, and a downloadable ZIP archive. All language model inference is performed locally via an on‑prem LLM (e.g., Ollama), ensuring privacy and offline operation.

## Goals & Objectives
- Enable developers to instantly transform legacy codebases or high-level specifications into clean, modern application scaffolds.
- Provide a Streamlit UI for input of repository URL or PRD and desired stack.
- Use LangChain to orchestrate a sequence of LLM agents that analyse, plan, and generate the code.
- Produce backend and frontend scaffolds, documentation, and package them into a ZIP.

## Inputs
- **Repository URL**: Optional GitHub link to analyse; if omitted, operate solely from PRD.
- **Standalone PRD**: If no repository is provided, this document defines the functionality and constraints.
- **Target Stack**: Desired technology stack (e.g., React + FastAPI, Next.js + Node).
- **Additional Params**: Optional configurations (auth type, database, API style).

## Outputs
- **Backend Scaffold**: Generated backend code for the selected stack.
- **Frontend Scaffold**: Generated frontend code with API integration.
- **Documentation**: README.md and any additional docs.
- **Repo Map / Risk Register**: Analysis artifacts summarising the input.
- **ZIP Bundle**: Package containing all generated code and docs.

## Agent Workflow
1. **PRD Pathfinder** – Reads this PRD (or the provided repository) and produces `repo_map.md` and `risk_register.md`.
2. **PRD Architect** – Converts the analysis into a structured `PRD.md`.
3. **Task Planner** – Produces `tasks.json` with ordered tasks and dependencies.
4. **Backend Builder** – Generates backend scaffolding.
5. **Frontend Builder** – Generates frontend scaffolding.
6. **Docs Packager** – Produces README and docs.
7. **Integrator QA Gate** – Validates the generated application and ensures alignment.

## Success Criteria
- The generated application scaffolding matches the target stack.
- Documentation clearly explains how to run the generated app.
- All artifacts are packaged into a downloadable ZIP.
