# jstack-evals

Behavioural evaluations for [jstack](https://github.com/JeremyPVTG/jstack), a set of agent skills for research, scoping, building and review. Each harness runs the same cases with and without a skill, on Claude Sonnet 5.5 and Opus 5.5, so the score gap is the skill's contribution.

## Results

| Skill | Question | Result | Shipped? |
|---|---|---|---|
| [j-review + j-deliver](harness/j-review-deliver/RESULTS.md) | Do the rebuilt review skills beat the six older ones and no skill? | 30/30 against 20/30 (old) and 19/30 (none), Sonnet, 3 runs per probe | Yes |
| [j-research](harness/j-research/README.md) | Does the skill beat the same agent with the same tools? | Held-out mean 0.10 to 0.87 (Sonnet), 0.13 to 0.80 (Opus); the 0.90 release gate on the sealed test set was missed (0.82, 0.80) | Yes, gate missed and recorded |
| [j-build](harness/j-build/README.md) | Does j-build take the small path on small tasks? | Short small-path report 1/3 to 3/3 (Sonnet), 0/3 to 1/3 (Opus); evidence and stopping already at ceiling | Yes |
| [jvault search](harness/jvault-search/README.md) | Does adding vector matches to BM25 find pages worded differently? | Top 3: 10/12 to 12/12; mean reciprocal rank 0.65 to 0.82 | Yes |
| [j-scope](harness/j-scope/README.md) | Does tighter wording cut over-asking? | No gain: current wording already 1.00 | No |
| [j-verify](harness/j-verify/README.md) | Does a verify skill catch bugs a plain agent misses? | No gain: baseline at ceiling on every case | No |
| [j-verify, pstack way](harness/j-verify-pstack/RESULTS.md) | Does an independent base-vs-head verdict help? | Worse: 1/3 against 3/3 without the skill (sandbox setup failed) | No |
| [Jev judge](experiments/2026-11-07-jev-judge/README.md) | Does judging search results before reading save reads? | Kept 10 cited sources against 13 for the search provider's own order | No |
| [Trigger classifier](experiments/2026-11-08-trigger-classifier/) | Jev or Haiku for the j-research reminder hook? | On 10 fresh validation prompts both fired on 10/10 and falsely on 0/10; Jev's median latency was 176 ms against Haiku's 699 ms | Jev used in the optional hook |

Every table above links to its own limits. Common ones: cases are mostly written by the skill's author (held-out sets were written by other models without reading the skill), web search is frozen fixtures, graders are partly model-judged, and runs are 2 to 5 per case.

## Layout

- `harness/<skill>/`: `source/` holds cases, fixtures and graders; `build.sh` assembles a plugin with or without the skill; `run_eval.sh` runs one pass with `claude plugin eval`; `results/` holds the raw JSON, including full agent transcripts.
- `experiments/`: one-off questions with their own data and scripts.
- `docs/decisions/`: protocols agreed before a run (for example the j-research hill-climb rules).
- `scripts/subject.py`: pins the exact jstack commit under test.

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

- [Protocol](PROTOCOL.md): comparison conditions, scoring, budgets and release gates.
- [Hill-climb rules](docs/hill-climb.md) and [evidence contract](docs/evidence.md).
- [T3 model matrix](docs/t3-matrix.md).

There is no aggregate score. Report task success, failures, cost and limits separately, with full denominators.
