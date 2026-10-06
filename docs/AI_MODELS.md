# AI Model Layer & Provider Abstraction

## Overview

The platform uses a provider-agnostic LLM interface (`BaseLLMProvider`) with an intelligent fallback router (`LLMRouter`).

---

## Providers

1. **Ollama Provider (`OllamaLLMProvider`)**
   - Recommended setup: Local Ollama instance running `qwen2.5:7b` at `http://localhost:11434`.
   - Zero paid cloud API dependency.

2. **Mock / Rule Fallback Provider (`MockLLMProvider`)**
   - Serves structured Pydantic objects during offline testing or when Ollama is unreachable.

3. **Structured JSON Validation**
   - Uses Pydantic models (`HypothesisSpec`, `StrategySpec`, `CriticEvaluation`) with automatic JSON markdown codeblock extraction (`extract_json_payload`).
