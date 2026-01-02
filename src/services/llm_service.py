"""
LLM Service - Handles interaction with local Ollama LLM.
Provides abstraction layer for LLM provider (Ollama, Anthropic, OpenAI).
All LangChain agents depend on this service for LLM access.
"""

import re
from typing import Optional

from langchain_community.llms import Ollama
from src.utils.logger import setup_logger

from config.settings import settings

logger = setup_logger(__name__)


class OllamaConnectionError(Exception):
    """Raised when Ollama service is not available."""

    pass


class TokenCountError(Exception):
    """Raised when token counting fails."""

    pass


class LLMService:
    """
    Service for interacting with local Ollama LLM.

    Handles:
    - Connection to Ollama endpoint
    - Token counting and context window management
    - Retry logic and error handling
    - Cost tracking (local inference is free)
    - Model configuration
    """

    def __init__(self):
        """Initialize LLM service with Ollama connection."""
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.MODEL_NAME
        self.temperature = settings.OLLAMA_TEMPERATURE
        self.num_predict = settings.OLLAMA_NUM_PREDICT
        self.context_window = settings.CONTEXT_WINDOW_TOKENS

        self.llm = None
        self.total_tokens_used = 0
        self.total_requests = 0

        logger.info(f"Initializing LLM Service with model: {self.model_name}")
        logger.info(f"Ollama endpoint: {self.base_url}")
        self._initialize_ollama()

    def _initialize_ollama(self) -> None:
        """
        Initialize Ollama connection.

        Raises:
            OllamaConnectionError: If Ollama is not available
        """
        try:
            self.llm = Ollama(
                base_url=self.base_url,
                model=self.model_name,
                temperature=self.temperature,
            )

            # Test connection by calling a simple prompt
            self._test_connection()
            logger.info(f"✓ Successfully connected to Ollama on {self.base_url}")

        except Exception as e:
            error_msg = f"Failed to initialize Ollama: {str(e)}"
            logger.error(error_msg)
            raise OllamaConnectionError(error_msg) from e

    def _test_connection(self) -> None:
        """
        Test Ollama connection with a simple prompt.

        Raises:
            OllamaConnectionError: If connection test fails
        """
        try:
            response = self.llm.invoke("Hello")
            if not response:
                raise ValueError("Empty response from Ollama")
            logger.debug("Ollama connection test successful")
        except Exception as e:
            raise OllamaConnectionError(f"Connection test failed: {str(e)}") from e

    def invoke(self, prompt: str, temperature: Optional[float] = None) -> str:
        """
        Send a prompt to the LLM and get a response.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Optional temperature override (0.0-1.0)

        Returns:
            LLM response text

        Raises:
            OllamaConnectionError: If LLM is not available
        """
        if not self.llm:
            raise OllamaConnectionError("LLM not initialized")

        try:
            # Override temperature if provided
            if temperature is not None:
                original_temp = self.llm.temperature
                self.llm.temperature = temperature

            logger.debug(f"Invoking LLM with prompt length: {len(prompt)} chars")
            response = self.llm.invoke(prompt)

            # Restore original temperature
            if temperature is not None:
                self.llm.temperature = original_temp

            # Track usage
            self.total_requests += 1
            estimated_tokens = self._estimate_tokens(prompt + response)
            self.total_tokens_used += estimated_tokens

            logger.debug(f"LLM response length: {len(response)} chars, "
                        f"estimated tokens: {estimated_tokens}")

            return response

        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}")
            raise OllamaConnectionError(f"LLM invocation failed: {str(e)}") from e

    def invoke_with_streaming(self, prompt: str, temperature: Optional[float] = None):
        """
        Send a prompt and stream the response.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Optional temperature override

        Yields:
            Text chunks from the response
        """
        if not self.llm:
            raise OllamaConnectionError("LLM not initialized")

        try:
            # Note: Ollama in LangChain may not support streaming
            # Fall back to invoke() for now
            logger.debug("Streaming requested - using invoke (Ollama streaming TBD)")
            response = self.invoke(prompt, temperature)
            yield response

        except Exception as e:
            logger.error(f"LLM streaming failed: {str(e)}")
            raise OllamaConnectionError(f"LLM streaming failed: {str(e)}") from e

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for given text.
        Uses simple heuristic: ~4 characters per token (average for English).

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Simple approximation: average ~4 chars per token
        # More accurate counting would require tokenizer
        estimated = len(text) // 4
        logger.debug(f"Estimated tokens for {len(text)} chars: {estimated}")
        return max(1, estimated)  # At least 1 token

    def can_fit_in_context(self, text: str, reserve_tokens: int = 500) -> bool:
        """
        Check if text can fit in context window with reserve.

        Args:
            text: Text to check
            reserve_tokens: Tokens to reserve for output

        Returns:
            True if text fits in context window
        """
        estimated_tokens = self.count_tokens(text)
        available = self.context_window - reserve_tokens
        fits = estimated_tokens <= available

        logger.debug(f"Context check: {estimated_tokens} tokens, "
                    f"available: {available}, fits: {fits}")

        return fits

    def get_remaining_context(self, used_tokens: int = 0) -> int:
        """
        Get remaining context window tokens.

        Args:
            used_tokens: Tokens already used in conversation

        Returns:
            Remaining tokens available
        """
        remaining = self.context_window - used_tokens - settings.CHUNK_OVERLAP_TOKENS
        return max(0, remaining)

    def estimate_completion_tokens(self, prompt: str, expected_response_ratio: float = 1.5) -> int:
        """
        Estimate tokens needed for LLM completion.

        Args:
            prompt: Input prompt
            expected_response_ratio: Expected response size relative to prompt (default 1.5x)

        Returns:
            Estimated tokens for prompt + response
        """
        prompt_tokens = self.count_tokens(prompt)
        # Estimate response will be 1.5x the prompt size
        response_tokens = int(prompt_tokens * expected_response_ratio)
        total = prompt_tokens + response_tokens

        logger.debug(f"Estimated completion: {prompt_tokens} (prompt) + "
                    f"{response_tokens} (response) = {total} total tokens")

        return total

    def validate_prompt(self, prompt: str) -> tuple[bool, Optional[str]]:
        """
        Validate a prompt before sending to LLM.

        Args:
            prompt: Prompt to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check not empty
        if not prompt or not prompt.strip():
            return False, "Prompt cannot be empty"

        # Check not too large (even with 32k context, some reserve needed)
        estimated_tokens = self.count_tokens(prompt)
        if estimated_tokens > self.context_window - 1000:
            return False, f"Prompt too large ({estimated_tokens} tokens, max {self.context_window - 1000})"

        # Check for suspicious patterns
        dangerous_patterns = [
            r"__import__",
            r"eval\(",
            r"exec\(",
            r"system\(",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False, f"Suspicious pattern detected: {pattern}"

        return True, None

    def _estimate_tokens(self, text: str) -> int:
        """Internal token estimation using simple heuristic."""
        # Refined heuristic: average ~4 characters per token for English
        return max(1, len(text) // 4)

    def get_stats(self) -> dict:
        """
        Get LLM service statistics.

        Returns:
            Dictionary with service statistics
        """
        return {
            "model": self.model_name,
            "endpoint": self.base_url,
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "context_window": self.context_window,
            "temperature": self.temperature,
            "api_cost": 0.0,  # Local LLM = free!
            "is_local": True,
        }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self.total_tokens_used = 0
        self.total_requests = 0
        logger.info("LLM service statistics reset")

    def health_check(self) -> bool:
        """
        Check if LLM service is healthy.

        Returns:
            True if service is healthy and responsive
        """
        try:
            self._test_connection()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False


# Global LLM service instance
try:
    llm_service = LLMService()
except OllamaConnectionError as e:
    logger.critical(f"Failed to initialize LLM service: {str(e)}")
    logger.critical("Make sure Ollama is running: ollama serve")
    llm_service = None
