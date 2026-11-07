# Evaluating jstack

Status: evaluation design, not benchmark results. Initial model trials are not yet run.

## Decision

Keep a skill when it helps complete realistic work reliably, with acceptable cost and interruption. Evaluate both the individual skill and the assembled stack. Do not produce one composite score: it can hide critical failures and turn subjective weighting into a ranking.

## Comparisons

Use the same model version, reasoning setting, host version, tools, project rules, starting artifacts, and budget for each matched trial. Start fresh sessions and isolated fixture copies. Randomize execution order so time or ordering does not consistently favor one variant.

1. Baseline: no added jstack or predecessor skills; retain identical required host and project instructions.
2. Previous: the relevant existing personal skill, snapshotted before changes.
3. Candidate: the pinned jstack revision and selected pack.

For a new skill without a comparable predecessor, mark Previous as not applicable and use a two-condition comparison. Do not manufacture a predecessor or count duplicate baseline runs as an independent condition.

If the host cannot exclude globally installed skills from the baseline, mark it contaminated and do not describe it as a no-skill comparison. Record exact skill content hashes and actual tool availability. Do not assume provider-specific sessions are identical.

Compare an upstream only for a capability it actually supports, with its required dependencies and equivalent task authority. Do not benchmark an incomplete installation, silently disable its essential workflow, or generalize results to the whole upstream collection.

## Four separate suites

### 1. Package integrity

Run package validation and installer tests on every relevant change. Check metadata, references, index freshness, pack membership, dry-run non-mutation, idempotence, backups, rollback, and preservation of subsequent user changes. These results say nothing about model quality.

### 2. Discovery

Use natural user requests without a skill name, path, or reminder. A fresh session sees only the normal installed metadata or the host's supported INDEX mechanism. Capture actual skill/reference loads from the tool trace; a model saying it used a skill is insufficient evidence.

Start with 28 prompts: 16 intended core-skill requests (four per skill), six close negatives, and six unrelated tasks. Record the allowed skill set per case; multiple routes may be valid. Report selection precision, recall, and unnecessary loads separately. An empty discovery selection can be correct for ordinary tasks.

Test the core pack first, then core alongside the selected upstream configuration. Report collisions, unnecessary loading, and whether competing workflows ran. Explicit-only upstream skills are tested with their intended invocation, not penalized for declining automatic discovery.

If the host does not expose load events, report discovery as unobservable; do not infer a pass from output quality.

### 3. Task outcomes

Explicitly load the relevant skill to isolate its behavior from discovery. Use the 15 case specifications in suites/development.json, with executable fixtures and hidden grading material prepared before a scored run. Each core skill gets one straightforward case, one difficult case, and one boundary case. Add one maintainer case and two multi-skill cases.

The agent receives the task, normal artifacts, available tool contracts, and allowed effects. The grader alone sees the expected outcomes, injected defects, and assertions. No live credentials, real messages, real merges, or production changes are needed: use a local Git remote and recorded or simulated provider responses. Simulations must disclose what they do not cover.

Check task completion as well as violations. An agent that avoids all actions fails a case requiring an authorized fix. Asking a question is correct when information is required; unnecessary questions count as interruptions. For interactive cases use the same scripted user answers across variants.

### 4. Host integration

Verify fresh-session discovery, one representative task, and installation removal on each host claimed as supported. Start with Claude Code and Codex. Record host/provider/model version, actual directory read, invocation path, tool availability, and date. T3 results name its provider as well as its host. Cursor and Hermes remain unverified until run.

A native host test is separate from a simulated behavior test. Passing one does not certify the other.

## Grading

Use deterministic graders first: final file and Git state, executable behavioral tests, fake-service state, attempted calls, protected-file hashes, and forbidden effects. A blocked unauthorized attempt counts as a violation attempt even if host enforcement prevents the effect.

For findings, map each actionable claim to the fixture's known defects and adjudicate unexpected but valid defects rather than marking them false automatically. Include a clean diff so finding nothing can be correct. Do not reward verbosity or a prescribed report format.

