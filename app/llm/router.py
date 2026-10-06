"""LLM Provider Router managing primary providers and graceful fallbacks."""
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider
from app.llm.ollama_provider import OllamaLLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.config.settings import settings
from app.config.logging import logger

T = TypeVar("T", bound=BaseModel)

class LLMRouter(BaseLLMProvider):
    """Resilient router that attempts primary LLM and falls back seamlessly on failure."""

    def __init__(self, primary: Optional[BaseLLMProvider] = None, fallback: Optional[BaseLLMProvider] = None):
        self.primary = primary or OllamaLLMProvider()
        self.fallback = fallback or MockLLMProvider()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            return self.primary.generate(prompt, system_prompt)
        except Exception as e:
            logger.warning(f"Primary LLM provider failed ({e}). Falling back to fallback provider.")
            return self.fallback.generate(prompt, system_prompt)

    def generate_json(self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None) -> T:
        try:
            return self.primary.generate_json(prompt, schema_cls, system_prompt)
        except Exception as e:
            logger.warning(f"Primary LLM JSON generation failed ({e}). Falling back to fallback provider.")
            return self.fallback.generate_json(prompt, schema_cls, system_prompt)
