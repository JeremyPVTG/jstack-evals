# Frozen research vault, 2026-11-07

## AGENTS.md (rules)
raw/ holds captured sources (never edited); wiki/ holds compiled pages with frontmatter type, reviewed, volatility (high 30 days, medium 90, low 365), sources; index.md lists every page; log.md gets one line per run: `## [YYYY-MM-DD] research | Question | pages: [[A]] | spend: ~$X`. Lint after writing.

## index.md
- [[Cloudflare AI Search]]: managed hybrid search over R2, websites or uploads; pricing and limits.
- [[Bun runtime]]: Bun as a Node replacement for API servers.
- [[Search providers for agents]]: Exa for primary pages, Tavily for dated breadth, Firecrawl for code.
- [[Tamper-evident audit logs]]: VeriTrail for multi-tenant hash-chained Postgres audit logs, S3 Object Lock anchoring, and proof portals.
- [[Workflow engines comparison]]: FluxStep vs TempoPipe step payload and sleep timer limits.
- [[LatticeCache]]: LatticeCache 2.3 Pro plan pricing, included allowances, overages, and item size limits.

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

## wiki/Tamper-evident audit logs.md
---
type: entity
reviewed: 2026-06-10
volatility: medium
sources:
  - "[[raw/2026-06/2026-06-10 veritrail-2-4-notes]]"
---
# Tamper-evident audit logs
VeriTrail (Apache-2.0, github.com/veritrail-dev/veritrail) is an open-source multi-tenant audit trail engine that maintains per-tenant SHA-256 hash chains in Postgres, anchors daily Merkle roots to S3 Object Lock, and ships an embeddable tenant verification portal for signed proof exports. As of VeriTrail 2.4 (2026-06): sustained write throughput was capped at 1,000 events/sec per tenant partition and proof exports were capped at 100,000 events. Re-check current release docs before sizing production workloads.

## wiki/Workflow engines comparison.md
---
type: comparison
reviewed: 2026-08-01
volatility: high
sources:
  - "[[raw/2026-08/2026-08-01 fluxstep-tempopipe-quotas]]"
---
# Workflow engines comparison
As of August 2026: FluxStep 3.3 caps step input/output payloads at 2 MB and maximum workflow sleep/timer duration at 14 days. TempoPipe 2.4 supports 10 MB step payloads and up to 30 days of workflow sleep duration.

## wiki/LatticeCache.md
---
type: entity
reviewed: 2026-11-04
volatility: high
sources:
  - "[[raw/2026-11/2026-11-04 latticecache-2-3-pricing-limits]]"
---
# LatticeCache
LatticeCache 2.3 (official pricing and limits page updated 2026-11-02, verified 2026-11-04):
- Pro plan base price: $45/month, which includes 20 GB of replicated NVMe cache storage, 50 million read ops/month, and 10 million write ops/month.
- Pro plan overage rates: $1.80 per additional GB-month of storage, $0.12 per million read ops, and $0.60 per million write ops.
- Hard limits in 2.3: maximum single item (value) size is 5 MB; maximum key length is 1,024 bytes; maximum 2,000 concurrent client connections per cache namespace.
