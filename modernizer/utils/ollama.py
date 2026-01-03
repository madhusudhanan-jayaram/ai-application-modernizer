"""Ollama + LangChain configuration for a shared local LLM.

This module exposes a single factory, `get_llm()`, which returns a
shared ChatOllama instance configured for qwen2.5-coder:7b running on a
local Ollama server. All calls are traced locally to a log file so you
can inspect prompts and responses without any cloud dependency.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from langchain_community.chat_models import ChatOllama
from langchain_core.callbacks import BaseCallbackHandler


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL_NAME = "qwen2.5-coder:7b"
DEFAULT_TEMPERATURE = 0.1
# Cap the number of tokens generated per call to keep
# each step of the workflow reasonably fast on local
# hardware while still allowing sufficiently rich outputs.
DEFAULT_MAX_TOKENS = 768

TRACE_FILE = Path("output/llm_trace.log")


class SimpleTraceHandler(BaseCallbackHandler):
    """Log prompts and responses from the local LLM to a file."""

    def on_llm_start(self, serialized, prompts, **kwargs):  # type: ignore[override]
        TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with TRACE_FILE.open("a", encoding="utf-8") as f:
            f.write("\n=== LLM START ===\n")
            for p in prompts:
                f.write(f"PROMPT:\n{p}\n")

    def on_llm_end(self, response, **kwargs):  # type: ignore[override]
        with TRACE_FILE.open("a", encoding="utf-8") as f:
            f.write("--- LLM END ---\n")
            f.write(f"RESPONSE:\n{response.generations}\n")


@lru_cache(maxsize=1)
def get_llm(
    model: str = DEFAULT_MODEL_NAME,
    base_url: str = DEFAULT_OLLAMA_BASE_URL,
    temperature: float = DEFAULT_TEMPERATURE,
    num_predict: int = DEFAULT_MAX_TOKENS,
) -> ChatOllama:
    """Return a shared ChatOllama instance.

    All agents in the modernizer should call this instead of constructing
    their own LLMs to ensure consistent configuration and efficient reuse.
    """

    llm = ChatOllama(
        model=model,
        base_url=base_url,
        temperature=temperature,
        num_predict=num_predict,
        callbacks=[SimpleTraceHandler()],
    )
    return llm
