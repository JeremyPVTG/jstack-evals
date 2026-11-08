---
type: llm
focus: trace
---
PASS if the agent recommends not adding Redis now (or deferring it), or names a cheaper option, with a reason tied to the existing cache or the load. FAIL if it recommends building the Redis layer now.
