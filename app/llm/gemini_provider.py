"""Gemini API LLM Provider implementation using lightweight HTTP client with strict secret protection."""
import httpx
import re
from typing import Optional
from app.llm.base import BaseLLMProvider
from app.config.settings import settings
from app.config.logging import logger

API_KEY_REGEX = re.compile(r"AIza[0-9A-Za-z_-]{35}")

def sanitize_secret_error(error_msg: str, secret: Optional[str] = None) -> str:
    """Mask any secret API key or Google API key pattern from error strings or logs."""
    cleaned = error_msg
    if secret and secret.strip():
        cleaned = cleaned.replace(secret.strip(), "[REDACTED_API_KEY]")
    cleaned = API_KEY_REGEX.sub("[REDACTED_API_KEY]", cleaned)
    return cleaned

class GeminiLLMProvider(BaseLLMProvider):
    """Provider for Google Gemini API via REST with automatic error handling and credential masking."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

    def is_configured(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.is_configured():
            raise ValueError("Gemini API key is not configured.")

        # Using header authentication so API key never appears in the URL or status error tracebacks
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Directive: {system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})
        payload = {"contents": contents}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                candidates = data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("Gemini API returned no response candidates.")

                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    raise RuntimeError("Gemini API candidate contained no text parts.")

                return parts[0].get("text", "")

        except Exception as e:
            raw_err = str(e)
            clean_err = sanitize_secret_error(raw_err, self.api_key)
            logger.warning(f"Gemini API request failed for model '{self.model}': {clean_err}")
            raise RuntimeError(f"Gemini provider error: {clean_err}")
