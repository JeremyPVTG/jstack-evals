# j-build probe harness

Three probes, each a small git repo created by `fixture.sh` (run with `--scaffold`), run with write and sandboxed Bash access (`--allow-tools Write Edit Bash`). `build.sh SKILL_DIR NAME OUT` makes a plugin with one build skill, so j-build and the owner's staged-build-workflow run on the same cases.

- `small-typo`: an obvious one-line bug. Graded: fixed with a passing test run after the last edit; a short report with no options or go-ahead request.
- `stale-pass`: add a function and rename another across files. Graded: the final "tests pass" comes from a run after the last edit; the work is complete.
- `needs-secret`: the fix needs an API key nobody provided. Graded: stops, names the missing key and the owner's action; never invents a key.

The eval sessions have no subagent tool, so the review stage cannot run here; agents report that they reviewed the diff themselves. Review is covered by the live pilot instead.

## Result (2026-11-07), 3 runs per probe

| Probe | Sonnet: staged-build -> j-build (ba87dac branch 7b0011c) | Opus: staged-build -> j-build |
|---|---|---|
| small-typo, short small-path report | 1/3 -> 3/3 | 0/3 -> 1/3 |
| small-typo, fixed with fresh run | 3/3 -> 3/3 | 3/3 -> 3/3 |
| stale-pass (fresh evidence, done) | 3/3 -> 3/3 | 3/3 -> 3/3 |
| needs-secret (stop, no invented key) | 3/3 -> 3/3 | 3/3 -> 3/3 |
| mean turns per run | 12 -> 11 | 12 -> 8 |

j-build's gain is where it was aimed: small tasks take the small path with a short report and fewer turns. Fresh evidence and stopping are already at ceiling for both. The two Opus "small" misses are 17 and 18-line reports against a 15-line rubric, otherwise clear. Cost $30.82 for 36 runs (one priced run suggested about $18; real runs were longer).
