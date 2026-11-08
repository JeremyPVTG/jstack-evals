# j-research eval harness

Measures what j-research adds over the same agent with the same tools. `build.sh JSTACK_REPO COMMIT` assembles two plugins named `jstack` with identical MCP servers (jvault, Exa, Tavily, Firecrawl), mocks and cases: `build/with-skill` contains `skills/j-research` at the pinned commit, `build/tools-only` does not. The score gap between them is the skill's contribution. (A plain `--ablation with-without` run would also remove the mocked tools from the baseline, so it would measure the tools, not the skill.)

- `source/evals/`: 8 core cases plus 5 trigger cases. Vault and web are frozen fixtures (`mocks/*/fixtures/`); search providers are judge-model mocks restricted to the snapshot, using each server's real `tools/list` (`_tools.json`).
- `source/trigger-evals/`: 15 two-turn cases (11 should trigger, 4 should not). `source/heldout-evals/`: 10 different prompts, used only to check the chosen description.
- `trigger_test.py LABEL FILE`: run the trigger suite with a candidate description. `descriptions/` holds the variants tested.

Run: `claude plugin eval build/<variant> --ablation none --tag core --runs 2 --model sonnet --threshold 0 --trust-plugin --no-publish --json results/<name>.json` (from the jeremy@ Claude config). Results JSON in `results/`.

## Results, 2026-11-07 (Sonnet as the agent, 2 runs per case)

Triggering (should-trigger runs that invoked j-research; false triggers on non-research prompts):

| Description | Tuning set | Held-out | False triggers |
|---|---|---|---|
| A, jstack a4c547a | 5/22 | 2/12 | 0/8, 0/8 |
| B, "depends on current information" | 19/22 | 7/12 | 0/8, 0/8 |
| C, directive (adopted in jstack 1fa56a6) | 21/22 | 11/12 | 0/8, 0/8 |

Core cases, mean score per case:

| Case | Tools only | j-research a4c547a | j-research 1fa56a6 |
|---|---|---|---|
| build-stops-for-scope | 1.00 | 1.00 | 1.00 |
| compile-into-vault | 0.00 | 0.36 | 0.91 |
| empty-lane | 1.00 | 1.00 | 1.00 |
| lookup-control | 1.00 | 1.00 | 1.00 |
| multi-lane | 0.67 | 0.67 | 0.50 * |
| social-lane-missing | 1.00 | 1.00 | 1.00 |
| vault-fresh | 0.00 | 0.00 | 1.00 |
| vault-stale | 0.25 | 0.38 | 1.00 |
| **Mean** | **0.61** | **0.68** | **0.93** (0.99 excluding *) |

\* One of the two multi-lane runs was rejected by the harness ("a result in the trace is not one the harness gave") after a long Exa fetch; that run's transcript shows two providers, captured sources, lint and a coverage line. It scores 0 in the official number.

Findings: without the skill, Sonnet answered "current" questions from memory in one turn and never searched; with the old description the skill rarely triggered, so most of its value was invisible; the directive description fixed triggering without false triggers. Costs: about $1.1 to $1.6 per 16-run core pass, $1 per trigger pass.

### Lane brief re-check, jstack c94d800 (2026-11-08)

`--case '*-lane'`, 2 runs each, Sonnet: multi-lane 1.00 (2/2), empty-lane 1.00 (2/2), $1.17 including judging. No regression from adding the lane brief. This does not show the brief helps: the earlier multi-lane 0.50 was a harness rejection, not a wrong answer, and the run traces were cleaned up before I could check whether the agent delegated lanes to subagents.

## Readiness pass, jstack c94d800 (2026-11-08)

Same harness, traces kept (`--keep-temp`), mean score per variant. Core cases are mine; held-out cases (`source/heldout-cases/`, 5 cases) were written by GPT-6.1 Sol from a behaviour list, without reading the skill, and graded on substance.

| Suite | Model | Runs per case | Tools only | j-research |
|---|---|---|---|---|
| Core (8) | Sonnet | 5 | 0.62 (39 runs) | 0.98 (40 runs) |
| Core (8) | Opus | 3 | 0.71 | 0.93 |
| Held-out (5) | Sonnet | 3 | 0.10 | 0.53 |
| Held-out (5) | Opus | 3 | 0.13 | 0.60 |

Findings:

- **The gain holds on cases the author did not write**, on both models: vault reuse and re-checks, primary over marketing and social sources, and saying what was not found.
- **Triggering is the main weakness.** On held-out prompts j-research fired in 10/15 Sonnet runs and 12/15 Opus runs. It never fired on "How would you build a small internal purchase-approval app for us?" (0/6): both models designed a custom app from memory instead of finding the existing tool in the vault. When it fired on Sonnet, held-out mean was 0.80.
- **Subagents were never used**: 0 delegations in 94 with-skill runs, so the lane brief is untested by behaviour.
- **Opus needs the skill less**: without it Opus already reuses fresh vault pages (1.00); the skill's gain on Opus is re-checking stale pages (0.25 to 1.00), compiling (0.61 to 0.91) and the scope stop (0.67 to 1.00).
- Known case defects: `lookup-control` scores 0.50 on Opus with and without the skill because the frozen page claims Node 24 is Active LTS in November 2026 and Opus rightly doubts it; `rivetdb-regional-failover` scores 0.50 on every run because its answer grader requires every point stated explicitly (answers read as correct; grader left unchanged to avoid tuning after the fact); `compile-into-vault` loses 0.09 because agents omit spend for free mocked calls.
- Cost reported by the harness for this pass: about $69.

Not changed after seeing held-out results: the skill, its description, and the held-out graders (except rewriting the held-out vault-first regexes, which were invalid JavaScript, before any run).

Limits: 2 runs per case, one agent model, frozen mock web, graders partly judged by a model, cases written by the skill's author.
