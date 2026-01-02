"""
Base Agent - Abstract base class for all LangChain agents.
Implements ReAct pattern (Reasoning + Acting) with tool registration.
Provides common agent functionality: memory, error handling, logging.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

from src.services.code_analysis_service import code_analysis_service
from src.services.github_service import github_service
from src.services.llm_service import llm_service
from src.utils.cache_manager import cache_manager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AgentError(Exception):
    """Base exception for agent errors."""

    pass


class AgentExecutionError(AgentError):
    """Raised when agent execution fails."""

    pass


class ToolError(AgentError):
    """Raised when tool execution fails."""

    pass


class BaseAgent(ABC):
    """
    Abstract base class for all LangChain agents.

    Features:
    - ReAct pattern (Reasoning + Acting)
    - Tool registration and management
    - LLM integration (local Qwen via Ollama)
    - Error handling and recovery
    - Memory and context management
    - Logging and monitoring
    """

    def __init__(
        self,
        agent_name: str,
        description: str,
        system_prompt: Optional[str] = None,
        max_iterations: int = 10,
        temperature: float = 0.1,
    ):
        """
        Initialize base agent.

        Args:
            agent_name: Name of agent (e.g., 'RepositoryAnalyzer')
            description: Agent description for logging
            system_prompt: Initial system prompt
            max_iterations: Max tool calls per execution
            temperature: LLM temperature (0.1 for deterministic code generation)
        """
        self.agent_name = agent_name
        self.description = description
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.max_iterations = max_iterations
        self.temperature = temperature

        # Initialize services
        self.llm_service = llm_service
        self.github_service = github_service
        self.cache_manager = cache_manager
        self.code_analysis_service = code_analysis_service

        # Tool registry
        self.tools: List[Tool] = []
        self.tool_registry: Dict[str, callable] = {}

        # Execution state
        self.current_input = None
        self.execution_history = []

        logger.info(f"✓ {self.agent_name} initialized: {description}")

    def register_tool(
        self,
        name: str,
        description: str,
        func: callable,
    ) -> None:
        """
        Register a tool for this agent.

        Args:
            name: Tool name (used in prompts)
            description: Human-readable tool description
            func: Callable that implements tool logic

        Raises:
            ToolError: If tool registration fails
        """
        try:
            # Create LangChain Tool
            tool = Tool(
                name=name,
                description=description,
                func=func,
            )

            self.tools.append(tool)
            self.tool_registry[name] = func

            logger.debug(f"Registered tool: {name}")

        except Exception as e:
            raise ToolError(f"Failed to register tool {name}: {str(e)}") from e

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input before execution.

        Subclasses can override for custom validation.

        Args:
            input_data: Input dictionary

        Returns:
            True if valid

        Raises:
            AgentError: If validation fails
        """
        if not input_data:
            raise AgentError(f"{self.agent_name}: Empty input")

        return True

    def prepare_context(self, input_data: Dict[str, Any]) -> str:
        """
        Prepare context string for LLM.

        Subclasses can override to customize context.

        Args:
            input_data: Input dictionary

        Returns:
            Context string for LLM prompt
        """
        context_parts = []

        # Add agent context
        context_parts.append(f"Agent: {self.agent_name}")
        context_parts.append(f"Task: {input_data.get('task', 'Not specified')}")

        # Add repository context if available
        if "repo_url" in input_data:
            context_parts.append(f"Repository: {input_data['repo_url']}")

        if "repo_path" in input_data:
            context_parts.append(f"Local Path: {input_data['repo_path']}")

        return "\n".join(context_parts)

    def execute(
        self,
        input_data: Dict[str, Any],
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute agent with given input.

        Args:
            input_data: Input dictionary with task and context
            use_cache: Whether to use cached results

        Returns:
            Execution result dictionary

        Raises:
            AgentExecutionError: If execution fails
        """
        logger.info(f"[{self.agent_name}] Starting execution")
        self.current_input = input_data

        try:
            # Validate input
            self.validate_input(input_data)

            # Check cache
            if use_cache:
                cache_key = self._make_cache_key(input_data)
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info(f"[{self.agent_name}] Cache hit")
                    return cached_result

            # Prepare context
            context = self.prepare_context(input_data)

            # Build prompt
            prompt = self._build_prompt(input_data, context)

            # Execute with LLM
            response = self._execute_with_tools(prompt, input_data)

            # Post-process result
            result = self._process_result(response, input_data)

            # Cache result
            if use_cache:
                cache_key = self._make_cache_key(input_data)
                self.cache_manager.set(result, cache_key)

            # Log execution
            self.execution_history.append(
                {
                    "input": input_data,
                    "result": result,
                    "success": True,
                }
            )

            logger.info(f"[{self.agent_name}] ✓ Execution complete")
            return result

        except Exception as e:
            logger.error(f"[{self.agent_name}] Execution failed: {str(e)}")

            # Log failure
            self.execution_history.append(
                {
                    "input": input_data,
                    "error": str(e),
                    "success": False,
                }
            )

            raise AgentExecutionError(
                f"{self.agent_name} execution failed: {str(e)}"
            ) from e

    def _execute_with_tools(self, prompt: str, input_data: Dict[str, Any]) -> str:
        """
        Execute agent with tools using ReAct pattern.

        Args:
            prompt: Full prompt for LLM
            input_data: Input data (for context)

        Returns:
            LLM response string
        """
        try:
            # Check if we have tools
            if not self.tools:
                # No tools, just invoke LLM directly
                logger.debug(f"[{self.agent_name}] No tools registered, using LLM directly")
                response = self.llm_service.invoke(prompt, self.temperature)
                return response

            # With tools: Create ReAct agent
            logger.debug(f"[{self.agent_name}] Executing with {len(self.tools)} tools")

            # Create LangChain agent
            agent = create_react_agent(
                llm=self._get_langchain_llm(),
                tools=self.tools,
                prompt=self._get_react_prompt_template(),
            )

            # Create executor
            executor = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                verbose=False,
                max_iterations=self.max_iterations,
            )

            # Run agent
            result = executor.invoke({"input": prompt})

            return result.get("output", "")

        except Exception as e:
            logger.warning(
                f"[{self.agent_name}] Tool execution failed, falling back to LLM: {str(e)}"
            )
            # Fallback: Just use LLM without tools
            response = self.llm_service.invoke(prompt, self.temperature)
            return response

    def _get_langchain_llm(self) -> Any:
        """
        Get LangChain LLM instance.

        Returns:
            LangChain-compatible LLM
        """
        # Import here to avoid circular dependencies
        try:
            from langchain_community.llms import Ollama

            return Ollama(
                model="qwen2.5-coder:7b",
                base_url="http://localhost:11434",
                temperature=self.temperature,
            )
        except ImportError:
            logger.warning("langchain_community not installed, using LLM service directly")
            return None

    def _get_react_prompt_template(self) -> PromptTemplate:
        """
        Get ReAct prompt template.

        Returns:
            PromptTemplate for ReAct pattern
        """
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:"""

        return PromptTemplate.from_template(template)

    def _build_prompt(self, input_data: Dict[str, Any], context: str) -> str:
        """
        Build prompt for LLM execution.

        Subclasses can override for custom prompts.

        Args:
            input_data: Input dictionary
            context: Prepared context string

        Returns:
            Full prompt for LLM
        """
        prompt_parts = [
            self.system_prompt,
            "",
            context,
            "",
            "Task:",
            input_data.get("task", "Analyze the provided information"),
            "",
            "Additional Context:",
            input_data.get("context", "No additional context provided"),
        ]

        return "\n".join(prompt_parts)

    def _process_result(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process LLM response.

        Subclasses can override for custom processing.

        Args:
            response: Raw LLM response
            input_data: Original input data

        Returns:
            Processed result dictionary
        """
        return {
            "agent": self.agent_name,
            "response": response,
            "input_task": input_data.get("task"),
            "success": True,
        }

    def _make_cache_key(self, input_data: Dict[str, Any]) -> str:
        """
        Create cache key from input data.

        Args:
            input_data: Input dictionary

        Returns:
            Cache key string
        """
        key_parts = [
            self.agent_name,
            input_data.get("repo_url", "no_repo"),
            input_data.get("task", "generic"),
        ]

        return f"agent_{'_'.join(key_parts)}"

    def _get_default_system_prompt(self) -> str:
        """
        Get default system prompt for agent.

        Subclasses can override.

        Returns:
            System prompt string
        """
        return f"""You are {self.agent_name}, an expert code analyst and software architect.

Your role is to analyze source code repositories and provide detailed insights.

You are highly skilled at:
- Understanding software architecture and design patterns
- Analyzing code quality and identifying improvements
- Detecting technology stacks and frameworks
- Planning software migrations and modernization

Always provide detailed, actionable analysis with specific recommendations.
Focus on clarity, correctness, and practical value."""

    def get_execution_history(self) -> List[Dict]:
        """
        Get execution history.

        Returns:
            List of execution records
        """
        return self.execution_history

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history = []

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.agent_name}(tools={len(self.tools)}, iterations={self.max_iterations})"
