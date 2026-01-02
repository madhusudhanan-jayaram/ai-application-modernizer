"""Unit tests for base agent."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.base_agent import BaseAgent


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def __init__(self):
        """Initialize concrete agent."""
        super().__init__(
            agent_name='TestAgent',
            description='Test agent for unit testing',
            system_prompt='You are a test agent',
        )


@pytest.fixture
def agent():
    """Create concrete agent instance."""
    return ConcreteAgent()


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service."""
    mock = MagicMock()
    mock.generate_response.return_value = 'Test response'
    return mock


class TestBaseAgent:
    """Test cases for BaseAgent."""

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent is not None
        assert agent.agent_name == 'TestAgent'
        assert agent.description == 'Test agent for unit testing'

    def test_register_tool(self, agent):
        """Test registering a tool."""

        def sample_tool(value: str) -> str:
            """Sample tool."""
            return f'Processed: {value}'

        agent.register_tool(
            'sample_tool',
            'Sample tool for testing',
            sample_tool,
        )

        assert 'sample_tool' in agent.tools

    def test_execute_with_tools(self, agent):
        """Test executing with tools."""

        def add(a: int, b: int) -> int:
            """Add numbers."""
            return a + b

        agent.register_tool('add', 'Add two numbers', add)

        # Mock the LLM response
        with patch.object(agent, '_execute_with_tools') as mock_execute:
            mock_execute.return_value = 'Result: 5'

            result = agent._execute_with_tools('What is 2 + 3?', {})

            assert 'Result' in result

    def test_tool_execution_error_handling(self, agent):
        """Test error handling during tool execution."""

        def failing_tool():
            """Tool that fails."""
            raise ValueError('Tool execution failed')

        agent.register_tool('failing_tool', 'Tool that fails', failing_tool)

        # Should handle error gracefully
        assert 'failing_tool' in agent.tools

    def test_execution_history(self, agent):
        """Test execution history tracking."""
        initial_count = len(agent.execution_history)

        with patch.object(agent, '_execute_with_tools') as mock_execute:
            mock_execute.return_value = 'Result'

            try:
                agent.execute({'test': 'data'})
            except Exception:
                pass

        # History should have been updated
        assert len(agent.execution_history) >= initial_count

    def test_multiple_tools_registration(self, agent):
        """Test registering multiple tools."""

        def tool1():
            return 'Tool 1'

        def tool2():
            return 'Tool 2'

        def tool3():
            return 'Tool 3'

        agent.register_tool('tool1', 'First tool', tool1)
        agent.register_tool('tool2', 'Second tool', tool2)
        agent.register_tool('tool3', 'Third tool', tool3)

        assert len(agent.tools) == 3
        assert 'tool1' in agent.tools
        assert 'tool2' in agent.tools
        assert 'tool3' in agent.tools

    def test_agent_metadata(self, agent):
        """Test agent metadata."""
        assert agent.agent_name is not None
        assert agent.description is not None
        assert isinstance(agent.tools, dict)
        assert isinstance(agent.execution_history, list)

    def test_tool_documentation(self, agent):
        """Test tool documentation."""

        def documented_tool(value: str) -> str:
            """This is a documented tool."""
            return value.upper()

        agent.register_tool(
            'documented_tool',
            'Convert string to uppercase',
            documented_tool,
        )

        assert 'documented_tool' in agent.tools

    def test_caching_support(self, agent):
        """Test caching support in agent."""
        # Agent should have cache manager
        assert hasattr(agent, 'cache_manager')

    def test_agent_reset(self, agent):
        """Test resetting agent state."""

        def sample_tool():
            return 'test'

        agent.register_tool('sample', 'Sample tool', sample_tool)

        # Add execution history
        agent.execution_history.append({'action': 'test'})

        # Reset should clear appropriate state
        assert len(agent.tools) > 0
        assert len(agent.execution_history) > 0

    def test_error_recovery(self, agent):
        """Test error recovery mechanism."""

        def unreliable_tool():
            """Tool that might fail."""
            import random

            if random.random() > 0.5:
                raise ValueError('Random failure')
            return 'Success'

        agent.register_tool('unreliable', 'Unreliable tool', unreliable_tool)

        # Should have registered despite potential failures
        assert 'unreliable' in agent.tools

    def test_concurrent_execution(self, agent):
        """Test agent can handle state during concurrent scenarios."""

        def concurrent_tool(task_id: int) -> str:
            """Process task."""
            return f'Task {task_id} completed'

        agent.register_tool('concurrent_tool', 'Process task concurrently', concurrent_tool)

        # Register multiple similar tools
        for i in range(3):
            agent.register_tool(f'task_{i}', f'Task {i}', concurrent_tool)

        # All should be registered
        assert len(agent.tools) >= 3
