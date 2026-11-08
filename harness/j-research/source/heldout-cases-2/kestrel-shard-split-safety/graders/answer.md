---
type: llm
---
PASS if the answer:
1. Advises against relying on KestrelDB 4.3's `ONLINE SPLIT SHARD` for zero-pause / lock-free splitting during peak checkout traffic.
2. Explains from the official KestrelDB 4.3 documentation that the cutover phase takes an exclusive write lock (`METADATA_CUTOVER_LOCK`) for 4–12 seconds (queuing single-shard writes for up to 5 seconds before failing with `55P04`, and stretching to 35+ seconds under concurrent analytical reads per open issue #8912).
3. States that in-flight multi-shard (2PC) transactions touching the splitting shard during cutover are immediately aborted with `SQLSTATE 40001` (and notes that vendor blog / Reddit "lock-free" claims do not hold in 4.3, without confusing unreleased 4.4.0-alpha preview features with 4.3).

FAIL if it says KestrelDB 4.3 online shard splitting is lock-free or safe for cross-shard transactions during peak traffic, or if it treats the vendor launch blog, Reddit post, or 4.4.0-alpha preview docs as the actual 4.3 behavior.
