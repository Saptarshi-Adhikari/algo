# Bounded AI Experiment Loop & Memory Engine

## Workflow Overview

The automated AI research loop runs autonomously up to a bounded maximum (default: 10 iterations per run):

```
READ MEMORY
   │
   ▼
CLASSIFY MARKET REGIME (Trending / Ranging / High Vol / Low Vol)
   │
   ▼
PROPOSE ONE HYPOTHESIS (Researcher Agent)
   │
   ▼
BUILD DETERMINISTIC STRATEGY (Strategy Builder Agent)
   │
   ▼
DETERMINISTIC BACKTEST (Dev & Validation Data Splits)
   │
   ▼
CRITIQUE EVIDENCE (Critic Agent -> REJECT / RETEST / KEEP_FOR_PAPER_TESTING)
   │
   ▼
PERSIST EXPERIMENT & LESSONS (SQLite Memory Repository)
   │
   ▼
DECIDE NEXT STEP (Next-Experiment Agent -> New Hyp / Retest / Rollback)
   │
   ▼
REPEAT UNTIL BOUNDED MAX
```

---

## Memory Retrieval & Querying (`app/memory/repository.py`)
- Query experiments by verdict (`get_experiments_by_verdict`).
- Query by regime (`get_experiments_by_regime`).
- Retrieve strategy version lineage trees (`get_strategy_lineage`).
- Compute aggregate summary statistics without dumping entire database into LLM context.
