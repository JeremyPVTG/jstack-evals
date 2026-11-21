# j-scope eval harness

One-turn cases for j-scope (`source/evals/`): each gives a brief plus a small repo (created by `fixture.sh`, run with `--scaffold`) and grades the agent's first reply: at most 4 decision questions, each with a recommendation (`asks`); no question asks a fact the repo answers (`facts`); at least one cut proposed (`cut`). AskUserQuestion is not available in `claude plugin eval` sessions, so agents ask in their message and the graders judge that.

`build.sh JSTACK_REPO COMMIT OUT` makes a plugin with only j-scope at COMMIT. `run_eval.sh` runs a pass billed to the Platform key.

## Result (2026-11-07): no gain, wording not shipped

| Model | Current (jstack 75be255) | Candidate 27f8e51 (budget, facts first, template) |
|---|---|---|
| Sonnet, 4 cases x 3 runs | 1.00 | 0.97 (one `asks` miss: decisions framed as facts with no marked recommendation) |
| Opus, 4 cases x 3 runs | 1.00 | 1.00 |

The current j-scope already settles repo facts, asks few questions with recommendations, and cuts scope on these cases. The overruns found in real use (up to 19 decisions; facts asked as decisions; see the vault page "j-scope in practice") come from long multi-turn sessions that one-turn cases do not reproduce. Shipped instead: the decision template and a lint warning for scope pages (jstack db762cf). Cost: $72.65 for 48 runs, about $1.50 a run, well above the $10 to $20 estimated beforehand.

A multi-turn eval with a simulated owner is the next step if real sessions keep overrunning.
