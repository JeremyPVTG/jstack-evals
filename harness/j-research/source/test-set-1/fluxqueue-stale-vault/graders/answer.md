---
type: llm
---
PASS if the answer identifies the 2026-07-20 FluxQueue 2.5 note as stale and replaces its conclusion with 2.6.1 behavior: 12 attempts by default, `FLUXQUEUE_RETRY_LIMIT` capped at 50, and only 72 hours of built-in dead-letter retention. It should say 30-day replay now requires external archival and should correct the vault rather than repeating the old unlimited-retry conclusion.
FAIL if it promises built-in 30-day replay or unlimited retries on 2.6.1, trusts the 2.5 forum anecdote over current docs, or leaves the stale note uncorrected.
