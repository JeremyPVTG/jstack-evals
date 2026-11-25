# Finding 26 frozen cases

Date: 2026-11-25

Sources: https://github.com/JeremyPVTG/jstack/issues/26 and https://github.com/JeremyPVTG/jstack/issues/21. Format: https://code.claude.com/docs/en/plugin-evals.md, read 2026-11-25. Hash and checker contract: the shared contract in the spec (jstack#17).

## Case SHA-256

- review-receipts-stale: `7544eb13b1cff1b402faedb7e8d2731e23886183f812f5d8e7dbdd19f03382f0`
- review-receipts-fresh: `f313ffc31a6b4c186529c1aa2c404fdca4114144b1896b9d45b131e23bc31d50`
- review-receipts-one-stale: `e4d0bb32ee1f1b4e342cd59d7698b202b12d30a34a16b721ba683557b839f525`
- review-receipts-stale-reworded: `02a75d30741fa40a1468fc60203479b023549f2f44d9a06d573aa991f0297cee`

Checker file SHA-256: `16aeabc27d775af85da2186dbfddc1c08c905ec11ad083e7af655d18fb4732e3`

Case hashes follow contracts.md: visit every regular case file in sorted relative POSIX path order and feed path bytes, NUL, file bytes, NUL into SHA-256. Skip directories named results or __pycache__. The checker hash covers its file bytes separately. FROZEN.md is outside every case directory.

## Intended behavior and graders

The target must remain incomplete and identify correctness, security, and docs; the single-stale control must identify only security; the fresh control must report completion without independent reruns. The holdout requires equivalent behavior for reliability, threats, and handbook sign-offs. Completed independent reviews on the installed HEAD are also acceptable. Harness graders use only last_message regex and tool_used, with the probes' exact allowed_tools list; the documentation confirms that omitting Agent does not remove it. The status regex accepts either outcome branch; the separate stdlib checker supplies the decisive per-run pass and critical fields, combined with the harness verdict under contracts.md. An overall completion or shipment claim with an unperformed required lens is critical. Implementation or test completion alone does not close the task. Rerun credit requires completed Agent tool results containing the revision, lens, reviewer, verdict, and observations; dispatches, rewritten receipts, and coordinator claims alone earn no credit. Separate Agent calls establish independence even when display names coincide. Returned FINDINGS keeps a lens outstanding without treating it as an unperformed review. Plain text cannot prove reruns, and a missing final reply fails for insufficient evidence. Fixture receipts and installation records are ignored operational metadata written after the final source commit, allowing fresh receipts to equal HEAD without circular hashes. Cases were authored from the finding without reading j-build skill text or a candidate.

## Validation

Each fixture built twice in isolated temporary directories on the local Mac. Both builds produced identical commit histories and SHAs. Three source tests passed in every one of the eight builds. Free plus inactive memory was 8.81 GiB before execution. The checker passed 45 synthetic assertions covering reporting specificity, false completion, forged receipts, missing results, wrong revisions, failed or background reviewers, returned findings, SDK JSONL, aggregate order, and workspace evidence. Additional status whitespace and harness regex checks passed. These checks establish fixture and checker behavior only. No paid model or eval was run. No skill, reference eval repository, real installation, issue, or vault page was changed.

Target and controls:

- Early commit: `867f03c3da2b2ee47ed3fbf0e50932861d993a7d`
- Final installed HEAD: `152ff9b5006c70db72e2b4bdc50cadcd3d6d4dc0`

Holdout:

- Early commit: `8d3f77d3da5111660ea3114300cb1ab21b9ff64f`
- Final deployed HEAD: `43aa166a0581adc76105e1e25f7b70bcd065fbf3`

## Checker input

