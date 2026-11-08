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

## https://docs.harborrelay.example/4.2/delivery-guarantees (official, HarborRelay 4.2, updated 2026-11-04)
HarborRelay 4.2 delivery guarantees: cross-region forwarding, including Frankfurt to Montreal, is at least once. Duplicate deliveries are possible after regional failover. The 24-hour event-ID deduplication window operates inside one region only; it does not survive a region boundary. Consumers handling forwarded events must remain idempotent. The archived global-receipt preview is not a 4.2 feature.

## https://harborrelay.example/changelog/4.2 (official changelog, 2026-11-04)
HarborRelay 4.2 is generally available. The global-receipt preview was retired; active preview deployments were migrated to regional deduplication. Cross-region forwarding uses at-least-once delivery. Current delivery-guarantees documentation supersedes the 4.0 preview archive.

## https://docs.harborrelay.example/archive/4.0/global-receipts (official archived documentation, HarborRelay 4.0 preview, 2026-08-20)
HarborRelay 4.0 global-receipt preview: enrolled preview workspaces share event receipts across regions for seven days, providing exactly-once delivery within that receipt window. Status: preview, not a GA contract. This page is an archived 4.0 document and does not describe 4.2.

## https://dispatchstack.example/blog/harborrelay-42-launch (vendor marketing blog, 2026-11-06)
HarborRelay 4.2 brings exactly-once delivery worldwide: invoice events arrive once whether routed from Frankfurt to Montreal or anywhere else. Delete those duplicate-event guards! Our source is HarborRelay's global-receipts documentation at https://docs.harborrelay.example/archive/4.0/global-receipts. DispatchStack sells HarborRelay deployment services. This launch article does not discuss the retired preview.

## https://docs.quillstore.example/2.7/deletion-and-restore (official, Quillstore 2.7, updated 2026-11-03)
Quillstore 2.7 compact-on-delete immediately removes the collection from the query index. The supported restore path is a customer-retained snapshot. Restore replays data only through the last successful snapshot; writes after that snapshot are excluded. This page specifies no post-delete support recovery window, no hidden retention period, and no support recovery SLA.

## https://quillstore.example/changelog/2.7 (official changelog, 2026-11-01)
Quillstore 2.7 introduces compact-on-delete and faster index reclamation. Operators should validate their retained snapshot restore procedure before enabling the option. No additional recovery or retention guarantee is announced in this release.

## https://community.quillstore.example/t/72-hour-undelete/914 (community forum, 2026-11-05)
User maple_packet: "On 2.7 I deleted a collection with compact-on-delete, and support got it back two days later. They must keep hidden copies for 72 hours; you probably don't need snapshots anymore." No support employee or maintainer replied. The post contains no support transcript, recovery method, or policy link. This is the only source in this snapshot claiming a 72-hour hidden recovery window.

## https://docs.latchdesk.example/community/6.1/approvals (official, LatchDesk Community 6.1, updated 2026-10-21)
LatchDesk has shipped a self-hosted purchase-approval application since 2021. Community 6.1 ships as a container with persistent local storage. It includes purchase request forms, two sequential approvers, append-only approval history, and CSV export for manual payment workflows. Community limits: 12 members and 500 open requests. Only sequential approval is supported; no parallel or conditional branches. No payment execution, native SSO, or bank integrations. Existing requirements within these boundaries do not require plugins or custom application code.

## https://workflowcraft.example/blog/build-purchase-approvals-in-a-weekend (consultancy blog, 2026-11-02)
Build purchase approvals in a weekend: use a form UI, a custom workflow state machine, an audit table, and a CSV worker. We sell a starter kit. The article does not compare existing approval products or document LatchDesk Community 6.1.

## https://docs.sparrowhook.example/4.8/workspace-limits (official, SparrowHook 4.8, updated 2026-11-05)
SparrowHook 4.8 workspace limits: maximum 37 active webhook endpoints per workspace on all plans. Archived endpoints do not count toward the active limit; up to 200 archived endpoint records may be retained per workspace. This is a workspace-wide limit, not a per-project or per-API-key limit.

## https://docs.rivetdb.example/7.3/replication (official, RivetDB 7.3, updated 2026-11-02)
RivetDB 7.3 acknowledgement requires a quorum of two out of three replicas within the primary region. Cross-region replicas apply the log asynchronously; remote_apply_lag_ms reports observed lag and is not a maximum-lag bound or contractual RPO. The synchronous cross-region mode documented for 7.0 was removed in 7.3. This release makes no documented zero-loss guarantee for loss of the entire primary region and publishes no contractual region-loss recovery-time guarantee.

## https://engineering.rivetdb.example/7.3/planned-switchover-notes (official engineering report, 2026-11-04)
RivetDB 7.3 lab exercise: six planned switchovers between healthy regions completed in 8-14 seconds. Both regions remained online throughout. We did not test complete primary-region loss. These six samples are not a p99 measurement and do not establish a recovery-time SLA. We have not published a 7.3 region-loss latency distribution in this snapshot.

## https://launchledger.example/rivetdb-73-instant-recovery (reseller blog, 2026-11-06)
RivetDB 7.3: "instant recovery for your ledger." The official lab's 8-14 second switchovers mean everyone should be back in under 20 seconds. This article provides no region-loss experiment, percentile calculation, or contractual terms.
