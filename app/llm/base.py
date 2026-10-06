"""Base Provider-Agnostic LLM Interface."""
from abc import ABC, abstractmethod
from typing import TypeVar, Type, Optional
import json
import re
from pydantic import BaseModel
from app.config.logging import logger

T = TypeVar("T", bound=BaseModel)

def extract_json_payload(text: str) -> str:
    """Robust extraction of JSON payload from raw LLM text outputs containing markdown codeblocks."""
    cleaned = text.strip()
    # Match markdown json block if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Try finding first '{' and last '}'
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return cleaned[start_idx:end_idx+1]

    return cleaned

class BaseLLMProvider(ABC):
    """Abstract LLM Provider interface."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate raw text completion."""
        pass

    def generate_json(self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None) -> T:
        """Generate and parse structured JSON conforming to a Pydantic schema."""
        json_instruction = (
            f"\n\nIMPORTANT: Respond strictly with a single valid JSON object matching this JSON schema:\n"
            f"{json.dumps(schema_cls.model_json_schema(), indent=2)}\n"
            f"Do not include any conversational preamble or markdown outer formatting outside the JSON codeblock."
        )
        full_prompt = prompt + json_instruction
        raw_response = self.generate(full_prompt, system_prompt=system_prompt)
        json_str = extract_json_payload(raw_response)

        try:
            parsed_dict = json.loads(json_str)
            return schema_cls.model_validate(parsed_dict)
        except Exception as e:
            logger.error(f"Failed to parse LLM JSON output into {schema_cls.__name__}: {e}. Raw response was: {raw_response[:200]}...")
            raise ValueError(f"LLM JSON parsing error: {e}")
