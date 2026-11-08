# Hill-climb log (protocol: docs/decisions/2026-11-08-j-research-hill-climb-protocol.md)

Incumbent: a7f940a + hook. Spend counted from here against the $550 cap (review at $300).

## Candidate 1: b58df5c (open vault pages before relying on them)
Hypothesis: agents cite a vault page from its search snippet without opening it; adding that to the every-run checklist makes them read it.
Targeted cases: heldout-cases/purchase-approval-reuse, heldout-cases-2/latticecache-fresh-vault, evals/vault-fresh.
Screen: targeted cases, 3 runs, Sonnet and Opus, candidate and incumbent interleaved.
Screen result ($7.71): purchase-approval-reuse Opus 0.50 -> 0.83, Sonnet 0.50 -> 0.50 (Sonnet calls vault search, never read); latticecache and vault-fresh 1.00 both. Not the same direction on both models: **not kept**.

## Candidate 2: d93de69 (open a vault page with the read tool before citing it)
Hypothesis: the general wording did not move Sonnet; naming the action at the point of use (open the page with the read tool before citing it; search results show only snippets) will. Same targeted cases and screen.

## Test set 1 sealed
Written by Kimi K3.1 Pro (10 cases, 2 owner-sourced). Content hash 057d1c842d2becd9. Not opened by the climber; first look only on a frozen candidate.
Screen result ($8.09): purchase-approval-reuse Sonnet 0.50 -> 1.00, Opus 0.50 -> 0.83; latticecache and vault-fresh 1.00 both. Same direction on both models: **confirm**.
Confirm result ($59.86): purchase-approval-reuse 0.50 -> 1.00 on both models, 5/5 each; latticecache and vault-fresh unchanged at 1.00. Core Opus 1.00 -> 1.00. Core Sonnet 0.99 -> 0.90, all from social-lane-missing 1.00 -> 0.33: two of three candidate runs were harness rejections (exa/web_fetch_exa "a result in the trace is not one the harness gave"; ungraded). Classified as infrastructure: the plugin has no PostToolUse hook, the skill change does not touch fetching, and both rejected runs fetched the same Exa page twice. Retried once per protocol. Bootstrap over targeted cases: P(gain > 0) = 0.70 on each model, structurally capped because only 1 of 3 targeted cases could move; raised with the council.
Retry with 5 attempts per variant (round 5 rule): incumbent 4 graded (all 1.00), 1 excluded as the known schema-hint fault (1/5, under the one-third threshold); candidate 5 graded (all 1.00), 0 excluded. Core Sonnet with exclusions: incumbent 0.99, candidate about 0.98 (within 0.03). Named failing case purchase-approval-reuse: 0.50 -> 1.00 on both models, 5 vs 5 runs each, bootstrap lower bound above 0. **Candidate 2 kept**; it is the new incumbent.

## Freeze for test set 1, first look
Owner chose (j-scope, 2026-11-08): test look, then ship. Frozen: jstack d93de69 (j-research skill + scripts/research_hook.py), hook via hooks/hooks.json (UserPromptSubmit, Jev jev-1.14.0, thresholds 0.70/0.30), harness jstack-evals as committed after this entry, run_eval.sh with tool search on, schema-hint exclusion rule (climb/rejections.py). Test set hash 25606b41ffda81fe. Look 1: 10 cases x 5 runs x Sonnet and Opus, candidate and tools-only.

Format fix before any look (2026-11-08): the eval runner rejects `weight: 0` ("Number must be greater than 0"), so all 10 `critical.md` graders were changed to `weight: 0.001`, nothing else; no agent run had happened. The gate reads the critical grader directly, so the pass decision is unchanged. Re-sealed: content hash 44f944789e3fe439.

## Test set 1, look 1 (failed the gate; set is now dev)
Candidate d93de69 + hook, 5 runs per case. Sonnet: mean pass rate 0.82, cases below 4/5: owner-boatdev-ci-cost 1/5, siftline-default-batch 2/5, meterly-adopt-existing 3/5; critical failures 3. Opus: 0.80, below 4/5: owner-boatdev-ci-cost 0/5, siftline-default-batch 2/5; critical failures 4. Tools-only pass rate 0.34 (Sonnet), 0.46 (Opus). Excluded as schema-hint fault: 1 (candidate Sonnet). Cost $121.85. Per protocol: no second look; the set becomes dev.
Owner decision (2026-11-08): ship d93de69 now without a "proven" claim; grader fixes and a second test set wait for evidence from real use. Shipped to jstack main and claude.ai (j-research v3). Climb spend: about $207 of $550.
