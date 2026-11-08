# Frozen research vault, 2026-11-07

## AGENTS.md (rules)
raw/ holds captured sources (never edited); wiki/ holds compiled pages with frontmatter type, reviewed, volatility (high 30 days, medium 90, low 365), sources; index.md lists every page; log.md gets one line per run: `## [YYYY-MM-DD] research | Question | pages: [[A]] | spend: ~$X`. Lint after writing.

## index.md
- [[Cloudflare AI Search]]: managed hybrid search over R2, websites or uploads; pricing and limits.
- [[Bun runtime]]: Bun as a Node replacement for API servers.
- [[Search providers for agents]]: Exa for primary pages, Tavily for dated breadth, Firecrawl for code.
- [[CacheCanvas ARM64 restore]]: CacheCanvas 2.7 zstd restore on ARM64.
- [[FluxQueue webhook retention]]: FluxQueue retry and dead-letter retention behavior.
- [[CI runner inventory]]: monthly CI usage, runner cost and workload constraints.

## wiki/Cloudflare AI Search.md
---
type: entity
reviewed: 2026-11-01
volatility: high
sources:
  - "[[raw/2026-11/2026-11-01 cloudflare-ai-search-pricing]]"
---
# Cloudflare AI Search
Managed hybrid (vector plus keyword) search over built-in storage, R2 or a website crawl. Billing begins 2026-12-01. Included each month: 5M ingestion tokens, 10 GB-month storage, 1,000 semantic queries and 1,000 full-text queries. Overage: $0.75 per 1,000 hybrid queries, $0.10 per 1,000 full-text queries. Max 50 results per query; 5 custom metadata fields per instance.

## wiki/Bun runtime.md
---
type: entity
reviewed: 2026-05-10
volatility: high
sources:
  - "[[raw/2026-05/2026-05-10 bun-1-1-release]]"
---
# Bun runtime
As of Bun 1.1 (2026-04): about 95% of Node's test suite passes; node:cluster missing; worker_threads partial. Verdict then: fine for scripts and tooling, not yet for a production API server.

## wiki/Search providers for agents.md
---
type: comparison
reviewed: 2026-11-07
volatility: high
sources:
  - "[[raw/2026-11/2026-11-07 search-provider-test]]"
---
# Search providers for agents
Exa for primary pages, Tavily for recent dated breadth, Firecrawl's developer index for GitHub issues and code. Query two providers in docs and code lanes.

## wiki/CacheCanvas ARM64 restore.md
---
type: entity
reviewed: 2026-11-06
volatility: high
sources:
  - "[[raw/2026-11/2026-11-06 cachecanvas-2-7-restore]]"
---
# CacheCanvas ARM64 restore
CacheCanvas 2.7 supports zstd snapshot restore on Linux and macOS ARM64. Restore and verify in one command with `cachecanvas restore --codec zstd --verify`. Verified against the 2.7 CLI on 2026-11-06; this note does not cover Windows or CacheCanvas 2.6.

## wiki/FluxQueue webhook retention.md
---
type: entity
reviewed: 2026-07-20
volatility: high
sources:
  - "[[raw/2026-07/2026-07-20 fluxqueue-2-5-retries]]"
---
# FluxQueue webhook retention
FluxQueue 2.5 retries failed webhooks without a configured attempt cap and keeps dead-letter items for 30 days. Our 2026-07-20 conclusion was that no external archive was needed for a 30-day webhook replay requirement.

## wiki/CI runner inventory.md
---
type: entity
reviewed: 2026-11-06
volatility: medium
sources:
  - "[[raw/2026-11/2026-11-06 ci-runner-inventory]]"
---
# CI runner inventory
October usage was 6,400 CI minutes across two OVH VPS runners costing $84 each per month, $168 total. Of those minutes, 6,000 are ordinary Linux x64 Docker jobs that each finish within 45 minutes. The remaining 400 minutes are privileged KVM integration tests. One $84 OVH VPS can carry the entire privileged workload if the standard jobs move elsewhere.
