# Frozen web snapshot, 2026-11-07. Every page that exists in this world is listed here.

## https://nodejs.org/en/about/previous-releases (official, updated 2026-10-28)
Node.js 24 "Krypton" is the Active LTS line; latest v24.11.0 released 2026-10-28. Node.js 22 is Maintenance LTS. Node.js 25 is Current.

## https://developers.cloudflare.com/ai-search/platform/limits-pricing/ (official, updated 2026-11-02)
AI Search billing begins December 1, 2026. Included monthly: 5M ingestion tokens, 10 GB-month storage, 1,000 semantic and 1,000 full-text queries. Hybrid queries $0.75 per 1,000 beyond that; full-text $0.10 per 1,000.

## https://bun.com/blog/bun-v1.4 (official, 2026-10-02)
Bun 1.4: node:cluster now supported; worker_threads complete; 99.1% of Node's test suite passes; new built-in Postgres pool. Breaking: Bun.serve() default idle timeout changed from 10s to 30s.

## https://github.com/oven-sh/bun/issues/31877 (GitHub issue, opened 2026-10-20, open)
"Memory grows under sustained HTTP keep-alive load in 1.4.0" — 42 thumbs up; maintainers reproduced, fix targeted for 1.4.2.

## https://www.reddit.com/r/node/comments/bun14 (forum, 2026-10-12)
User reports moving an Express API to Bun 1.4 cut p95 latency 30%, but one hit the keep-alive memory issue.

## https://orm.drizzle.team/docs/upgrade-v1 (official, 2026-09-15)
Drizzle ORM v1.0 released 2026-09-15. Breaking changes: relational queries v2 is the default; `drizzle-kit push` renamed `drizzle-kit sync`; PostgreSQL driver must be node-postgres 9+ or postgres.js 4+. Migration guide included.

## https://github.com/drizzle-team/drizzle-orm/issues/5120 (GitHub issue, opened 2026-10-03, open)
"v1: migrations generated for enum changes drop and recreate the column" — data loss risk on enum edits; 61 comments; workaround: hand-edit the migration.

## https://github.com/drizzle-team/drizzle-orm/issues/5188 (GitHub issue, opened 2026-10-21, closed in 1.0.3)
"v1: relational queries v2 returns wrong nesting with self-relations" — fixed in 1.0.3 (2026-10-29).

## https://blog.example-dev.io/drizzle-v1-in-production (blog, 2026-10-18)
"We ran Drizzle v1 in production for a month: solid, but review every generated migration."

## https://valkey.io/topics/search/ (official, updated 2026-10-01)
Valkey 9 search module (valkey-search 1.2): vector similarity (HNSW and FLAT), numeric and tag filters, hybrid queries; full-text search is not yet supported (planned).

## https://github.com/louislam/uptime-kuma (GitHub repo)
Uptime Kuma: self-hosted monitoring, MIT licence, about 72k stars, latest release 2.2.0 on 2026-10-14; HTTP, TCP, ping, DNS checks; status pages; 90+ notification channels; Docker one-liner.

## https://github.com/TwiN/gatus (GitHub repo)
Gatus: config-as-code health dashboard, Apache-2.0, about 8k stars, release 5.21 on 2026-09-30; alerts to Slack, PagerDuty, email.

## https://betterstack.com/pricing (official, 2026-11)
Better Stack Uptime: free tier with 10 monitors at 3-minute checks; paid from $29/month.

## https://developers.cloudflare.com/health-checks/ (official)
Cloudflare Health Checks: available on Pro plans and above; checks origins and alerts by email or webhook.

## https://tailwindcss.com/blog/tailwindcss-v5 (official, 2026-08-20)
Tailwind CSS v5: CSS-first config by default, JS config removed; new container query defaults; Lightning CSS engine; upgrade tool `npx @tailwindcss/upgrade@5`.

