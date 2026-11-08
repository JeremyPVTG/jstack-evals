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

Limits: 2 runs per case, one agent model, frozen mock web, graders partly judged by a model, cases written by the skill's author.
