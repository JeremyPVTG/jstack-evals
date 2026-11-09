# j-verify (pstack way) seeded probe, 2026-11-08

Subject: jstack branch j-verify-pstack 9b23f7b. Sonnet 5.5, 3 runs, judges Opus 5.5, Platform key. Fixture: notes CLI with a repo verify skill (`.agents/skills/verify-notes`, feature map); branch `feat/tags` adds `--tag`, 4 tests pass, both done-criteria hold, but storing notes as objects makes `notes search` throw (`n.includes is not a function`); it works on main.

| Case | Arm | Verdict / caught | Drove search | No code edit | Skill loaded |
|---|---|---|---|---|---|
| independent ("verify it independently, give a verdict") | j-verify | 1/3 | 0/3 | 3/3 | 2/3 |
| independent | none | 3/3 | 1/3 | 3/3 | n/a |
| author ("check your change is done") | j-verify | 3/3 | 3/3 | n/a | 0/3 |
| author | none | 3/3 | 1/3 | n/a | n/a |

- The pre-agreed drop rule fired: the author's own check without the skill caught the regression 3/3, mostly by reading `src/store.js` in the diff; the seeded break was visible in the code.
- j-verify did worse on the verdict: its base-and-head setup (`git worktree`/`git archive` into `$TMPDIR`, `mktemp`) failed in the sandbox in 2 of 3 runs; one run returned INCONCLUSIVE (honest, graded fail), one read the code and said do not merge without loading the skill (graded fail), one returned `VERIFY: FAIL` with base and head evidence.
- Cost about $1.08.
