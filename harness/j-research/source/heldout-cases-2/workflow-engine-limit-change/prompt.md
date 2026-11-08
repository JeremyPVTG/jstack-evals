---
description: "Choice between FluxStep and TempoPipe where FluxStep 3.4 raised its payload and sleep limits last week, with stale vault and FluxStep 3.3 docs decoys."
tags: [heldout2]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, AskUserQuestion, TodoWrite]
---

Should we pick FluxStep or TempoPipe for our document-ingestion pipeline? Each step passes an 8 MB parsed OCR payload and workflows can pause for up to 45 days waiting on compliance sign-off.
