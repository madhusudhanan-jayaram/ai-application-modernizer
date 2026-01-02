"""
Centralized configuration management using Pydantic Settings.
All application configuration loads from environment variables via .env file.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CACHE_DIR: Path = DATA_DIR / "cache"
    REPOS_DIR: Path = DATA_DIR / "repos"
    REPORTS_DIR: Path = DATA_DIR / "reports"
    PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"

    # LLM Configuration
    LLM_PROVIDER: str = "ollama"  # "ollama" or "anthropic" or "openai"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "qwen2.5-coder:7b"
    OLLAMA_NUM_PREDICT: int = 2048  # Max tokens to generate
    OLLAMA_TEMPERATURE: float = 0.1  # Low temperature for deterministic output

    # Optional: For cloud LLM providers (future)
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # GitHub Configuration
    GITHUB_TOKEN: Optional[str] = None  # Optional, for private repos

    # Application Settings
    LOG_LEVEL: str = "INFO"
    MAX_FILES_TO_ANALYZE: int = 50
    MAX_FILE_SIZE_MB: int = 5
    CONTEXT_WINDOW_TOKENS: int = 32000  # Qwen2.5-coder context window
    CHUNK_OVERLAP_TOKENS: int = 500

    # Caching
    ENABLE_CACHING: bool = True
    CACHE_TTL_HOURS: int = 24

    # Streamlit Configuration
    STREAMLIT_SERVER_PORT: int = 8501
    STREAMLIT_SERVER_HEADLESS: bool = False

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def __init__(self, **data):
        """Initialize settings and create required directories."""
        super().__init__(**data)
        self._create_directories()

    def _create_directories(self) -> None:
        """Create required directories if they don't exist."""
        for directory in [
            self.DATA_DIR,
            self.CACHE_DIR,
            self.REPOS_DIR,
            self.REPORTS_DIR,
            self.PROMPTS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def is_local_llm(self) -> bool:
        """Check if using local LLM (Ollama)."""
        return self.LLM_PROVIDER == "ollama"

    @property
    def is_anthropic_llm(self) -> bool:
        """Check if using Anthropic Claude."""
        return self.LLM_PROVIDER == "anthropic"

    @property
    def is_openai_llm(self) -> bool:
        """Check if using OpenAI."""
        return self.LLM_PROVIDER == "openai"


# Global settings instance
settings = Settings()
