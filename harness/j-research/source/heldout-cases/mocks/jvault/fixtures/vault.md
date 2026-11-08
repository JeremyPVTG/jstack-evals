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

## wiki/HarborRelay delivery.md
---
type: entity
reviewed: 2026-09-30
volatility: high
sources:
  - "[[raw/2026-09/2026-09-30 harborrelay-preview]]"
---
# HarborRelay delivery
We evaluated the HarborRelay 4.0 preview for invoice events between Frankfurt and Montreal. The preview's global receipts persisted seven days across regions. Tentative recommendation at the time: enrolled preview workspaces could omit their consumer duplicate-event guard during that receipt window. This note has not been reviewed for GA 4.2.

## raw/2026-09/2026-09-30 harborrelay-preview
Source: https://docs.harborrelay.example/archive/4.0/global-receipts
Captured: 2026-09-30
HarborRelay 4.0 global-receipt preview, official page dated 2026-08-20. Enrolled preview workspaces share receipts across regions for seven days. Preview only; not a GA contract.

## wiki/Small-team purchase approvals.md
---
type: comparison
reviewed: 2026-10-23
volatility: medium
sources:
  - "[[raw/2026-10/2026-10-23 latchdesk-6-1]]"
---
# Small-team purchase approvals
For a self-hosted internal purchase-approval app with eight staff, two sequential approvers, an audit history and CSV export before manual payment, adopt LatchDesk Community 6.1 rather than implement a workflow engine. LatchDesk has shipped this application since 2021. Version 6.1 runs as a container with persistent local storage, includes forms, two sequential approvers, append-only approval history, and CSV export. Limits: 12 members, 500 open requests, sequential approval only, no parallel or conditional branches. It executes no payments and provides neither native SSO nor bank integration. These limits fit a small team that pays manually and does not require SSO. Start by deploying the container and validating one request through both approvals and its CSV export. No bespoke application code is needed for this workflow. This review contains all the documented capabilities and limits needed for that decision.

## raw/2026-10/2026-10-23 latchdesk-6-1
Source: https://docs.latchdesk.example/community/6.1/approvals
Captured: 2026-10-23
Official LatchDesk Community 6.1 documentation, updated 2026-10-21: self-hosted container; forms, two sequential approvers, append-only approval history, CSV export; 12 members; 500 open requests; no parallel/conditional branches, payment execution, native SSO, or bank integrations. LatchDesk has shipped the application since 2021. No plugins or custom code are required for supported workflows.

## wiki/RivetDB recovery.md
---
type: entity
reviewed: 2026-07-31
volatility: medium
sources:
  - "[[raw/2026-07/2026-07-31 rivetdb-7-0]]"
---
# RivetDB recovery
RivetDB 7.0 supported synchronous cross-region replicas. Our single planned switchover in a 7.0 test took 12 seconds with both regions healthy. We tentatively expected zero acknowledged-write loss when using that synchronous mode. This note is about 7.0, not later releases; the one test was not a p99 measurement.

## raw/2026-07/2026-07-31 rivetdb-7-0
Source: https://docs.rivetdb.example/7.0/replication
Captured: 2026-07-31
RivetDB 7.0 documentation: optional synchronous cross-region mode. Internal annotation: one healthy-region planned switchover took 12 seconds. No percentile or whole-region-loss test was recorded.
