# T3-first model transfer

T3 Code is the fixed host for the primary benchmark. The provider adapter and selected model are explicit experimental variables. Standalone CLI trials are optional and cannot certify T3 behavior.

## Matrix

Choose available models at experiment setup from T3's current catalog. Keep model identifiers and provider-instance routing in the run configuration, not in skills. No model list or account identity is committed as a universal default.

Start the development pilot on one configuration. Confirm the frozen candidate and matched baseline on at least two models from distinct provider families inside T3 before claiming tested model transfer. Report every tested configuration separately; no average can hide a critical regression on one. Additional families can extend coverage without changing the skill text.

Use the same task, fixtures, assertions, authorization, and tools within each baseline/candidate pair. Preserve model settings within the pair. Reasoning setting names are not equivalent across providers: record their actual values rather than treating matching labels as equal compute. Record token availability, wall-time budgets, and any unequal tool affordances.

For cross-model comparisons, distinguish the shared-capability task subset from provider-specific features. Report unsupported cases and coverage rather than silently dropping them. A capability absent in a provider is an integration limitation; a fabricated capability or unauthorized substitution is an agent failure.

## Evidence per configuration

Record installed T3 version/build and upstream commit if known; provider adapter/driver and version if exposed; model ID/version; reasoning/runtime settings; discovered skill root and loaded file hashes; tool availability; fixture, subject, suite, and grader revisions; and per-trial artifacts. Use null for unavailable version fields. A source snapshot is not evidence that the installed build matches it.

T3 auto-discovery, explicit skill invocation, and INDEX fallback are separate conditions. Test natural discovery independently of explicit-load task outcomes. Do not prompt a supposedly unassisted baseline with jstack descriptions or leave installed jstack copies reachable through another scanned root.

## Host behavior suite

[t3-integration.json](../suites/t3-integration.json) specifies host contract cases. They are additional to the 15 core task specifications and currently have no executable fixtures or graders. Delegation cases are explicitly authorized in their task; they do not grant the benchmark runner general permission to launch extra work.

Use the jstack subject's hosts/t3-source.lock.json as the upstream reference. Link to upstream cases for inspiration but classify reused or adapted cases as development material, never unseen confirmation. Recheck actual current tools before dispatch; no model runs are started merely by reading the matrix.

## Promotion

Apply the main protocol's critical-failure and quality gates independently to each supported T3 configuration. Require a useful paired tradeoff rather than an identical numeric score across models. Until cross-provider runs pass, describe the stack as designed to be model agnostic and list compatibility as unverified.
