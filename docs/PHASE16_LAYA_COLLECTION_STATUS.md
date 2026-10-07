# Phase 16 — Laya Collection Status Policy

## Collection Status Architecture
Collection Status answers:
> "Is the shadow system successfully collecting and resolving fresh predictions?"

## Allowed Status Values
- `NOT_STARTED`: Collection has not been initialized.
- `WAITING_FOR_DATA`: Insufficient fresh market data to collect predictions.
- `COLLECTING`: Fresh predictions are actively being collected.
- `PAUSED`: Collection is intentionally paused while preserving accumulated evidence.
- `COLLECTION_ERROR`: Technical collector failure prevents new prediction gathering.
- `COLLECTION_COMPLETE_FOR_WINDOW`: The configured collection window is complete.

## State Transitions
Transitions are explicit. Pausing collection does NOT erase or downgrade Evidence Status.
