---
type: llm
---
PASS if the answer:
1. Recommends FluxStep (v3.4, released 2026-10-31) over TempoPipe (v2.5) for this pipeline.
2. Cites the FluxStep 3.4 limit increase raising max step payload from 2 MB to 16 MB and max workflow sleep/wait duration from 14 days to 90 days (satisfying both the 8 MB payload and 45-day wait).
3. Explains that TempoPipe 2.5 supports 10 MB step payloads but hard-caps workflow sleep/wait duration at 30 days (`WORKFLOW_TTL_EXCEEDED`), which cannot handle a 45-day compliance wait.

FAIL if it relies on the stale vault note or FluxStep 3.3 decoy docs (claiming FluxStep is still capped at 2 MB payloads or 14-day sleeps), or if it recommends TempoPipe for a 45-day pause.
