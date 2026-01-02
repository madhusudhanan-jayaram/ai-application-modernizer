"""
Progress Tracker Component - Streamlit component for displaying workflow progress.
Shows real-time progress updates during analysis, migration, and report generation.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ProgressStage:
    """Represents a single progress stage."""

    name: str
    description: str
    weight: float  # Progress weight (0-1)
    status: str  # pending, in_progress, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    details: Optional[str] = None


class ProgressTracker:
    """
    Component for tracking and displaying workflow progress in real-time.

    Features:
    - Multi-stage progress tracking
    - Real-time progress updates
    - Time estimation
    - Status indicators (pending, in_progress, completed, failed)
    - Error tracking and recovery
    - Progress persistence
    """

    # Predefined workflow stages
    ANALYSIS_STAGES = [
        ("Repository Cloning", "Fetching repository from GitHub", 0.15),
        ("Repository Analysis", "Analyzing repository structure and contents", 0.35),
        ("Tech Stack Detection", "Identifying frameworks and dependencies", 0.50),
    ]

    MIGRATION_STAGES = [
        ("Migration Planning", "Creating migration strategy and roadmap", 0.30),
        ("Code Generation", "Generating modernized code samples", 0.70),
    ]

    REPORT_STAGES = [
        ("Documentation Generation", "Creating migration guides and documentation", 0.50),
        ("Report Assembly", "Compiling comprehensive report", 0.75),
        ("Report Finalization", "Preparing downloads and exports", 1.00),
    ]

    def __init__(self):
        """Initialize progress tracker."""
        logger.debug("Progress tracker initialized")
        self.stages: List[ProgressStage] = []
        self.start_time: Optional[datetime] = None

    def render_progress(
        self,
        stages: List[tuple],
        current_stage: int,
        overall_progress: float,
        stage_details: Optional[str] = None,
    ) -> None:
        """
        Render progress tracker in Streamlit.

        Args:
            stages: List of (name, description, weight) tuples
            current_stage: Index of current stage (0-based)
            overall_progress: Overall progress percentage (0-1)
            stage_details: Optional details about current stage
        """
        try:
            import streamlit as st

            # Header with overall progress
            st.subheader("📊 Processing Progress")

            # Overall progress bar
            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(min(overall_progress, 1.0))
            with col2:
                st.metric("Progress", f"{int(overall_progress * 100)}%")

            # Stage breakdown
            st.markdown("---")
            st.write("**Workflow Stages**")

            for i, (stage_name, description, weight) in enumerate(stages):
                # Stage status indicator
                if i < current_stage:
                    status_emoji = "✅"
                    status_text = "Completed"
                    progress_color = "green"
                elif i == current_stage:
                    status_emoji = "⏳"
                    status_text = "In Progress"
                    progress_color = "blue"
                else:
                    status_emoji = "⏹️"
                    status_text = "Pending"
                    progress_color = "gray"

                # Stage progress indicator
                with st.container(border=True):
                    col1, col2 = st.columns([0.5, 3])

                    with col1:
                        st.write(status_emoji)

                    with col2:
                        st.write(f"**{stage_name}**")
                        st.caption(description)
                        st.caption(f"Status: {status_text}")

                        # Stage-specific details
                        if i == current_stage and stage_details:
                            st.info(f"📝 {stage_details}")

        except ImportError:
            logger.warning("Streamlit not available")

    def render_step_progress(
        self,
        steps: List[str],
        current_step: int,
        step_weights: Dict[str, float],
    ) -> float:
        """
        Render step-by-step progress indicator.

        Args:
            steps: List of step names
            current_step: Index of current step (0-based)
            step_weights: Dictionary mapping step names to progress weights

        Returns:
            Overall progress value (0-1)
        """
        try:
            import streamlit as st

            # Calculate overall progress
            overall_progress = sum(
                step_weights.get(steps[i], 0)
                for i in range(min(current_step + 1, len(steps)))
            )

            # Progress visualization
            col1, col2 = st.columns([4, 1])

            with col1:
                st.progress(min(overall_progress, 1.0))

            with col2:
                st.metric("Step", f"{current_step + 1}/{len(steps)}")

            # Step indicators
            st.write("**Workflow Steps**")

            step_cols = st.columns(len(steps))
            for i, (col, step) in enumerate(zip(step_cols, steps)):
                with col:
                    if i < current_step:
                        st.markdown(f"✅ **{step}**")
                    elif i == current_step:
                        st.markdown(f"⏳ **{step}**")
                    else:
                        st.markdown(f"⏹️ {step}")

            return overall_progress

        except ImportError:
            return 0.0

    def render_timeline(
        self, events: List[Dict[str, str]], max_events: int = 10
    ) -> None:
        """
        Render timeline of events.

        Args:
            events: List of event dictionaries with 'time', 'event', and 'status'
            max_events: Maximum number of events to display
        """
        try:
            import streamlit as st

            st.subheader("📋 Event Timeline")

            if not events:
                st.info("No events yet")
                return

            # Display latest events
            for event in events[-max_events:]:
                timestamp = event.get("time", "Unknown")
                event_text = event.get("event", "Unknown")
                status = event.get("status", "info")

                if status == "error":
                    st.error(f"[{timestamp}] {event_text}")
                elif status == "success":
                    st.success(f"[{timestamp}] {event_text}")
                elif status == "warning":
                    st.warning(f"[{timestamp}] {event_text}")
                else:
                    st.info(f"[{timestamp}] {event_text}")

        except ImportError:
            pass

    def render_metrics(
        self,
        metrics: Dict[str, str],
        columns: int = 3,
    ) -> None:
        """
        Render progress metrics.

        Args:
            metrics: Dictionary of metric names to values
            columns: Number of columns to display
        """
        try:
            import streamlit as st

            st.subheader("📈 Metrics")

            if not metrics:
                st.info("No metrics available")
                return

            # Display metrics in grid
            metric_cols = st.columns(columns)

            for i, (metric_name, metric_value) in enumerate(metrics.items()):
                with metric_cols[i % columns]:
                    st.metric(metric_name, metric_value)

        except ImportError:
            pass

    def render_status_summary(
        self,
        current_step: str,
        status: str,
        duration: Optional[str] = None,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
    ) -> None:
        """
        Render status summary with errors and warnings.

        Args:
            current_step: Current step name
            status: Current status (pending, in_progress, completed, failed)
            duration: Elapsed time as string
            errors: List of error messages
            warnings: List of warning messages
        """
        try:
            import streamlit as st

            st.subheader("📍 Current Status")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Current Step", current_step)

            with col2:
                status_emoji = (
                    "⏳"
                    if status == "in_progress"
                    else "✅"
                    if status == "completed"
                    else "⚠️"
                    if status == "failed"
                    else "⏹️"
                )
                st.metric("Status", f"{status_emoji} {status.title()}")

            with col3:
                if duration:
                    st.metric("Duration", duration)

            # Error and warning display
            st.markdown("---")

            if errors:
                st.subheader("❌ Errors")
                for error in errors:
                    st.error(error)

            if warnings:
                st.subheader("⚠️ Warnings")
                for warning in warnings:
                    st.warning(warning)

        except ImportError:
            pass

    def estimate_duration(
        self,
        current_step: int,
        total_steps: int,
        elapsed_time: float,
    ) -> str:
        """
        Estimate remaining and total duration.

        Args:
            current_step: Index of current step
            total_steps: Total number of steps
            elapsed_time: Elapsed time in seconds

        Returns:
            Duration estimate as formatted string
        """
        if current_step == 0:
            return "Estimating..."

        # Calculate average time per step
        avg_time_per_step = elapsed_time / (current_step + 1)
        remaining_steps = total_steps - current_step - 1
        estimated_remaining = avg_time_per_step * remaining_steps

        # Format time
        def format_seconds(seconds: float) -> str:
            if seconds < 60:
                return f"{int(seconds)}s"
            elif seconds < 3600:
                return f"{int(seconds / 60)}m {int(seconds % 60)}s"
            else:
                hours = int(seconds / 3600)
                minutes = int((seconds % 3600) / 60)
                return f"{hours}h {minutes}m"

        elapsed_str = format_seconds(elapsed_time)
        remaining_str = format_seconds(estimated_remaining)
        total_str = format_seconds(elapsed_time + estimated_remaining)

        return f"Elapsed: {elapsed_str} | Remaining: {remaining_str} | Total: {total_str}"

    def create_progress_callback(
        self, callback_func: Callable[[float, str], None]
    ) -> Callable:
        """
        Create a callback function for progress updates.

        Args:
            callback_func: Function that takes (progress, message)

        Returns:
            Callback function
        """

        def progress_callback(progress: float, message: str = "") -> None:
            """
            Report progress.

            Args:
                progress: Progress value (0-1)
                message: Optional progress message
            """
            try:
                callback_func(min(progress, 1.0), message)
                logger.debug(f"Progress: {progress * 100:.1f}% - {message}")
            except Exception as e:
                logger.error(f"Error in progress callback: {str(e)}")

        return progress_callback


# Global progress tracker instance
progress_tracker = ProgressTracker()
