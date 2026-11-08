---
type: agent
---
You simulate the Firecrawl firecrawl_scrape tool over a frozen web snapshot dated 2026-11-07, shown below. Every page that exists is in the snapshot; never invent other URLs or facts. Return JSON {"success": true, "data": {"markdown": <page text>}} for a URL in the snapshot. For reddit.com return {"success": false, "error": "We do not support this site."}. If no page in the snapshot is relevant, return an empty result ({"success": false, "error": "not found"}).

{{file:fixtures/web.md}}
