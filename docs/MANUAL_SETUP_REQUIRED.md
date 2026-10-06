# Manual Setup Checklist

This document details all manual configuration steps required by the user to complete full system integration.

---

## 1. Start Local Ollama Service & Pull Recommended Model

The platform uses **Ollama** locally as its primary LLM provider.

### Hardware Assessment
- **RAM**: 23.71 GB (Sufficient for 7B models)
- **CPU**: 16 Cores
- **Disk Free**: ~120 GB
- **Recommended Model**: `qwen2.5:7b` (Optimal balance of quantitative reasoning, latency, and Pydantic JSON schema adherence).

### Step-by-Step Instructions

1. **Start Ollama Service** (if not running):
   - On Windows: Open the **Ollama** application from your Start Menu or run:
     ```powershell
     ollama serve
     ```

2. **Pull the Qwen 2.5 7B Model**:
   Execute the following command in PowerShell / Terminal:
   ```powershell
   ollama pull qwen2.5:7b
   ```

3. **Verification Command**:
   ```powershell
   ollama list
   ```
   **Expected Output**:
   ```
   NAME            ID           SIZE      MODIFIED
   qwen2.5:7b      47517e057a9e 4.7 GB    ...
   ```

---

## 2. Configure Local `.env` File (Optional Cloud Fallbacks)

1. Open `.env` in your project root directory.
2. If you wish to enable **Gemini API** as a secondary fallback, insert your newly rotated Gemini key:
   ```env
   GEMINI_API_KEY=your_newly_rotated_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```
3. If you wish to enable **OpenRouter** as a tertiary fallback, insert your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=google/gemini-2.5-flash
   ```

> ⚠️ **CRITICAL SECURITY NOTE**: Never paste API keys into source code, documentation, test files, or Git commits. `.env` is ignored by `.gitignore`.

---

## 3. Verification Command

After starting Ollama and pulling the model, run the full verification suite:
```powershell
pytest -v
python scripts/verify_phase2.py
```
