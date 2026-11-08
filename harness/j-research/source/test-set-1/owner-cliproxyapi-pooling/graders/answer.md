---
type: llm
---
PASS if the answer distinguishes a unified gateway from pooled quota: CLIProxyAPI 7.4 can expose one endpoint/key, route and fail over among Claude subscription, Codex and OpenRouter accounts, and provide a unified local usage report. It must also say provider quotas and balances remain independent, with no cross-provider usage transfer or conversion into OpenRouter credit, and reject the forum's "one giant quota" claim.
FAIL if it says subscription allowances or OpenRouter credits become one balance, promises unlimited usage, or misses that routing/failover is the supported capability.
