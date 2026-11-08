---
description: "An obvious one-line bug: small path, fresh test run, short report."
tags: [probe]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite, Edit, Write, Bash]
---

Use the j-build skill (or the staged build workflow skill if that is what is installed). Bug: `average([2, 4])` returns 6 instead of 3. Fix it.
