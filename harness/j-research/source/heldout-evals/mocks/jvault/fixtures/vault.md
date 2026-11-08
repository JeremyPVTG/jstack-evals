# Frozen research vault, 2026-11-07

## AGENTS.md (rules)
raw/ holds captured sources (never edited); wiki/ holds compiled pages with frontmatter type, reviewed, volatility (high 30 days, medium 90, low 365), sources; index.md lists every page; log.md gets one line per run: `## [YYYY-MM-DD] research | Question | pages: [[A]] | spend: ~$X`. Lint after writing.

## index.md
- [[Cloudflare AI Search]]: managed hybrid search over R2, websites or uploads; pricing and limits.
- [[Bun runtime]]: Bun as a Node replacement for API servers.
- [[Search providers for agents]]: Exa for primary pages, Tavily for dated breadth, Firecrawl for code.

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
