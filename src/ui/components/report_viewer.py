"""
Report Viewer Component - Streamlit UI for displaying analysis/migration reports.
Provides interactive report viewing with section navigation, downloads, and filtering.
"""

from typing import Any, Dict, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ReportViewerError(Exception):
    """Exception for report viewer errors."""

    pass


class ReportViewer:
    """
    Component for displaying and interacting with modernization reports.

    Features:
    - Display multi-section reports
    - Interactive section navigation
    - Report filtering and search
    - Download capabilities (Markdown, HTML, ZIP)
    - Comparison views (before/after)
    - Export and sharing options
    - Report metadata display
    """

    def __init__(self):
        """Initialize report viewer."""
        logger.debug("Report viewer initialized")

    def render_report(self, report_data: Dict[str, Any]) -> None:
        """
        Render complete report in Streamlit.

        Args:
            report_data: Report dictionary with sections and metadata
        """
        try:
            import streamlit as st

            # Page configuration
            st.set_page_config(page_title="Modernization Report", layout="wide")

            # Header
            self._render_header(report_data)

            # Executive summary
            self._render_executive_summary(report_data.get("executive_summary", {}))

            # Navigation tabs
            st.markdown("---")

            tabs = st.tabs(
                ["Sections", "Code Samples", "Migration Plan", "Download", "Metadata"]
            )

            with tabs[0]:
                self._render_sections(report_data.get("sections", []))

            with tabs[1]:
                self._render_code_samples(report_data.get("generated_code", {}))

            with tabs[2]:
                self._render_migration_plan(report_data.get("migration_phases", []))

            with tabs[3]:
                self._render_downloads(report_data)

            with tabs[4]:
                self._render_metadata(report_data)

        except ImportError:
            logger.warning("Streamlit not available - report viewer requires Streamlit")
            raise ReportViewerError("Streamlit is required for report viewer")
        except Exception as e:
            logger.error(f"Error rendering report: {str(e)}")
            raise ReportViewerError(f"Report rendering failed: {str(e)}") from e

    def _render_header(self, report_data: Dict[str, Any]) -> None:
        """Render report header."""
        try:
            import streamlit as st

            st.markdown(
                f"# {report_data.get('report_type', 'Modernization Report')}"
            )

            # Metadata row
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Repository",
                    report_data.get("repository_url", "Unknown")
                    .split("/")[-1]
                    .replace(".git", ""),
                )

            with col2:
                st.metric(
                    "Generated",
                    report_data.get("generated_at", "Unknown")
                    [:10],  # Date only
                )

            with col3:
                st.metric("Status", report_data.get("status", "Unknown"))

        except ImportError:
            pass

    def _render_executive_summary(self, summary: Dict[str, Any]) -> None:
        """Render executive summary section."""
        try:
            import streamlit as st

            st.header("Executive Summary")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Migration Overview")
                st.write(f"**Current Stack**: {summary.get('current_stack', 'Unknown')}")
                st.write(f"**Target Stack**: {summary.get('target_stack', 'Unknown')}")
                st.write(f"**Difficulty**: {summary.get('difficulty', 'Unknown')}")

            with col2:
                st.subheader("Effort & Timeline")
                st.write(f"**Effort**: {summary.get('effort', 'Unknown')}")
                st.write(f"**Duration**: {summary.get('duration', 'Unknown')}")
                st.write(f"**Overview**: {summary.get('overview', '')}")

            # Next steps
            if summary.get("next_steps"):
                st.subheader("Next Steps")
                for i, step in enumerate(summary["next_steps"], 1):
                    st.write(f"{i}. {step}")

        except ImportError:
            pass

    def _render_sections(self, sections: List[Dict[str, Any]]) -> None:
        """Render report sections."""
        try:
            import streamlit as st

            st.header("Detailed Report")

            # Section selection
            section_titles = [s.get("title", f"Section {i}") for i, s in enumerate(sections, 1)]
            selected_section = st.selectbox("Select Section", section_titles)

            # Find and display selected section
            for section in sections:
                if section.get("title") == selected_section:
                    st.markdown(section.get("content", "No content"))
                    break

            # Or show all sections
            if st.checkbox("Show all sections"):
                for section in sections:
                    st.markdown(f"## {section.get('title', 'Section')}")
                    st.markdown(section.get("content", ""))

        except ImportError:
            pass

    def _render_code_samples(self, code_data: Dict[str, Any]) -> None:
        """Render generated code samples."""
        try:
            import streamlit as st

            st.header("Generated Code Samples")

            files = code_data.get("files_generated", [])

            if not files:
                st.info("No code files generated")
                return

            # File selector
            selected_file = st.selectbox("Select Code File", files)

            st.code(f"# {selected_file}\n# Code content would be displayed here", language="python")

            # File list
            st.subheader("All Generated Files")
            st.write(f"Total: {len(files)} files")

            for file_path in files:
                st.write(f"- `{file_path}`")

        except ImportError:
            pass

    def _render_migration_plan(self, phases: List[Dict[str, Any]]) -> None:
        """Render migration plan with phases."""
        try:
            import streamlit as st

            st.header("Migration Roadmap")

            if not phases:
                st.info("No migration phases defined")
                return

            # Timeline visualization
            for i, phase in enumerate(phases, 1):
                with st.expander(
                    f"Phase {phase.get('phase', i)}: {phase.get('name', 'Unknown')}"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Effort**: {phase.get('effort_hours', 0)} hours")
                        st.write(f"**Risk Level**: {phase.get('risk_level', 'Unknown')}")

                    with col2:
                        dependencies = phase.get("dependencies", [])
                        if dependencies:
                            st.write(f"**Dependencies**: {', '.join(dependencies)}")
                        else:
                            st.write("**Dependencies**: None")

                    st.write("**Tasks**:")
                    for task in phase.get("tasks", []):
                        st.write(f"- {task}")

        except ImportError:
            pass

    def _render_downloads(self, report_data: Dict[str, Any]) -> None:
        """Render download options."""
        try:
            import streamlit as st

            st.header("Download Report")

            from src.services.report_service import report_service

            # Markdown download
            md_content = report_service.generate_markdown_report(report_data)
            st.download_button(
                label="📄 Download Markdown Report",
                data=md_content,
                file_name="modernization_report.md",
                mime="text/markdown",
            )

            # HTML download
            html_content = report_service.generate_html_report(report_data)
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_content,
                file_name="modernization_report.html",
                mime="text/html",
            )

            # JSON download
            import json

            json_content = json.dumps(report_data, indent=2)
            st.download_button(
                label="📊 Download JSON Data",
                data=json_content,
                file_name="report_data.json",
                mime="application/json",
            )

            st.info("💾 All formats available for download above")

        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Error rendering downloads: {str(e)}")

    def _render_metadata(self, report_data: Dict[str, Any]) -> None:
        """Render report metadata."""
        try:
            import streamlit as st

            st.header("Report Metadata")

            # Basic info
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Report Type**")
                st.write(report_data.get("report_type", "Unknown"))

                st.write("**Repository**")
                st.write(report_data.get("repository_url", "Unknown"))

            with col2:
                st.write("**Generated**")
                st.write(report_data.get("generated_at", "Unknown"))

                st.write("**Status**")
                st.write(report_data.get("status", "Unknown"))

            # Files
            st.subheader("Generated Files")
            files = report_data.get("generated_files", [])
            st.write(f"Total: {len(files)} files")

            for file_info in files[:10]:  # Show first 10
                st.write(f"- {file_info.get('path', 'Unknown')} ({file_info.get('type', 'Unknown')})")

            if len(files) > 10:
                st.write(f"... and {len(files) - 10} more files")

            # Documentation
            st.subheader("Documentation Files")
            docs = report_data.get("documentation_files", [])
            for doc in docs:
                st.write(f"- {doc}")

        except ImportError:
            pass

    def render_comparison(
        self,
        before_data: Dict[str, Any],
        after_data: Dict[str, Any],
    ) -> None:
        """
        Render before/after comparison view.

        Args:
            before_data: Before (current) state data
            after_data: After (target) state data
        """
        try:
            import streamlit as st

            st.header("Technology Stack Comparison")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Current Stack")
                self._render_tech_stack(before_data.get("technology_stack", {}))

            with col2:
                st.subheader("Target Stack")
                self._render_tech_stack(after_data.get("technology_stack", {}))

        except ImportError:
            pass

    def _render_tech_stack(self, tech_stack: Dict[str, Any]) -> None:
        """Render technology stack details."""
        try:
            import streamlit as st

            st.write(f"**Primary Language**: {tech_stack.get('primary_language', 'Unknown')}")

            languages = tech_stack.get("languages", [])
            if languages:
                st.write("**Languages**:")
                for lang in languages:
                    st.write(f"- {lang.get('language', 'Unknown')} (v{lang.get('version', 'Unknown')})")

            frameworks = tech_stack.get("frameworks", [])
            if frameworks:
                st.write("**Frameworks**:")
                for fw in frameworks:
                    st.write(f"- {fw.get('name', 'Unknown')} ({fw.get('category', 'Unknown')})")

        except ImportError:
            pass

    def export_summary(self, report_data: Dict[str, Any]) -> str:
        """
        Export report as text summary.

        Args:
            report_data: Report dictionary

        Returns:
            Text summary
        """
        summary = report_data.get("executive_summary", {})

        text = f"""
MODERNIZATION REPORT SUMMARY
{'=' * 60}

Repository: {report_data.get('repository_url', 'Unknown')}
Generated: {report_data.get('generated_at', 'Unknown')}

MIGRATION STRATEGY
{'-' * 60}
Current Stack: {summary.get('current_stack', 'Unknown')}
Target Stack: {summary.get('target_stack', 'Unknown')}
Difficulty: {summary.get('difficulty', 'Unknown')}
Effort: {summary.get('effort', 'Unknown')}
Duration: {summary.get('duration', 'Unknown')}

NEXT STEPS
{'-' * 60}
"""

        for i, step in enumerate(summary.get("next_steps", []), 1):
            text += f"{i}. {step}\n"

        return text


# Global report viewer instance
report_viewer = ReportViewer()
