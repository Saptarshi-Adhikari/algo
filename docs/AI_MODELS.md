# AI Model Layer & Provider Abstraction

## Overview

The platform uses a provider-agnostic LLM interface (`BaseLLMProvider`) managed by a resilient 4-tier Local-First Router (`LLMRouter`).

---

## Provider Priority Chain

```
LLM ROUTER
    │
    ├─► 1. Ollama (PRIMARY LOCAL) — default model: qwen2.5:7b
    │
    ├─► 2. Gemini API (SECONDARY OPTIONAL) — model: gemini-1.5-flash
    │      (Triggered only if GEMINI_API_KEY is configured in .env and Ollama fails)
    │
    ├─► 3. OpenRouter API (TERTIARY OPTIONAL) — model: google/gemini-2.5-flash
    │      (Triggered only if OPENROUTER_API_KEY is configured in .env and previous providers fail)
    │
    └─► 4. Mock Provider (FINAL SAFE FALLBACK) — offline deterministic schema generator
```

---

## Security & Credential Protection
- API keys are retrieved dynamically from `settings.GEMINI_API_KEY` and `settings.OPENROUTER_API_KEY`.
- All error logging uses `sanitize_secret_error` to strip and mask raw API keys (`[REDACTED_API_KEY]`).
- Cloud APIs are never called if Ollama succeeds or if API keys are unconfigured.

---

## Structured JSON Parsing
- All agents request structured JSON via Pydantic model contracts (`HypothesisSpec`, `StrategySpec`, `CriticEvaluation`).
- Markdown codeblock extraction (`extract_json_payload`) parses outputs cleanly across all providers.
