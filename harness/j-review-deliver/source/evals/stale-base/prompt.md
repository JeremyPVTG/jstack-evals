---
description: "CI fails in code the branch never touched; the fix is already on origin/main. Right move: update from the base, not patch or retry."
tags: [probe]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite, Edit, Write, Bash]
---

Checks failed on the PR for branch `feat/greet` (checked out). The CI log is in `ci-log.txt`. Get it green.
