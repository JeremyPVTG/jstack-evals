# jstack-evals

Behavioural evaluations for [jstack](https://github.com/JeremyPVTG/jstack), a set of agent skills for research, scoping, building, review and delivery. A skill stays in jstack only when it helps complete realistic work. This repository tests that claim: most harnesses run the same cases with and without a skill and score the gap. Each harness states its models, its comparison and the jstack commit it tested.

There is no aggregate score. Each result reports task success, failures, cost and limits separately, with full denominators, including the runs where a skill made no difference or made things worse.

## Coverage

This table lists jstack's current skills and what has been measured for each, as of 2026-11-25. "Specs only" means the case is written in `suites/` but has no fixtures, graders or runs yet.

| Skill | Status | Result or plan |
|---|---|---|
| j-review + j-deliver | Measured | [30/30 against 20/30 for the older pr-* skills and 19/30 for no skill](harness/j-review-deliver/RESULTS.md) (Sonnet, 4 probes, 3 runs each). Shipped. More cases are specs only. |
| j-research | Measured | [Held-out mean 0.10 to 0.87 (Sonnet), 0.13 to 0.80 (Opus)](harness/j-research/README.md) against the same agent with the same tools. The 0.90 release gate on the sealed test set was missed (0.82, 0.80) and recorded. Shipped. |
| j-build | Measured | [Short small-path report 1/3 to 3/3 (Sonnet), 0/3 to 1/3 (Opus)](harness/j-build/README.md); evidence and stopping were already at ceiling. Shipped. Demonstration proof (jstack, 2026-11-17) is unmeasured. |
| j-scope | Measured, no gain | [Tighter wording did not cut over-asking](harness/j-scope/README.md): the current wording already scored 1.00. The candidate wording was not shipped; a decision template and a lint warning were. |
| j-evidence | Planned, due 2026-11-30 | Count transcript runs where it changed a reported status or kept an uncertainty. Fewer than two: fold into j-research. Cases are specs only. |
| j-skill-audit | Planned, due 2026-11-30 | Run once on jstack. Keep only if it finds a cut or merge the owner accepts that nothing else found. Cases are specs only. |
| j-bookmarks | Planned, due 2026-11-30 | After three weekly runs, every saved bookmark in the window has a linked ledger row. |
| j-launch | Planned, due 2026-12-16 | At least three launches, each starting on the named item with every named skill loaded. Routing and T3 cases are specs only. |
| j-daily | Not measured | No harness and no plan. |

The plans and their cut rules are in jstack's [skill value audit](https://github.com/JeremyPVTG/jstack/blob/main/docs/skill-value-audit.md). The plans for j-evidence, j-skill-audit, j-bookmarks and j-launch measure real use from transcripts, not runs in this repository.

## Past questions

Skills that were tried and dropped, and one-off experiments.

| Question | Result | Outcome |
|---|---|---|
| [j-verify](harness/j-verify/README.md): does a verify skill catch bugs a plain agent misses? | No gain: baseline at ceiling on every case | Dropped; folded into j-build |
| [j-verify, pstack way](harness/j-verify-pstack/RESULTS.md): does an independent base-vs-head verdict help? | Worse: 1/3 against 3/3 without the skill (sandbox setup failed) | Dropped; jstack points at pstack's verification skills |
| [jvault search](harness/jvault-search/README.md): does adding vector matches to BM25 find pages worded differently? | Top 3: 10/12 to 12/12; mean reciprocal rank 0.65 to 0.82 | Shipped |
| [Jev judge](experiments/2026-11-07-jev-judge/README.md): does judging search results before reading save reads? | Kept 10 cited sources against 13 for the search provider's own order | Not shipped |
| [Trigger classifier](experiments/2026-11-08-trigger-classifier/): Jev or Haiku for the j-research reminder hook? | Both fired on 10/10 fresh prompts and falsely on 0/10; median latency 176 ms (Jev) against 699 ms (Haiku) | Jev used in the optional hook |

## Limits

Every result links to its own limits. The common ones:

- Most cases are written by the skill's author. The j-research held-out sets were written by other models that did not read the skill.
- Web search runs against frozen fixtures.
- Graders are partly model-judged.
- Runs are 2 to 5 per case.
- Results describe the jstack commit each harness names, not current jstack main.

## Layout

- `harness/<skill>/`: `source/` holds cases, fixtures and graders; `build.sh` assembles a plugin with or without the skill; `run_eval.sh` runs one pass with `claude plugin eval`; `results/` holds the raw JSON, including full agent transcripts.
- `harness/retro-loop/gate.py`: the retro improvement loop's gate (jstack#18). `decide MANIFEST` reads recorded `claude plugin eval` results and checker output and returns accepted, rejected, inconclusive or retry (reproduced or not_reproduced in reproduce mode) with reasons per model. `hash CASE_DIR` prints the sha256 a frozen case is checked against. It calls no model.
- `harness/retro-loop/run.py`: the loop's run driver (jstack#22). Given the runner's plan for a finding, the frozen cases, the checker and the jstack revisions, it builds one plugin per condition from `git archive`, runs `claude plugin eval` with the j-build harness's flags inside a local wrapper (`$JSTACK_RETRO_CLAUDE`, or `harness/retro-loop/wrapper.local.json` copied from `wrapper.example.json`, since billing and secret routing are per machine) (incumbent and candidate paired per case and model in a seeded random order recorded as `order_seed`, run counts as `gate.py` plans them, `--max-cost-usd` from what is left of the step's budget), runs the checker, writes the manifest and prints `gate.py`'s decision. Raw results stay in a run directory outside both repositories (default `~/.local/share/jstack-retro-loop/runs/<finding>/`); running it again with the same inputs reuses saved results. `--help` lists the options.
- `harness/retro-loop/record.py`: copies one decided reproduce or gate run into the public experiment record, `harness/retro-loop/records/<finding>/`: the frozen target and controls under `cases/<freeze>/`, the soft holdout under `holdout/<freeze>/` (gate records only, so it joins after its gate), and per run the manifest with relative paths, the decision, the ledger extract, the result and checker files and the SKILL.md copies. Records are append-only, and every copied manifest must give its recorded decision again before anything is written. The retro-loop skill in jstack opens a record pull request for every reproduce and gate outcome.
- `experiments/`: one-off questions with their own data and scripts.
- `suites/`: case specifications not yet built into harnesses: [development cases](suites/development.json) per skill, [T3 integration cases](suites/t3-integration.json), and [routing sketches](suites/routing-sketches.json) that say which skill a request should load.
- `subject.lock.json` and `subjects/`: pins of the jstack commit under test. The root lock pins jstack 8f66363 (2026-11-07); `subjects/` keeps earlier pins. Harnesses that pin their own commit name it in their README.
- `docs/decisions/`: protocols agreed before a run, such as the j-research hill-climb rules.
- `tests/`: checks for the pinning tool, for doc links, and for the retro loop gate, run driver (with a fake `claude`) and records. They do not measure model performance.
- [AGENTS.md](AGENTS.md): rules for agents working in this repository, including holdout handling and never editing a grader to win an existing run.

## Reproduce

Keep sibling checkouts named `jstack` and `jstack-evals`.

```sh
python3 scripts/subject.py pin --repo ../jstack --output subject.lock.json
python3 scripts/subject.py verify --repo ../jstack --lock subject.lock.json
python3 -m unittest discover -s tests
```

Pin records the subject's full commit, tree and tracked file hashes, and refuses to overwrite an existing lock. Each harness README gives its build and run commands. Runs bill an Anthropic API key; each README states what its pass cost.

## Notes on the recorded transcripts

Transcripts contain local paths from the machine that ran them. Run logs keep the jstack commit IDs from before the 2026-11-21 history rewrite; [docs/jstack-commit-ids.md](docs/jstack-commit-ids.md) maps them to current IDs. In `harness/j-build/results/staged-*.json`, the loaded text of a private comparison skill was replaced with a marked redaction on 2026-11-21; scores and the rest of each transcript are unchanged.

## Design

- [Protocol](PROTOCOL.md): comparison conditions, scoring, budgets and release gates. The target is T3 Code across models.
- [Hill-climb rules](docs/hill-climb.md) and [evidence contract](docs/evidence.md).
- [T3 model matrix](docs/t3-matrix.md).
