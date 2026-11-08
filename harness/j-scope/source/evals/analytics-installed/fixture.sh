#!/bin/bash
set -e
mkdir -p src
cat > package.json <<'J'
{"name": "portfolio", "private": true, "dependencies": {"next": "16.0.1", "react": "19.2.0", "posthog-js": "1.290.0"}}
J
cat > src/analytics.ts <<'J'
import posthog from "posthog-js";
// Product analytics for the whole site. Pageviews and link clicks are captured automatically.
export function initAnalytics() {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, { api_host: "https://us.i.posthog.com", capture_pageview: true });
}
J
cat > README.md <<'J'
# Portfolio
Next.js site. Analytics: PostHog (src/analytics.ts), set up 2026-07. No Google Tag Manager.
Traffic: about 40 visits a week.
J