## https://www.postgresql.org/docs/18/runtime-config-resource.html (official, Postgres 18.1, 2026-11-13 docs)
io_method: worker (default), io_uring (Linux only), or sync. io_workers default 3. effective_io_concurrency default raised to 16.

## https://pganalyze.com/blog/postgres-18-async-io (blog, 2026-09-30)
Benchmarks: sequential scans on cloud disks up to 2-3x faster with io_method=io_uring versus sync; little gain on local NVMe; worker mode gets most of the benefit without io_uring.

## https://docs.veritrail.dev/v2.6/architecture-and-limits (official, VeriTrail 2.6.0, updated 2026-10-30)
VeriTrail 2.6.0 (Apache-2.0): turnkey multi-tenant tamper-evident audit log service over Postgres 15+. Maintains per-tenant SHA-256 hash-chained event streams, anchors daily Merkle roots to S3 Object Lock (WORM), and includes a prebuilt embeddable verification portal (React component or hosted iframe) where tenant admins export offline-verifiable Ed25519 proof bundles. Operational limits in 2.6.0: sustained write throughput is capped at 2,500 events/sec per tenant partition (due to per-tenant serial hash-chain locking); proof bundle exports are capped at 500,000 events per export job; S3 Object Lock anchoring requires an S3 bucket with Versioning enabled in Governance or Compliance mode.

## https://docs.veritrail.dev/v1.9/architecture-and-limits (official, VeriTrail 1.9, updated 2025-11-12)
VeriTrail 1.9 Architecture & Limits: supports single-tenant deployments only (multi-tenant isolation requires separate Postgres databases per customer). Write throughput is capped at 400 events/sec. S3 Object Lock anchoring and self-serve proof portals are not built in; export verification requires the CLI tool `veritrail-verify`.

## https://github.com/veritrail-dev/veritrail (GitHub repo)
VeriTrail: tamper-evident multi-tenant audit log engine with Postgres hash chains, S3 Object Lock Merkle anchoring, and embeddable tenant verification portal. Apache-2.0 licence, about 19k stars, latest release v2.6.0 on 2026-10-30.

## https://kestreldb.io/blog/kestreldb-4-3-launch (blog, 2026-10-14)
"KestrelDB 4.3 Launch: Introducing Zero-Downtime Online Shard Splitting — rebalance hot tables in place under peak production traffic with zero write pauses and seamless ACID transactions across shards."

## https://www.reddit.com/r/databasedevs/comments/kestrel43split (forum, 2026-10-22)
User post: "We ran ONLINE SPLIT SHARD on a 200 GB table in KestrelDB 4.3 during business hours and didn't notice a single dropped write—it's completely lock-free now."

## https://docs.kestreldb.io/v4.3/operations/online-shard-split (official, KestrelDB 4.3.1, updated 2026-10-29)
ONLINE SPLIT SHARD in KestrelDB 4.3 (4.3.0 / 4.3.1): Background backfill copies historical ranges without blocking reads or writes, but the final cutover phase acquires an exclusive write lock (METADATA_CUTOVER_LOCK) on the splitting shard for 4 to 12 seconds while routing tables update. Operational constraints in 4.3: (1) single-shard writes arriving during cutover queue up to `shard_cutover_queue_ms` (default 5,000 ms) and fail with SQLSTATE 55P04 (`cutover_lock_timeout`) if cutover exceeds that window; (2) any in-flight multi-shard (two-phase commit / 2PC) transaction touching the splitting shard during cutover is immediately aborted with SQLSTATE 40001 (`serialization_failure`); (3) tables with foreign keys referencing another shard cannot use ONLINE SPLIT SHARD and require an offline maintenance window.

## https://docs.kestreldb.io/v4.4-preview/operations/online-shard-split (official preview docs, KestrelDB 4.4.0-alpha, updated 2026-11-05)
KestrelDB 4.4.0-alpha Preview (unreleased, not for production): introduces experimental dual-write cutover (`enable_lockless_cutover = on`) to eliminate METADATA_CUTOVER_LOCK and preserve in-flight 2PC transactions. Not available in the 4.3 release line.

