# j-research hill-climb protocol (2026-11-08)

Owner asked to hill-climb j-research's eval scores to 0.95, agreed by a council (Claude Opus 5.5, GPT-6.1 Sol, GLM 5.3). Round 1: all three said a 0.95 suite mean is false precision as a gate on 5 to 8 cases with 0.05 to 0.10 rerun noise. Round 2: all three accepted the merged draft with changes, merged here. Owner set the spend cap.

## Targets

- **Dev goal (not a gate):** mean >= 0.95 on Sonnet and on Opus over core + held-out 1 + held-out 2.
- **Gate, on a fresh test set, Sonnet and Opus separately, 5 runs per case per model:**
  - A run **passes** if its answer grader passes (majority of the judge's 3 votes) and it has no critical failure. Trace checks (regex, tool use) are reported as their own lines and do not decide a pass, except where a case's spec names one as the decisive behaviour.
  - Mean per-case pass rate >= 0.90.
  - No case below 4 of 5 runs.
  - Zero critical failures (fabricated evidence, an unsupported guarantee stated as fact, an unsafe recommendation), from a **separate critical-failure judge pass** with its own prompt over every test-set trace; verdicts stored in the results JSON next to the scores.
  - The weighted grader score is reported alongside, but the binary pass rate decides.
- **Tools-only gap:** reported as a paired improvement with its bootstrap interval; diagnostic, not a gate.
- **Triggering:** zero false fires is a hard floor; should-fire >= 0.95.

## Sets and looks

- Core, held-out 1 and held-out 2 are dev and regression sets (held-out 2 had one look across four variants).
- **Fresh test set:** 10 cases, all written by Kimi K3.1 Pro, which has written none so far, from the behaviour spec, without reading the skill, earlier sets, transcripts or graders. Two of the ten start from the owner's real past research questions; Kimi also writes their rubrics and fixtures.
- **Freeze before the first look:** candidate commit, hook and its configuration, fixtures, rubrics, judge and harness configuration.
- **At most two looks, non-adaptive:** the second look reruns the same frozen candidate with fresh runs; both looks must pass. If the first look fails, or any change is informed by it, the set becomes dev and a new test set is needed. Tools-only runs on the test set do not count as a look.

## Deciding whether a change helped

- One behavioural change per candidate; its hypothesis and targeted cases are written down before the run.
- Screen: the targeted dev cases, 3 runs, both models, candidate and incumbent interleaved.
- Confirm: the targeted cases with 5 runs, plus core with 3 runs as the regression check.
- Keep a change only if, on each model, the gain on the **named failing cases** is positive with a 90% lower bound above 0 (paired bootstrap: run differences within each named case, then cases resampled with equal weight), and the gain points the same way on both models. Other targeted cases and core are no-regression checks: no targeted case drops, and core does not drop more than 0.03. Otherwise revert and record it. *(Amended in council round 4: a bootstrap over mostly-ceiling control cases could never pass a clean single-case fix.)*
- The named failing cases are frozen in the climb log before screening starts. A fix proven on named cases shows it works there, not that it generalises; the fresh test set decides that.
- Ungraded runs (harness rejections) are left out of every average and do not trigger the core check. If more than a third of either variant's runs on a case are rejected, that comparison is inconclusive, and an inconclusive core comparison cannot clear the regression check: the harness is repaired and the case rerun for both variants first.

## Grader and fixture defects

Rule: the defect is shown from the spec (the skill text or reality), not from traces; recorded here or in a sibling decision before regrading; applied to every variant; stored traces regraded where possible; original scores kept.

- `lookup-control`: make the fixture's facts consistent with the evaluation date; split correctness and brevity into separate graders.
- `compile-into-vault`: drop the spend requirement (the skill allows omitting spend when there is none).
- `rivetdb-regional-failover`: rubric unchanged during the climb; after a candidate is frozen, GPT Sol (its author) may revise it from intent alone, without answers; both versions reported.
- `purchase-approval-reuse`: not a grader defect. The skill says not to search the web for what a fresh vault page covers, so the web search is a skill failure. The no-web check is reported as its own efficiency line.
- Harness rejections ("a result in the trace is not one the harness gave"): classified before exclusion. Only independently established infrastructure faults are retried (once); candidate-caused violations count as failures; if the retry also fails, that comparison is reported inconclusive.

### Known harness fault: Claude Code's schema hint (council round 5, unanimous: option B)

Tool search stays on in eval runs, as in the owner's real sessions. When an agent calls a deferred tool before loading its schema, the mock returns a tool error and Claude Code appends a schema hint; the harness then rejects the run. A rejection is classified as this fault only when a tool result in the trace equals the mock's recorded output exactly, followed by exactly Claude Code's hint (`climb/rejections.py`, `HINT_PREFIX`, frozen as seen on 2026-11-08). Such runs are excluded from averages, kept as raw traces, and counted against all attempts, per variant. Every other rejection follows the general rule above.

- Exclusion rates are compared between variants: they may depend on variant behaviour, and a difference of more than one run in five is reported as a behaviour change, not noise. Similar counts are not claimed as equivalence.
- A case where this fault blocks a comparison is rerun with 5 attempts per variant, then 10 in total if the round-4 threshold (more than a third rejected) is hit; if still inconclusive, the candidate is not promoted on that evidence.
- `ENABLE_TOOL_SEARCH=false` (all tools upfront; verified to pass through the eval environment) is kept as a diagnostic only.
- The fault is reported upstream to Claude Code.

## Budget and stops

| Step | Runs | Approx. cost |
|---|---|---|
| Screen one change (targeted ~5 cases, 3 runs, 2 models, 2 variants) | 60 | $32 |
| Confirm it (targeted, 5 runs, 2 models, 2 variants; core 3 runs, 2 models) | 148 | $78 |
| First test look (10 cases, 5 runs, 2 models, candidate + tools-only) | 200 | $105 |
| Second test look (same candidate only) | 100 | $53 |

- Cap $550 incremental, judging and retries included; review with the owner at $300 (owner's decision, 2026-11-08).
- Stop at the first of: the gate is met; three candidates in a row without a kept gain; SKILL.md grows more than 20% in tokens; median turns or cost per run rises more than 25%; the cap. If the cap is reached without a decision, report "inconclusive".

## Do not optimise

Answer padding or mandatory headings to please the judge; tool-call order shaped to regexes; a more eager hook; forced subagent delegation (the lane brief is decided on reasoning: 94 runs never delegated); skill text naming fixture products, dates or topics; the saturated core score; any grader edit made after seeing the result it changes.
