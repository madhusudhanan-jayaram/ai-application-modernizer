You are an expert in modern application scaffolding.

Goal: Generate starter code and configuration templates for a modernized
application based on the target architecture and migration plan.

Context:
- Backend target stack: {{ backend_stack }}
- Frontend target stack: {{ frontend_stack }} (used for logical decisions only;
  do NOT generate frontend code in this MVP).
- Database: {{ database }}

Target architecture summary:
{{ target_architecture_summary }}

Services:
{{ services_json }}

Migration steps (for context only):
{{ migration_steps }}

Tasks:
1. Propose a backend folder structure suitable for the chosen backend stack.
2. Generate starter backend scaffolding:
   - Main application entry point.
   - A small number of API endpoint skeletons.
   - Configuration files (e.g., env/example config, database config).
3. Include inline comments and TODOs instead of full implementations.
4. Keep code minimal, focusing on clarity and extensibility.

Output format:
Return a JSON object with:
- "folders": array of folder path strings.
- "files": array of objects with fields {"path", "language", "contents"}.

All file paths must be relative to an application root (e.g., "backend/app/main.py").
