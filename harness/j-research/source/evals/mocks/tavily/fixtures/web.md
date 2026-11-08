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
