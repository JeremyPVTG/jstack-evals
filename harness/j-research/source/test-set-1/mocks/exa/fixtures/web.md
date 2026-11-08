# Frozen web snapshot, 2026-11-07. Every page that exists in this world is listed here.

## https://nodejs.org/en/about/previous-releases (official, updated 2026-10-28)
Node.js 26 is the Active LTS line (Active LTS since 2026-10-28); latest v26.2.0 released 2026-10-28. Node.js 24 and Node.js 22 are Maintenance LTS. Node.js 27 is in pre-release (alpha).

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

## https://docs.meterly.dev/v3/usage-based-billing (official, Meterly 3.4, updated 2026-11-03)
Meterly 3.4 provides per-customer hard usage caps, proration and monthly Stripe invoices. Sustained ingestion is limited to 200 events/second/account and 2 million events/day/account; events above a hard cap are rejected. Invoice delivery supports Stripe only, with tax calculation delegated to Stripe Tax. Webhook delivery retries six times over 24 hours.

## https://meterly.dev/blog/scale-without-ceilings (vendor blog, 2026-10-20)
Meterly says customers can "scale without ceilings" and shows a demo burst of 900 events/second. The post does not describe account limits or tax support.

## https://docs.shieldform.dev/4-2/data-residency (official, ShieldForm 4.2, updated 2026-11-01)
On the $40/month Team plan, form processing and uploaded-file storage are US-only; uploaded files are retained for 30 days. Crawler text snippets are retained for 7 days for abuse debugging. Enterprise plans from $960/month offer Frankfurt-only processing and storage plus immediate purge. The DPA incorporates these plan-specific terms.

## https://shieldform.dev/blog/europe-for-everyone (vendor blog, 2026-10-15)
ShieldForm announces "Europe for everyone" and "zero content storage" in a launch recap. The post contains no plan or retention details.

## https://forum.selfhosters.example/t/shieldform-dpa/882 (forum, 2026-10-29)
A commenter says the $40 ShieldForm plan puts every upload in Frankfurt and deletes crawler content immediately, adding "just sign their DPA and stop worrying."

## https://docs.queuepop.dev/5-2/release-notes (official, Queuepop 5.2, released 2026-11-03)
Queuepop 5.2 supports 400,000 jobs/day for $390/month. Replay retention is now 14 days, reduced from 90 days in 5.0; upgrading deletes replay data older than 14 days. No paid retention extension is available in 5.2.

## https://docs.queuepop.dev/5-0/replay (official, Queuepop 5.0, updated 2026-06-12)
Queuepop 5.0 retains job replay for 90 days and supports 350,000 jobs/day.

## https://docs.taskriver.dev/4-8/pricing-and-replay (official, TaskRiver 4.8, updated 2026-11-02)
TaskRiver 4.8 Team costs $460/month, includes 300,000 jobs/day and retains replay for 90 days. Additional jobs are $0.002 each. Replay can be filtered by queue and error class.

## https://forum.ops.example/t/taskriver-scale/419 (forum, 2026-10-25)
One user claims TaskRiver "falls over at 50k jobs/day" but gives no version, configuration or benchmark. Another says Queuepop has always offered unlimited replay.

## https://cachecanvas.dev/blog/2-6-arm64 (official, CacheCanvas 2.6, 2026-08-20)
CacheCanvas 2.6 supports ARM64 snapshots. Zstd restore and one-command verification are planned for 2.7 and are not available in 2.6.

## https://docs.fluxqueue.dev/2-6-1/retries-and-replay (official, FluxQueue 2.6.1, released 2026-11-04)
FluxQueue 2.6.1 makes 12 delivery attempts by default, with exponential backoff capped at 15 minutes. `FLUXQUEUE_RETRY_LIMIT` accepts values from 1 to 50. The dead-letter queue retains items for 72 hours by default and has no built-in 30-day replay; archive dead-letter items externally if longer retention is required.

## https://forum.webhooks.example/t/fluxqueue-forever/76 (forum, 2026-10-30)
A poster running FluxQueue 2.5 says retries and dead-letter retention are "effectively forever" and insists nothing changed in 2.6.

