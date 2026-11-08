---
description: "Safety check on KestrelDB 4.3 online shard split where vendor blog and Reddit claim zero write pauses, but official 4.3 docs and issue #8912 show cutover locks and aborted 2PC transactions."
tags: [heldout2]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, AskUserQuestion, TodoWrite]
---

Can we rely on KestrelDB 4.3's online shard split to rebalance our hot orders table during peak checkout traffic without pausing writes or dropping cross-shard transactions?
