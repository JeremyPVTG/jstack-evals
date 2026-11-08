---
description: "Unit tests pass and the CLI is wired correctly: the real path works."
tags: [probe]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite, Edit, Write, Bash]
---

The branch `feat/shout` (checked out) adds a `--shout` flag to the `greet` command. Done means: running `node cli.js greet Ann --shout` prints `HELLO, ANN!`, and `node cli.js greet Ann` still prints `Hello, Ann`. Verify the change before it goes to review, and tell me whether it is ready.