Use blinded pairwise assessment for evidence sufficiency, actionability, and material uncertainty when mechanical grading is insufficient. Shuffle A/B labels; hide author, model, and condition. Have the assessor cite supporting artifacts. Human-review disagreements and consequential verdicts. The candidate must not grade its own run. Use an independent evaluator when available and authorized; otherwise record human grading rather than inventing automation.

## Measurements

Report per case and suite:

- Task success: all required outcome assertions satisfied.
- Critical failures: destructive unauthorized actions or attempts, lost collaborator work, secret disclosure, fabricated execution evidence, or unsupported merge/deploy/completion claims.
- Review quality: consequential defects found, missed, and unsupported actionable findings.
- Friction: unnecessary clarification rounds and human interventions.
- Cost: input/output tokens including tool and child usage where observable, provider cost if known, tool calls, wall time, retries, and timeouts. Unknown means null, not zero.
- Evidence: artifact paths, sanitized tool trace, model/host settings, fixture and skill revisions, grader version.

Report infrastructure failure separately, retaining its receipt. Retry only under a predeclared infrastructure rule and show both attempts. A task-driven timeout is a task failure. A host restriction is part of that tested integration's result, not proof the skill is universally incapable.

## First benchmark and budget

Prepare two development fixtures per skill initially: eight core tasks, two trials per variant, three variants = up to 48 agent task runs on one chosen primary model/host. Snapshot predecessor skills and prepare artifacts before dispatch. Do not start paid model runs just to edit this protocol.

After the pilot, freeze all 15 cases and grading assertions for a release comparison. Use three trials per case and variant: up to 135 task runs on the primary configuration. The pilot is for fixing the harness, not a public quality claim. Run discovery separately and budget it explicitly. An isolated discovery run with only a catalog may be cheaper but cannot certify native host discovery.

Then confirm the candidate on a second model/host and run matched baselines there before making cross-model improvement claims. If the cost is disproportionate, publish a narrower result with its limitation instead of buying a larger headline.

Reserve separate holdout fixture variants before editing from evaluation feedback. Keep grading material outside agent-readable workspaces. If the author tunes against a public case, classify it as regression coverage rather than unseen generalization. Never call familiar regression cases a hidden benchmark.

## Release gates

These are initial engineering gates, not statistical proof of superiority:

1. Package checks and installer tests pass.
2. No observed critical failure in the release suite; a failure blocks promotion pending repair and targeted plus regression re-evaluation.
3. Every case succeeds in at least two of three trials, at least 90% of all task trials succeed, and no previously reliable critical case regresses. Inspect counts, not rounded percentages.
4. Discovery precision and recall are each at least 90% on this small set, with zero competing orchestration launches. Report denominators and every miss. Host support requires its fresh-session checks.
5. Candidate demonstrates a useful tradeoff against baseline and predecessor. If costs increase by more than 25% without additional task successes or fewer material errors, keep the simpler version or document why the extra cost is justified. The 25% band is a provisional review trigger, not a scientific constant.

Do not claim a significant win from a small sample. Publish case-level paired differences, counts, and uncertainty. Mark ties and inconclusive results honestly. Preserve critical improvements even when aggregate success is tied; explain the specific failure avoided.

## Maintenance

Run deterministic checks on ordinary PRs. Re-run affected behavioral cases for instruction changes; run the full release suite for pack composition, routing, or major workflow changes. A model or host upgrade requires targeted compatibility checks before carrying forward old claims. Convert real sanitized failures into regression cases. Revisit retained skills if the unassisted model catches up.

## Public reporting

Publish the task, fixtures or a reproducible equivalent, exact tested versions, method, complete results including losses, and limitations. Private logs and grading material remain outside installed skill folders. No leaderboard or SOTA label is required.

Source guidance: [Agent Skills: evaluating output quality](https://agentskills.io/skill-creation/evaluating-skills) describes matched baseline runs and fresh contexts. [Anthropic: agent evaluations](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) distinguishes trials, graders, traces, and actual environment outcomes. The case counts, thresholds, and budget above are jstack's proposed engineering choices.
