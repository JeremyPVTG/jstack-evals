---
name: j-verify
description: Use this skill to prove a code change works by running it on the real path (the app, CLI, API or job a user touches) and checking each done-criterion with evidence, returning VERIFIED, NOT VERIFIED or INCONCLUSIVE per criterion at a named commit. It writes or updates the repository's own `verify` recipe so later runs and pre-commit checks reuse it. Use after building and reviewing a change, before a council or merge, or when asked to "verify", "prove it works" or "show it working". Not for reviewing code style or for open research questions.
---

# Verify

Prove the change does what the brief says on the real path, and leave evidence another agent or the council can check without rerunning anything. A claim is not evidence: "tests pass", "it compiles", an HTTP 200, a merged PR or an agent saying so prove nothing on their own.

Every run:

1. Pin the commit you verify (`git rev-parse HEAD`, and say if the tree is dirty). Evidence from another commit does not count; a change after verification means verifying again.
2. Never weaken a check, a journey, a test or its data to get a pass. If a criterion cannot pass honestly, it is NOT VERIFIED.
3. What you could not run is INCONCLUSIVE, never VERIFIED. Say what it needs (a GPU, a credential, a service, the owner).

## 1. Criteria

Take the done-criteria from the brief, the j-scope decision page's "Goal and proof", or the issue. Each must be observable: what a user does and what they then see or what state changes. Rewrite vague ones as observable checks and list them before running anything; when you had to invent one, mark it as yours. One criterion per behaviour the change adds or fixes, plus one for the main path the change could break.

## 2. Recipe

Use the repository's verify recipe: a skill named `verify` (for Claude Code, `.claude/skills/verify/SKILL.md`; the build file may name another place). If there is none, or it does not cover what this change touches, write or extend it first. [How to write the recipe](references/recipe.md). A recipe that has never run is a draft: run it before relying on it.

## 3. Run

For each criterion: launch, check the instance is the one you built, drive the real user path, capture the action and the resulting state, then clean up what you started. Prefer the strongest evidence you can get:

1. Reproduced in the running app: a screenshot next to the expected state, a terminal transcript, a response body, the row or file that changed.
2. Ran it: a command and its full output with exit status.
3. A test that fails when the change is reverted and passes with it (show both runs).
4. Read the code path (file:line). This alone never makes a criterion VERIFIED.

When a check fails, suspect how you observed it before suspecting the change: confirm the harness, the instance and the data, then rerun once.

## 4. Verdicts

Per criterion: **VERIFIED** (evidence at levels 1 to 3 at the pinned commit), **NOT VERIFIED** (it ran and the behaviour is wrong or missing), **INCONCLUSIVE** (it could not run, or the evidence is ambiguous). The overall verdict is the weakest one.

## 5. Evidence pack

Write the pack where the build file says, else `.verify/<commit>/` (gitignored): `verdicts.md` with one line per criterion (criterion, verdict, evidence path, one-line reason) plus the screenshots, transcripts and outputs it cites. Cleanup never deletes the pack. The council and reviewers read this pack with the diff; a fix they trigger means verifying again.

## Report

Lead with the overall verdict and the commit. Then each criterion with its verdict and evidence path, what was INCONCLUSIVE and what it needs, and whether the recipe changed. End with the owner's next actions as a numbered list, or "Nothing needed from you".

Recipe approach adapted from pstack's [create-verification-skill](https://github.com/cursor/plugins/tree/main/pstack/skills/create-verification-skill); evidence levels from pstack blast-radius; fresh-evidence rule from superpowers [verification-before-completion](https://github.com/obra/superpowers/tree/main/skills/verification-before-completion).
