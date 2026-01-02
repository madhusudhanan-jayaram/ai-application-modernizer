"""
Tech Stack Selector Component - Streamlit component for selecting target technology stack.
Provides predefined options and custom input for target technology selection.
"""

from typing import List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TechStackSelector:
    """
    Component for selecting target technology stack.

    Features:
    - Predefined technology stack options
    - Category-based organization
    - Custom stack specification
    - Stack compatibility information
    - Migration difficulty hints
    """

    # Predefined stacks organized by category
    PREDEFINED_STACKS = {
        "Python": [
            "Python 3 + FastAPI",
            "Python 3 + Flask",
            "Python 3 + Django",
            "Python 3 + Fastapi + PostgreSQL",
        ],
        "Java": [
            "Java 11+ + Spring Boot",
            "Java 17+ + Spring Boot + PostgreSQL",
            "Java 8 + Spring Framework",
        ],
        "JavaScript/Node.js": [
            "Node.js + Express",
            "Node.js + Express + React",
            "Node.js + NestJS",
            "Node.js + GraphQL",
        ],
        "TypeScript": [
            "TypeScript + NestJS",
            "TypeScript + Express",
            "TypeScript + NextJS",
        ],
        "Frontend": [
            "React + TypeScript",
            "Vue.js 3 + TypeScript",
            "Angular 15+",
            "Svelte",
        ],
        "Other": [
            "Go + Gin",
            "Go + Echo",
            "Rust + Actix",
            "Rust + Rocket",
            "C# + ASP.NET Core",
        ],
    }

    # Migration difficulty hints
    DIFFICULTY_HINTS = {
        ("Python 2", "Python 3"): "easy",
        ("Python + Flask", "Python + FastAPI"): "medium",
        ("Monolith", "Microservices"): "hard",
        ("Synchronous", "Asynchronous"): "medium",
    }

    def __init__(self):
        """Initialize tech stack selector component."""
        logger.debug("Tech stack selector initialized")

    def render_streamlit(self) -> str:
        """
        Render tech stack selector in Streamlit.

        Returns:
            Selected target tech stack
        """
        try:
            import streamlit as st

            st.subheader("🎯 Target Technology Stack")

            # Category selector
            categories = list(self.PREDEFINED_STACKS.keys())
            categories.insert(0, "All Options")

            selected_category = st.radio(
                "Select Category",
                categories,
                horizontal=True,
                help="Choose a technology category to filter options",
            )

            # Stack selector
            if selected_category == "All Options":
                all_stacks = []
                for stacks in self.PREDEFINED_STACKS.values():
                    all_stacks.extend(stacks)
                all_stacks.append("Other (Custom)")

                selected_stack = st.selectbox(
                    "Choose Target Stack",
                    all_stacks,
                    help="Select your target technology stack for migration",
                )
            else:
                stacks = self.PREDEFINED_STACKS[selected_category] + ["Other (Custom)"]

                selected_stack = st.selectbox(
                    f"Choose {selected_category} Stack",
                    stacks,
                    help="Select your target technology stack for migration",
                )

            # Custom input
            if selected_stack == "Other (Custom)":
                selected_stack = st.text_input(
                    "Specify Custom Stack",
                    placeholder="e.g., Go + PostgreSQL + Kubernetes",
                    help="Enter your custom target technology stack",
                )

            # Info boxes
            self._render_stack_info(selected_stack)

            return selected_stack

        except ImportError:
            logger.warning("Streamlit not available - using CLI mode")
            return self._get_cli_input()

    def _render_stack_info(self, selected_stack: str) -> None:
        """Render information about selected stack."""
        try:
            import streamlit as st

            if selected_stack:
                st.divider()

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**✓ Selected Stack**")
                    st.write(f"`{selected_stack}`")

                    # Show components
                    components = self._extract_components(selected_stack)
                    if components:
                        st.write("**Components**:")
                        for component in components:
                            st.write(f"- {component}")

                with col2:
                    # Migration difficulty
                    difficulty = self._estimate_difficulty(selected_stack)
                    if difficulty:
                        emoji = "✓" if difficulty == "easy" else "⚠" if difficulty == "medium" else "⚠⚠"
                        st.write("**Typical Difficulty**")
                        st.write(f"{emoji} {difficulty.title()}")

        except ImportError:
            pass

    def _extract_components(self, stack: str) -> List[str]:
        """Extract individual components from stack string."""
        return [c.strip() for c in stack.split("+")]

    def _estimate_difficulty(self, target_stack: str) -> Optional[str]:
        """Estimate migration difficulty for target stack."""
        if "FastAPI" in target_stack:
            return "medium"
        elif "Spring Boot" in target_stack:
            return "medium"
        elif "NestJS" in target_stack:
            return "medium"
        elif "Microservices" in target_stack:
            return "hard"
        elif "Kubernetes" in target_stack:
            return "hard"

        return None

    def _get_cli_input(self) -> str:
        """Get input from CLI."""
        print("\n🎯 Target Technology Stack Selection\n")

        # Display categories
        categories = list(self.PREDEFINED_STACKS.keys())

        for i, category in enumerate(categories, 1):
            print(f"\n{i}. {category}")
            stacks = self.PREDEFINED_STACKS[category]

            for j, stack in enumerate(stacks, 1):
                print(f"   {j}. {stack}")

        print(f"\n{len(categories) + 1}. Other (Custom)")

        while True:
            try:
                choice = int(input("\nSelect category number: "))

                if choice == len(categories) + 1:
                    return input("Enter custom target stack: ").strip()

                if 1 <= choice <= len(categories):
                    category = categories[choice - 1]
                    stacks = self.PREDEFINED_STACKS[category]

                    print(f"\n{category} Options:")
                    for i, stack in enumerate(stacks, 1):
                        print(f"{i}. {stack}")

                    stack_choice = int(input("\nSelect stack number: "))

                    if 1 <= stack_choice <= len(stacks):
                        return stacks[stack_choice - 1]
                    else:
                        print("Invalid choice")
                else:
                    print("Invalid category")

            except ValueError:
                print("Please enter a valid number")

    def get_stack_description(self, stack: str) -> str:
        """
        Get description of technology stack.

        Args:
            stack: Technology stack string

        Returns:
            Description
        """
        components = self._extract_components(stack)

        description = f"Target stack: {', '.join(components)}"

        # Add notes
        if "FastAPI" in stack:
            description += " (Modern async Python web framework)"
        elif "Spring Boot" in stack:
            description += " (Enterprise Java framework)"
        elif "NestJS" in stack:
            description += " (Full-stack Node.js framework)"

        return description


# Global instance
tech_stack_selector = TechStackSelector()
