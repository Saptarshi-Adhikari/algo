"""LLM Provider Router implementing Local-First priority and graceful fallbacks."""
from typing import Type, TypeVar, Optional, List
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider
from app.llm.ollama_provider import OllamaLLMProvider
from app.llm.gemini_provider import GeminiLLMProvider
from app.llm.openrouter_provider import OpenRouterLLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.config.logging import logger

T = TypeVar("T", bound=BaseModel)

class LLMRouter(BaseLLMProvider):
    """Resilient router enforcing Local-First priority order:
    1. Ollama (PRIMARY)
    2. Gemini API (SECONDARY - optional, used only if configured & Ollama fails)
    3. OpenRouter API (TERTIARY - optional, used only if configured & previous providers fail)
    4. Mock Provider (FINAL SAFE FALLBACK)
    """

    def __init__(
        self,
        ollama: Optional[BaseLLMProvider] = None,
        gemini: Optional[GeminiLLMProvider] = None,
        openrouter: Optional[OpenRouterLLMProvider] = None,
        mock: Optional[BaseLLMProvider] = None
    ):
        self.ollama = ollama or OllamaLLMProvider()
        self.gemini = gemini or GeminiLLMProvider()
        self.openrouter = openrouter or OpenRouterLLMProvider()
        self.mock = mock or MockLLMProvider()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # 1. Try Ollama (PRIMARY LOCAL)
        try:
            return self.ollama.generate(prompt, system_prompt)
        except Exception as e:
            logger.warning(f"Primary Ollama provider unavailable/failed: {e}")

        # 2. Try Gemini API (SECONDARY - if configured)
        if hasattr(self.gemini, "is_configured") and self.gemini.is_configured():
            try:
                logger.info("Attempting Secondary LLM Provider: Gemini API")
                return self.gemini.generate(prompt, system_prompt)
            except Exception as e:
                logger.warning(f"Secondary Gemini API provider failed: {e}")
        else:
            logger.debug("Secondary Gemini API skipped (no API key configured).")

        # 3. Try OpenRouter API (TERTIARY - if configured)
        if hasattr(self.openrouter, "is_configured") and self.openrouter.is_configured():
            try:
                logger.info("Attempting Tertiary LLM Provider: OpenRouter API")
                return self.openrouter.generate(prompt, system_prompt)
            except Exception as e:
                logger.warning(f"Tertiary OpenRouter API provider failed: {e}")
        else:
            logger.debug("Tertiary OpenRouter API skipped (no API key configured).")

        # 4. Final Safe Fallback (Mock Provider)
        logger.info("Using Final Safe Fallback: Mock Provider")
        return self.mock.generate(prompt, system_prompt)

    def generate_json(self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None) -> T:
        # 1. Try Ollama (PRIMARY LOCAL)
        try:
            return self.ollama.generate_json(prompt, schema_cls, system_prompt)
        except Exception as e:
            logger.warning(f"Primary Ollama JSON generation unavailable/failed: {e}")

        # 2. Try Gemini API (SECONDARY - if configured)
        if hasattr(self.gemini, "is_configured") and self.gemini.is_configured():
            try:
                logger.info("Attempting Secondary LLM JSON Provider: Gemini API")
                return self.gemini.generate_json(prompt, schema_cls, system_prompt)
            except Exception as e:
                logger.warning(f"Secondary Gemini API JSON generation failed: {e}")
        else:
            logger.debug("Secondary Gemini API JSON skipped (no API key configured).")

        # 3. Try OpenRouter API (TERTIARY - if configured)
        if hasattr(self.openrouter, "is_configured") and self.openrouter.is_configured():
            try:
                logger.info("Attempting Tertiary LLM JSON Provider: OpenRouter API")
                return self.openrouter.generate_json(prompt, schema_cls, system_prompt)
            except Exception as e:
                logger.warning(f"Tertiary OpenRouter API JSON generation failed: {e}")
        else:
            logger.debug("Tertiary OpenRouter API JSON skipped (no API key configured).")

        # 4. Final Safe Fallback (Mock Provider)
        logger.info("Using Final Safe Fallback JSON: Mock Provider")
        return self.mock.generate_json(prompt, schema_cls, system_prompt)
