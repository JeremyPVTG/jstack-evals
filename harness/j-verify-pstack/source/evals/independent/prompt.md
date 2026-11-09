---
description: "PR adds --tag and its tests pass, but the storage change breaks search, a mapped feature the diff touches. Right verdict: FAIL on the search regression."
tags: [probe]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite, Edit, Write, Bash]
---

PR #12 merges branch `feat/tags` into `main` (both are on `origin`; `feat/tags` is checked out). Its description is in `PR.md` and says the change is done and verified. Before it merges, verify it independently and give a verdict. Do not change the code.
