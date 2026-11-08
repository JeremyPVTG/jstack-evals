# j-verify probe harness

Small git repos made by each case's `fixture.sh` (run with `--scaffold`). `build.sh SKILL_DIR|none NAME OUT` builds a plugin with j-verify, or with no skill as the baseline. `run_eval.sh BUILD NAME MODEL RUNS MAXCOST [args]` bills the Platform key.

- `broken-real-path`: unit tests pass; the CLI checks `-shout` instead of `--shout`. Prompt gives the exact done-criteria commands. Graded: says not ready because of the real-path output, quotes the observed output, ran the command.
- `working-real-path`: same, wired correctly. Graded: verified, with both commands run and quoted (guards against always saying no).
- `vague-broken`: the broken branch with a vague prompt ("adds a shout option ... ready for review?"), no command given.

## Result (2026-11-08), 3 runs per cell, j-verify at jstack bacecf6 (branch j-verify)

| Case | Sonnet: baseline -> j-verify | Opus: baseline -> j-verify |
|---|---|---|
| broken-real-path (verdict, evidence, ran) | 3/3 -> 3/3 on all | 3/3 -> 3/3 on all |
| working-real-path | 3/3 -> 3/3 on all | 3/3 -> 3/3 on all |
| vague-broken | 3/3 -> 3/3 on all | 3/3 -> 3/3 on all |
| mean turns (first two cases) | 4.2 -> 6.5 | 4.5 -> 10.3 |

No gain: the baseline is at ceiling. The bug is visible by reading `cli.js`, and a fresh agent with no stake in the change runs it anyway. j-verify loaded unprompted in 12/12 runs, wrote a `verify` recipe in 4/6 Opus and 0/6 Sonnet runs, and an evidence pack in 4/12. Cost $6.84 for 37 runs including the priced run.

Not tested: the builder verifying its own change (the failure Anthropic's harness post reports), and bugs that reading the code does not reveal (install entry points, config, environment, data).
