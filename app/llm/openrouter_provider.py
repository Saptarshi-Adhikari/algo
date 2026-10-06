"""OpenRouter API LLM Provider implementation using lightweight HTTP client with secret protection."""
import httpx
from typing import Optional
from app.llm.base import BaseLLMProvider
from app.llm.gemini_provider import sanitize_secret_error
from app.config.settings import settings
from app.config.logging import logger

class OpenRouterLLMProvider(BaseLLMProvider):
    """Provider for OpenRouter free/low-cost API with credential masking."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        self.api_key = api_key if api_key is not None else settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL or "google/gemini-2.5-flash"
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

    def is_configured(self) -> bool:
        """Check if OpenRouter API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.is_configured():
            raise ValueError("OpenRouter API key is not configured.")

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/quant-ai",
            "X-Title": "QuantAI",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                choices = data.get("choices", [])
                if not choices:
                    raise RuntimeError("OpenRouter API returned no choices.")

                return choices[0].get("message", {}).get("content", "")

        except Exception as e:
            raw_err = str(e)
            clean_err = sanitize_secret_error(raw_err, self.api_key)
            logger.warning(f"OpenRouter API request failed for model '{self.model}': {clean_err}")
            raise RuntimeError(f"OpenRouter provider error: {clean_err}")
