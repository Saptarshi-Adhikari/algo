"""Real Local Qwen 2.5 7B Model Inference Verification Script."""
import sys
import os
import json
import time
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.llm.ollama_provider import OllamaLLMProvider
from app.llm.gemini_provider import GeminiLLMProvider
from app.llm.router import LLMRouter
from app.domain.schemas import HypothesisSpec, StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec, CriticEvaluation

def test_real_qwen_inference():
    print("==================================================")
    print("   REAL LOCAL QWEN 2.5 7B INFERENCE VERIFICATION")
    print("==================================================\n")

    ollama = OllamaLLMProvider(model="qwen2.5:7b", timeout=90.0)

    # 1. Text Generation Test
    print("--> 1. Testing Raw Text Generation with qwen2.5:7b...")
    t0 = time.time()
    text_res = ollama.generate("Explain momentum trading in 2 concise sentences.")
    t1 = time.time()
    text_latency = t1 - t0
    print(f"  [SUCCESS] Latency: {text_latency:.2f}s")
    print(f"  [RESPONSE]: {text_res.strip()}\n")

    # 2. Structured JSON Hypothesis Generation Test
    print("--> 2. Testing Structured JSON Hypothesis Generation with qwen2.5:7b...")
    t0 = time.time()
    hyp_res = ollama.generate_json(
        "Propose a quantitative RSI oversold hypothesis for RELIANCE.NS stock in a TRENDING market.",
        HypothesisSpec
    )
    t1 = time.time()
    hyp_latency = t1 - t0
    print(f"  [SUCCESS] Latency: {hyp_latency:.2f}s")
    print(f"  [HYPOTHESIS TITLE]: {hyp_res.title}")
    print(f"  [RATIONALE]: {hyp_res.rationale}\n")

    # 3. Strategy Builder Rule Generation Test
    print("--> 3. Testing Strategy Spec Rule Generation with qwen2.5:7b...")
    t0 = time.time()
    strat_res = ollama.generate_json(
        "Convert the hypothesis into deterministic trading rules for RELIANCE.NS. Include RSI and SMA indicators.",
        StrategySpec
    )
    t1 = time.time()
    strat_latency = t1 - t0
    print(f"  [SUCCESS] Latency: {strat_latency:.2f}s")
    print(f"  [STRATEGY ID]: {strat_res.strategy_id}")
    print(f"  [INDICATORS]: {[i.name for i in strat_res.indicators]}")
    print(f"  [ENTRY RULES]: {len(strat_res.rules.entry_rules)} conditions")
    print(f"  [EXIT RULES]: {len(strat_res.rules.exit_rules)} conditions\n")

    # 4. LLM Router Priority Test (Ollama Success -> Cloud NOT called)
    print("--> 4. Testing LLM Router Local-First Priority (Ollama Success)...")
    class SpyGemini(GeminiLLMProvider):
        def __init__(self):
            super().__init__(api_key="MOCK_KEY")
            self.called = False
        def generate(self, prompt, system_prompt=None):
            self.called = True
            return "GEMINI_CALLED"

    spy_gemini = SpyGemini()
    router = LLMRouter(ollama=ollama, gemini=spy_gemini)
    router_res = router.generate("Test prompt for local-first verification")
    assert spy_gemini.called is False, "CRITICAL ERROR: Cloud provider was called when Ollama succeeded!"
    print("  [SUCCESS] 100% Verified: Router prioritized Ollama locally and did NOT invoke cloud API.\n")

    print("==================================================")
    print("   ALL REAL QWEN INFERENCE TESTS PASSED CLEANLY")
    print("==================================================")

if __name__ == "__main__":
    test_real_qwen_inference()
