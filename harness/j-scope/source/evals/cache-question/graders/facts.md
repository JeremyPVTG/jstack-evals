---
type: llm
focus: trace
---
The workspace shows an in-memory LRU cache already in front of the database (src/cache.ts) and the load (docs/metrics.md: peak 12 requests per second, p95 48 ms, one instance). FAIL if any question asks the user whether there is already a cache, what the traffic or latency is, or how many instances run. PASS otherwise.