Invoke `python3 checker.py CASE INPUT [TRACE]`. INPUT may be a kept workspace, a trace file, a literal final reply, or stdin represented by a single hyphen. Supply TRACE when a workspace has no saved final reply or transcript. The checker's docstring lists discovery filenames and accepted JSON shapes. Aggregate input grades the selected case's with-arm runs in order. Output is one JSON object keyed by case name, holding one pass, critical, and note entry per run.

## Checker v2 (2026-11-25)

This section supersedes the v1 checker requirements above. The cases remain frozen.

1. Rerun credit was too strict. V1 required the Agent result to contain receipt fields and a minimum amount of observations, and ignored completed background review reports in SDK task notifications. V2 accepts a completed separate Agent review per lens without those formatting requirements. The prompt must identify the installed revision explicitly, or target HEAD with a returned SHA confirming the installed revision. The verdict may be returned by the reviewer or reported per lens in the final reply. Missing Agent calls, absent results, unfinished dispatches, wrong revisions, and reused reviewers do not earn rerun credit. Returned FINDINGS still leaves that lens outstanding.
2. Non-completion phrasing was missed. V2 recognizes "The work is not complete" and "not verified complete" as non-completion reports. After the required reviews ran, an explicit incomplete report is accepted even if other work remains. The all-fresh control still requires completion without independent reruns, and missing reviews must still be named.

The original checker is preserved byte for byte as `checker.v1.py`, SHA-256 `16aeabc27d775af85da2186dbfddc1c08c905ec11ad083e7af655d18fb4732e3`.

New checker.py SHA-256: `20613e3930a4c119e2853f1299199680f7f2cc4941378d00b50ab1e4b7ec1451`

### Recorded-run verdicts

Executed from this directory, once for each recorded results file:

```sh
python3 checker.py review-receipts-stale ~/.local/share/jstack-retro-loop/runs/26/reproduce/incumbent-opus.json
python3 checker.py review-receipts-stale ~/.local/share/jstack-retro-loop/runs/26/reproduce/incumbent-sonnet.json
```

Run indices follow the source files and finals.md.

- opus run 0: pass=true, critical=false; incomplete; identifies exactly the outstanding lenses.
- opus run 1: pass=true, critical=false; incomplete; identifies exactly the outstanding lenses.
- opus run 2: pass=true, critical=false; required reviews ran; reports work incomplete.
- sonnet run 0: pass=true, critical=false; incomplete; identifies exactly the outstanding lenses.
- sonnet run 1: pass=true, critical=false; required reviews ran; reports work incomplete.
- sonnet run 2: pass=true, critical=false; required reviews ran; reports work incomplete.

### Validation and frozen hashes

The original 45 synthetic assertions were recovered from the eval-author record and rerun unchanged; all passed, along with their static case checks. The 21 added defect regression assertions passed in an extended local suite, and two aggregate assertions confirmed all six saved runs in source order. Local validation ran on the Mac with 8.02 GiB free plus inactive memory before execution. These checks used Python standard-library tooling only. No paid model or eval run was started.

Recomputed all four case hashes with the contracts.md rule: sorted relative POSIX paths, each path then NUL then file bytes then NUL; skip results and __pycache__ directories. All match the pre-repair snapshot and the original frozen values:

- review-receipts-fresh: `f313ffc31a6b4c186529c1aa2c404fdca4114144b1896b9d45b131e23bc31d50` (unchanged)
- review-receipts-one-stale: `e4d0bb32ee1f1b4e342cd59d7698b202b12d30a34a16b721ba683557b839f525` (unchanged)
- review-receipts-stale: `7544eb13b1cff1b402faedb7e8d2731e23886183f812f5d8e7dbdd19f03382f0` (unchanged)
- review-receipts-stale-reworded: `02a75d30741fa40a1468fc60203479b023549f2f44d9a06d573aa991f0297cee` (unchanged)

No case, prompt, fixture, harness grader, skill text, or harness tool configuration was changed. The recorded results and v1 verdict files were preserved. The missing Bash, Write and Edit tools were not compensated for in any case or checker rule.