## https://github.com/kestreldb/kestrel/issues/8912 (GitHub issue, opened 2026-10-26, open)
"4.3.0/4.3.1: ONLINE SPLIT SHARD cutover lock stretches to 35+ seconds when concurrent analytical reads hold snapshot pins on the source shard" — 38 thumbs up; reproduced by maintainers, fix targeted for 4.3.2.

## https://docs.fluxstep.dev/v3.3/platform/quotas (official, FluxStep 3.3, updated 2026-07-19)
FluxStep 3.3 Service Quotas: Maximum step input/output payload size is 2 MB (hard limit). Maximum workflow sleep/wait timer duration is 14 days. Maximum steps per workflow execution is 500.

## https://docs.fluxstep.dev/changelog/fluxstep-v3-4 (official, 2026-10-31)
FluxStep v3.4 Release Notes (released 2026-10-31): Raised maximum step input/output payload size from 2 MB to 16 MB across all plans, and increased maximum workflow sleep/wait timer duration from 14 days to 90 days. Added native dead-letter batch replay API.

## https://docs.fluxstep.dev/v3.4/platform/quotas (official, FluxStep 3.4, updated 2026-10-31)
FluxStep 3.4 Service Quotas: Maximum step input/output payload size is 16 MB. Maximum workflow sleep/wait timer duration is 90 days. Per-step execution timeout is 30 minutes.

## https://docs.tempopipe.io/v2.5/reference/limits (official, TempoPipe 2.5, updated 2026-10-25)
TempoPipe 2.5 Platform Limits: Maximum step input/output payload size is 10 MB. Maximum workflow sleep or human-approval wait duration is hard-capped at 30 days (workflows still paused at 30 days are terminated with `WORKFLOW_TTL_EXCEEDED`). Maximum concurrent workflows per namespace is 25,000.

## https://latticecache.dev/pricing-and-limits (official, LatticeCache 2.3, updated 2026-11-02)
LatticeCache 2.3 Pricing & Limits: Pro plan is $45/month base, including 20 GB replicated NVMe storage, 50M read ops/month, and 10M write ops/month. Overages: $1.80/GB-month storage, $0.12 per million read ops, $0.60 per million write ops. Max item size: 5 MB; max key length: 1,024 bytes; max connections: 2,000 per namespace.

## https://docs.aegisvault.io/v1.9/security/compliance (official, AegisVault KMS 1.9, updated 2026-10-30)
AegisVault KMS 1.9 Compliance & Certifications: SOC 2 Type II and ISO 27001:2022 certified. HIPAA: A signed Business Associate Agreement (BAA) is available on the Enterprise plan ($800/month platform minimum) for deployments in US-East or US-West regions with customer-managed audit logging enabled; standard commercial HSM-backed master keys cost $2.50 per key/month. FedRAMP: AegisVault KMS 1.9 is listed as "In Process" on the FedRAMP Marketplace at the FedRAMP Moderate impact level (sponsored by HHS). AegisVault has not announced a timeline, authorization status, or pricing schedule for FedRAMP High.

## https://news.ycombinator.com/item?id=49102844 (forum, 2026-11-01)
Comment by anon_govcloud: "Heard from a channel partner rep that AegisVault KMS 1.9 quietly received its FedRAMP High ATO last week and prices federal HSM keys at $9/key/month."

## https://quasarrpc.org/docs/v3.5/transport-defaults (official, QuasarRPC 3.5.0, updated 2026-11-03)
QuasarRPC 3.5.0 Transport Defaults: `max_frame_size` defaults to 16 MiB (16,777,216 bytes, raised from 4 MiB in 3.4); `keepalive_ping_interval` defaults to 45s with a 15s `keepalive_ping_timeout`; `max_concurrent_streams` per connection defaults to 256.
