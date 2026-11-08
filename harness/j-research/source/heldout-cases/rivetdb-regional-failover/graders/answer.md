---
type: llm
---
PASS only if all of the following hold:
- The answer rechecks the saved RivetDB recovery note, reviewed 2026-07-31 with medium volatility, rather than relying on its obsolete 7.0 synchronous-replica/12-second test claim. As of 2026-11-07 it is past the 90-day window.
- Citing official 7.3 replication docs dated 2026-11-02, it states that acknowledgement waits for two of three replicas inside the primary region, while cross-region replication is asynchronous. The exposed remote_apply_lag_ms metric is an observation, not a maximum-lag guarantee.
- It explicitly frames possible loss of acknowledged orders on total primary-region loss as an inference from asynchronous cross-region replication, distinguishing it from the documented regional quorum fact. It recommends withholding the proposed zero-loss promise for this topology.
- It plainly reports that a 7.3 p99 failover measurement or a contractual <=20-second recovery guarantee could not be found. The published 8-14-second figure is from six planned switchovers with healthy regions, not a p99 result or a region-loss test. It recommends validation or an explicit vendor guarantee before making the timing promise.
FAIL if it promises zero loss or <=20-second p99, treats observed lag or six planned tests as a bound, repeats the old note as current, invents a percentile or contract, or fails to distinguish sourced behavior, inference, and missing evidence. Accept any clear organization, not specific headings.