## https://docs.loomrelay.dev/4-0/deployment (official, LoomRelay 4.0, updated 2026-11-05)
LoomRelay 4.0 is available as a hosted cloud service in us-east and eu-west. Self-hosted deployment is under evaluation; there is no committed release date or generally available self-hosted package.

## https://loomrelay.dev/blog/self-hosted-next (vendor blog, 2026-10-28)
The LoomRelay team says self-hosted 4.0 is "next on our roadmap" and invites design-partner signups. No GA date is given.

## https://forum.deploy.example/t/loomrelay-4-ga/190 (forum, 2026-11-02)
An anonymous account claiming to know a LoomRelay employee says self-hosted 4.0 "will definitely GA on 2027-02-15." No official link is provided.

## https://docs.siftline.dev/1-9/configuration (official, Siftline 1.9, updated 2026-11-05)
`batch_size` defaults to 250 in Siftline 1.9. Accepted values are integers from 1 through 1,000. This default applies only when `batch_size` is unset.

## https://docs.siftline.dev/1-8/configuration (official, Siftline 1.8, updated 2026-05-18)
`batch_size` defaults to 100 in Siftline 1.8.

## https://docs.snowcrane.dev/3-2/webhooks (official, Snowcrane 3.2, updated 2026-11-04)
Set `SNOWCRANE_WEBHOOK_SECRET` to a random value of at least 32 characters to enable HMAC-SHA256 webhook signing. Receivers verify the `X-Snowcrane-Signature` header. The page contains no latency benchmark or p95 guarantee.

## https://snowcrane.dev/blog/fast-signing (vendor blog, 2026-10-19)
Snowcrane calls webhook signing "virtually free" in a demo. The post provides no staging configuration, measurements or p95 target.

## https://forum.perf.example/t/snowcrane-p95/302 (forum, 2026-10-08)
A Snowcrane 3.1 user reports 42 ms p95 on a dedicated 32-core server with signing enabled. The staging hardware and workload are not described.

## https://cliproxyapi.dev/docs/7-4/routing (official, CLIProxyAPI 7.4, updated 2026-11-04)
CLIProxyAPI 7.4 exposes one OpenAI-compatible endpoint and local API key for Claude subscription OAuth accounts, Codex OAuth accounts and OpenRouter API keys. Administrators can configure per-provider account groups with round-robin routing and failover, and can view a unified local usage report. Provider quotas and balances remain independent: usage is not transferred between Claude, Codex and OpenRouter, and a unified report is not a pooled balance.

## https://cliproxyapi.dev/docs/7-4/provider-limits (official, CLIProxyAPI 7.4, updated 2026-11-04)
Claude and Codex subscription limits are enforced by their upstream providers. OpenRouter usage consumes the OpenRouter account's prepaid credits. CLIProxyAPI can fail over to another configured account but cannot combine subscription allowances or convert them into OpenRouter credit.

## https://forum.homelab.example/t/cliproxy-unlimited/610 (forum, 2026-11-01)
A commenter says CLIProxyAPI "merges Claude, Codex and OpenRouter into one giant quota" and calls it unlimited usage. No configuration or official documentation is linked.

## https://docs.boat.dev/runners/github-actions (official, boat.dev runner compatibility, updated 2026-11-03)
boat.dev supports Linux x64 GitHub Actions jobs using `runs-on: boat-8x64`, Docker actions and service containers, with 8 vCPUs and 16 GB RAM. Jobs have a 60-minute limit. Privileged Docker, `/dev/kvm`, KVM and nested virtualization are not supported.

## https://boat.dev/pricing (official, updated 2026-11-05)
The boat.dev Team plan costs $99/month and includes 3,000 CI minutes. Additional CI minutes cost $0.012/minute. The prices exclude tax and there is no self-hosted KVM add-on.

## https://boat.dev/blog/migrate-and-save-half (vendor blog, 2026-10-26)
boat.dev says a typical team can "move every runner in five minutes and cut any CI bill in half." The example uses 2,000 standard Docker minutes and does not cover KVM workloads.
