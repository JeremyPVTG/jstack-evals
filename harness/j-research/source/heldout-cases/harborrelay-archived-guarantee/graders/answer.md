---
type: llm
---
PASS only if all of the following hold:
- The answer advises keeping the duplicate-event guard for the Frankfurt-to-Montreal route.
- It cites the official HarborRelay 4.2 delivery-guarantees page or 4.2 changelog dated 2026-11-04, and correctly scopes the claim to 4.2: cross-region forwarding is at least once; the 24-hour deduplication window applies inside one region and does not survive a region boundary.
- It resolves the source conflict: the 2026-11-06 launch article's worldwide exactly-once claim is not the supported guarantee, and the official 4.0 archive dated 2026-08-20 described a retired 7-day global-receipt preview, not the current release.
- It recognizes that the saved HarborRelay note reviewed 2026-09-30 with high volatility is expired as of 2026-11-07 and rechecks its preview-era claim before deciding.
FAIL if any required point is absent; if it removes the guard based on the article, archive, or vault note; or if it turns regional deduplication into an end-to-end exactly-once guarantee. Judge substance, not labels or wording.
