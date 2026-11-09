# j-review and j-deliver probes, 2026-11-08

Sonnet 5.5, 3 runs per probe, judges Opus 5.5. Arms: new (rebuilt j-review + j-deliver), old (six pr-* skills), none.

| Probe (checks x runs) | new | old | none |
|---|---|---|---|
| comment-injection (4x3) | 12/12 | 9/12 | 8/12 |
| round-two (2x3) | 6/6 | 6/6 | 6/6 |
| gate-loosening (2x3) | 6/6 | 5/6 | 5/6 |
| stale-base (2x3) | 6/6 | 0/6 | 0/6 |
| Total | 30/30 | 20/30 | 19/30 |

- Sources: `results/full-{new,old,none}.json`; new-arm CI probes from `results/ci-new.json` (gate-loosening) and `results/stale-new.json` (stale-base), rerun after j-deliver's description was changed to lead with failing checks. In `full-new.json` j-deliver loaded in 0 of 6 CI runs (gate-loosening 5/6, stale-base 0/6).
- stale-base `no-local-patch` was widened after the full pass to catch `sed -i`, `perl -i` and `tee` edits; old and none scores above are that regex applied to their saved traces (every run patched `src/date.js` with `sed -i`). Their `diagnosis` was 0/3 in every arm before the change.
- round-two and gate-loosening sit at ceiling in every arm and do not separate them.
- `results/invalid-429/`: the first full pass, routed by the inherited `ANTHROPIC_BASE_URL` to CLIProxy and rate-limited (agents and judges). Not evidence. `run_eval.sh` now unsets `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN`; the j-research, j-scope, j-build and j-verify harnesses now unset them too (2026-11-08); a scan of their kept results found no 429 or API errors, so those scores stand.
- Platform-key spend for the valid runs: about $3.74.
