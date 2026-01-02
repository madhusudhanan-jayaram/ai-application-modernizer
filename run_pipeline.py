import subprocess
import sys


def run_agent(command: list[str]) -> None:
    """Run a single Claude agent command and exit on failure."""
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Agent failed with return code {e.returncode}")
        sys.exit(e.returncode)


def generate_app():
    """Execute the agent pipeline: run prd-pathfinder, mvp-prd-architect, task-breakdown-lead, backend-builder, frontend-builder, docs-packager, integrator-qa-gate."""
    run_agent([
        "claude", "--agent", "prd-pathfinder",
        "Generate repo_map.md and risk_register.md from the PRD in inputs/"
    ])
    run_agent([
        "claude", "--agent", "mvp-prd-architect",
        "Use artifacts/repo_map.md to generate PRD.md"
    ])
    run_agent([
        "claude", "--agent", "task-breakdown-lead",
        "Generate tasks.json from PRD.md"
    ])
    run_agent([
        "claude", "--agent", "backend-builder",
        "Create backend based on tasks.json and PRD.md"
    ])
    run_agent([
        "claude", "--agent", "frontend-builder",
        "Create frontend based on tasks.json and PRD.md"
    ])
    run_agent([
        "claude", "--agent", "docs-packager",
        "Produce README.md and docs from analysis and build artifacts"
    ])
    run_agent([
        "claude", "--agent", "integrator-qa-gate",
        "Validate that the generated code runs and components agree"
    ])


if __name__ == "__main__":
    generate_app()
