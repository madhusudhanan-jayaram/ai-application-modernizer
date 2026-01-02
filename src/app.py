"""
Main Streamlit Application - AI Application Modernizer
Orchestrates the complete modernization workflow.
GitHub URL input → Analysis → Migration → Report Generation → Download
"""

import streamlit as st
from typing import Optional, Dict, Any

from src.chains.analysis_chain import analysis_chain
from src.chains.migration_chain import migration_chain
from src.chains.report_generation_chain import report_generation_chain
from src.services.report_service import report_service
from src.ui.components.report_viewer import report_viewer
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="AI Application Modernizer",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 3em;
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }
        .sub-header {
            font-size: 1.2em;
            color: #666;
            text-align: center;
            margin-bottom: 30px;
        }
        .info-box {
            background-color: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        .success-box {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        .error-box {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize session state
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = {
            "repo_url": "",
            "target_stack": "",
            "analysis_result": None,
            "migration_result": None,
            "report": None,
            "current_step": "input",
        }

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")
        st.divider()

        st.subheader("Workflow Progress")
        progress = _get_workflow_progress()
        st.progress(progress)

        workflow_steps = [
            ("📝 Input", "input"),
            ("🔍 Analysis", "analysis"),
            ("🔄 Migration", "migration"),
            ("📊 Report", "report"),
            ("⬇️ Export", "export"),
        ]

        step_index = [s[1] for s in workflow_steps].index(st.session_state.workflow_state["current_step"])
        st.markdown(f"**Step {step_index + 1} of {len(workflow_steps)}**: {workflow_steps[step_index][0]}")

        st.divider()

        # Reset button
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.workflow_state = {
                "repo_url": "",
                "target_stack": "",
                "analysis_result": None,
                "migration_result": None,
                "report": None,
                "current_step": "input",
            }
            st.rerun()

    # Main header
    st.markdown(
        '<div class="main-header">🚀 AI Application Modernizer</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Transform your legacy applications into modern, scalable systems</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # Workflow tabs
    tabs = st.tabs(["Input", "Analysis", "Migration", "Report", "Export"])

    # ===== Tab 1: Input =====
    with tabs[0]:
        st.header("📝 Step 1: Repository Input & Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("GitHub Repository")

            repo_url = st.text_input(
                "GitHub Repository URL",
                value=st.session_state.workflow_state.get("repo_url", ""),
                placeholder="https://github.com/owner/repo or owner/repo",
                help="Enter the GitHub repository URL to analyze",
            )

            if repo_url:
                st.session_state.workflow_state["repo_url"] = repo_url

                # Validate repo
                if st.button("✓ Validate Repository"):
                    with st.spinner("Validating repository..."):
                        from src.services.github_service import github_service

                        is_valid, error = github_service.validate_repository(repo_url)

                        if is_valid:
                            st.success("✓ Repository found and accessible!")
                        else:
                            st.error(f"✗ Repository validation failed: {error}")

        with col2:
            st.subheader("Target Technology Stack")

            target_options = [
                "Python 3 + FastAPI",
                "Python 3 + Flask",
                "Python 3 + Django",
                "Java + Spring Boot",
                "Node.js + Express",
                "TypeScript + NestJS",
                "Go + Gin",
                "Rust + Actix",
                "Other (specify below)",
            ]

            target_stack = st.selectbox(
                "Select Target Stack",
                target_options,
                index=0,
            )

            if target_stack == "Other (specify below)":
                target_stack = st.text_input("Specify custom target stack")

            st.session_state.workflow_state["target_stack"] = target_stack

        st.divider()

        # Info boxes
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                <div class="info-box">
                <b>📖 About This Tool</b><br>
                This modernization tool analyzes your legacy applications and generates:
                <ul>
                <li>Repository structure analysis</li>
                <li>Technology stack detection</li>
                <li>Migration strategy with phases</li>
                <li>Generated code samples</li>
                <li>Comprehensive guides</li>
                </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                """
                <div class="info-box">
                <b>⚡ Supported Languages</b><br>
                <ul>
                <li>Python 2.x, 3.x</li>
                <li>Java 8+</li>
                <li>JavaScript (ES5-ES12)</li>
                <li>TypeScript</li>
                <li>And more...</li>
                </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Action button
        if st.button("▶️ Start Analysis", use_container_width=True, type="primary"):
            if st.session_state.workflow_state["repo_url"]:
                st.session_state.workflow_state["current_step"] = "analysis"
                st.rerun()
            else:
                st.error("Please enter a repository URL")

    # ===== Tab 2: Analysis =====
    with tabs[1]:
        st.header("🔍 Step 2: Repository Analysis")

        repo_url = st.session_state.workflow_state.get("repo_url")

        if not repo_url:
            st.warning("⚠️ Please enter a repository URL in the Input tab")
        else:
            st.info(f"Analyzing: {repo_url}")

            if st.button("🔄 Run Analysis", use_container_width=True, type="primary"):
                with st.spinner("🔍 Analyzing repository (this may take a moment)..."):
                    try:
                        progress_bar = st.progress(0)

                        # Clone repository
                        from src.services.github_service import github_service

                        progress_bar.progress(10)
                        st.write("📥 Cloning repository...")

                        repo_path = github_service.clone_repository(repo_url, depth=10)

                        progress_bar.progress(30)
                        st.write("🔍 Analyzing structure...")

                        # Run analysis chain
                        analysis_result = analysis_chain.run(repo_url, repo_path, use_cache=True)

                        progress_bar.progress(70)
                        st.write("✓ Analysis complete")

                        # Store result
                        st.session_state.workflow_state["analysis_result"] = analysis_result
                        progress_bar.progress(100)

                        st.success("✓ Repository analysis complete!")

                        # Display results
                        st.divider()
                        st.subheader("Analysis Results")

                        repo_analysis = analysis_result.get("repository_analysis", {})
                        tech_stack = analysis_result.get("technology_stack", {})

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Total Files",
                                repo_analysis.get("total_files", 0),
                            )

                        with col2:
                            st.metric(
                                "Analyzed",
                                repo_analysis.get("analyzed_files", 0),
                            )

                        with col3:
                            st.metric(
                                "Primary Language",
                                repo_analysis.get("primary_language", "Unknown"),
                            )

                        st.divider()

                        # Tech stack
                        st.subheader("Detected Technology Stack")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Languages**:")
                            for lang in tech_stack.get("languages", [])[:3]:
                                st.write(f"- {lang.get('language')} (v{lang.get('version')})")

                        with col2:
                            st.write("**Frameworks**:")
                            for fw in tech_stack.get("frameworks", [])[:3]:
                                st.write(f"- {fw.get('name')} ({fw.get('category')})")

                        st.divider()

                        # Move to migration
                        if st.button("▶️ Continue to Migration", use_container_width=True, type="primary"):
                            st.session_state.workflow_state["current_step"] = "migration"
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        logger.error(f"Analysis error: {str(e)}")

            elif st.session_state.workflow_state.get("analysis_result"):
                st.success("✓ Analysis complete (cached)")

                analysis_result = st.session_state.workflow_state["analysis_result"]

                repo_analysis = analysis_result.get("repository_analysis", {})
                tech_stack = analysis_result.get("technology_stack", {})

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Files", repo_analysis.get("total_files", 0))

                with col2:
                    st.metric("Analyzed", repo_analysis.get("analyzed_files", 0))

                with col3:
                    st.metric("Primary Language", repo_analysis.get("primary_language", "Unknown"))

                if st.button("▶️ Continue to Migration", use_container_width=True, type="primary"):
                    st.session_state.workflow_state["current_step"] = "migration"
                    st.rerun()

    # ===== Tab 3: Migration =====
    with tabs[2]:
        st.header("🔄 Step 3: Migration Planning & Code Generation")

        analysis_result = st.session_state.workflow_state.get("analysis_result")
        target_stack = st.session_state.workflow_state.get("target_stack")

        if not analysis_result:
            st.warning("⚠️ Please complete analysis first")
        else:
            st.info(f"Generating migration plan to: {target_stack}")

            current_stack = analysis_result.get("repository_analysis", {}).get("primary_language", "Unknown")

            if st.button("🔄 Generate Migration Plan", use_container_width=True, type="primary"):
                with st.spinner("📋 Creating migration strategy and generating code..."):
                    try:
                        progress_bar = st.progress(0)

                        progress_bar.progress(20)
                        st.write("📋 Planning migration strategy...")

                        # Run migration chain
                        migration_result = migration_chain.run(
                            current_tech_stack=current_stack,
                            target_tech_stack=target_stack,
                            analysis_result=analysis_result,
                            use_cache=True,
                        )

                        progress_bar.progress(80)
                        st.write("✓ Code generation complete")

                        st.session_state.workflow_state["migration_result"] = migration_result
                        progress_bar.progress(100)

                        st.success("✓ Migration plan and code generated!")

                        # Display results
                        st.divider()
                        st.subheader("Migration Strategy")

                        strategy = migration_result.get("migration_strategy", {})

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Difficulty", strategy.get("overall_difficulty", "Unknown"))

                        with col2:
                            st.metric("Effort (hours)", strategy.get("estimated_effort_hours", 0))

                        with col3:
                            st.metric("Duration (weeks)", strategy.get("estimated_duration_weeks", 0))

                        st.divider()

                        # Migration phases
                        st.subheader("Migration Phases")

                        phases = migration_result.get("migration_phases", [])
                        for phase in phases:
                            with st.expander(f"Phase {phase.get('phase')}: {phase.get('name')}"):
                                st.write(f"**Effort**: {phase.get('effort_hours')} hours")
                                st.write(f"**Risk**: {phase.get('risk_level')}")
                                st.write("**Tasks**:")
                                for task in phase.get("tasks", []):
                                    st.write(f"- {task}")

                        st.divider()

                        # Generated code
                        st.subheader("Generated Code Files")
                        files = migration_result.get("generated_code", {}).get("files_generated", [])
                        st.write(f"Total: {len(files)} files generated")
                        for file_path in files[:5]:
                            st.write(f"- {file_path}")

                        if len(files) > 5:
                            st.write(f"... and {len(files) - 5} more")

                        st.divider()

                        if st.button("▶️ Continue to Report", use_container_width=True, type="primary"):
                            st.session_state.workflow_state["current_step"] = "report"
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ Migration planning failed: {str(e)}")
                        logger.error(f"Migration error: {str(e)}")

            elif st.session_state.workflow_state.get("migration_result"):
                st.success("✓ Migration plan generated (cached)")

                migration_result = st.session_state.workflow_state["migration_result"]
                strategy = migration_result.get("migration_strategy", {})

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Difficulty", strategy.get("overall_difficulty", "Unknown"))

                with col2:
                    st.metric("Effort (hours)", strategy.get("estimated_effort_hours", 0))

                with col3:
                    st.metric("Duration (weeks)", strategy.get("estimated_duration_weeks", 0))

                if st.button("▶️ Continue to Report", use_container_width=True, type="primary"):
                    st.session_state.workflow_state["current_step"] = "report"
                    st.rerun()

    # ===== Tab 4: Report =====
    with tabs[3]:
        st.header("📊 Step 4: Generate Comprehensive Report")

        analysis_result = st.session_state.workflow_state.get("analysis_result")
        migration_result = st.session_state.workflow_state.get("migration_result")

        if not analysis_result or not migration_result:
            st.warning("⚠️ Please complete analysis and migration first")
        else:
            if st.button("📊 Generate Report", use_container_width=True, type="primary"):
                with st.spinner("📊 Generating comprehensive report..."):
                    try:
                        progress_bar = st.progress(0)

                        progress_bar.progress(30)
                        st.write("📝 Generating documentation...")

                        # Run report chain
                        report = report_generation_chain.run(
                            analysis_result=analysis_result,
                            migration_result=migration_result,
                            repo_url=st.session_state.workflow_state.get("repo_url", "unknown"),
                            use_cache=True,
                        )

                        progress_bar.progress(70)
                        st.write("✓ Report assembled")

                        st.session_state.workflow_state["report"] = report
                        progress_bar.progress(100)

                        st.success("✓ Comprehensive report generated!")

                        # Display report
                        st.divider()
                        report_viewer.render_report(report)

                        st.divider()

                        if st.button("▶️ Continue to Export", use_container_width=True, type="primary"):
                            st.session_state.workflow_state["current_step"] = "export"
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ Report generation failed: {str(e)}")
                        logger.error(f"Report error: {str(e)}")

            elif st.session_state.workflow_state.get("report"):
                st.success("✓ Report generated (cached)")

                report = st.session_state.workflow_state["report"]
                report_viewer.render_report(report)

                st.divider()

                if st.button("▶️ Continue to Export", use_container_width=True, type="primary"):
                    st.session_state.workflow_state["current_step"] = "export"
                    st.rerun()

    # ===== Tab 5: Export =====
    with tabs[4]:
        st.header("⬇️ Step 5: Download & Export")

        report = st.session_state.workflow_state.get("report")

        if not report:
            st.warning("⚠️ Please generate report first")
        else:
            st.success("✓ Report ready for download")

            st.divider()
            st.subheader("Download Options")

            col1, col2 = st.columns(2)

            with col1:
                # Markdown
                md_content = report_service.generate_markdown_report(report)
                st.download_button(
                    label="📄 Download Markdown",
                    data=md_content,
                    file_name="modernization_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

                # HTML
                html_content = report_service.generate_html_report(report)
                st.download_button(
                    label="🌐 Download HTML",
                    data=html_content,
                    file_name="modernization_report.html",
                    mime="text/html",
                    use_container_width=True,
                )

            with col2:
                # JSON
                import json

                json_content = json.dumps(report, indent=2)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_content,
                    file_name="report_data.json",
                    mime="application/json",
                    use_container_width=True,
                )

                # ZIP
                st.info("💾 Archive creation available in report service")

            st.divider()

            # Stats
            st.subheader("Report Statistics")

            col1, col2, col3 = st.columns(3)

            with col1:
                sections = report.get("sections", [])
                st.metric("Report Sections", len(sections))

            with col2:
                files = report.get("generated_files", [])
                st.metric("Generated Files", len(files))

            with col3:
                docs = report.get("documentation_files", [])
                st.metric("Documentation Files", len(docs))

            st.divider()

            st.markdown(
                """
                <div class="success-box">
                <b>✓ Modernization Complete!</b><br>
                Your comprehensive modernization report is ready. Download the files above to:
                <ul>
                <li>Review the complete analysis</li>
                <li>Study the migration roadmap</li>
                <li>Examine generated code samples</li>
                <li>Implement the recommendations</li>
                </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _get_workflow_progress() -> float:
    """Calculate workflow progress."""
    step_weights = {
        "input": 0.1,
        "analysis": 0.35,
        "migration": 0.65,
        "report": 0.85,
        "export": 1.0,
    }

    current_step = st.session_state.workflow_state.get("current_step", "input")
    return step_weights.get(current_step, 0.0)


if __name__ == "__main__":
    main()
