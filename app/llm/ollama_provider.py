"""Local Ollama LLM Provider implementation."""
import httpx
from typing import Optional
from app.llm.base import BaseLLMProvider
from app.config.settings import settings
from app.config.logging import logger

class OllamaLLMProvider(BaseLLMProvider):
    """Local Ollama provider communicating with local Ollama instance."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = None
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2}
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.warning(f"Ollama request to {url} ({self.model}) failed: {e}")
            raise RuntimeError(f"Ollama provider error: {e}")
