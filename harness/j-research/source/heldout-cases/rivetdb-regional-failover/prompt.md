---
description: "Recheck an expired medium-volatility note and distinguish a documented topology from inferred risk and missing measurements."
tags: [heldout]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, AskUserQuestion, TodoWrite]
---

For our order ledger on RivetDB 7.3, can I promise customers that losing a whole region loses zero acknowledged orders and restores service within 20 seconds at p99? We have one primary region and its cross-region replica. Give me a recommendation I can use in the launch review.
