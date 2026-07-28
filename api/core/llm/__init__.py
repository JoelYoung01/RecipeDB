"""LLM client abstractions for meal-plan wizard and future OpenRouter wiring."""

from api.core.llm.client import LlmClient, get_llm_client

__all__ = ["LlmClient", "get_llm_client"]
