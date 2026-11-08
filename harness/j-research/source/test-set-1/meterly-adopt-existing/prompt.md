---
description: "Choose an existing billing product instead of building a commodity pipeline."
tags: [test1]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, AskUserQuestion, TodoWrite]
---

We need per-customer hard usage caps and monthly Stripe invoices by January. Should we build the billing service ourselves, or is there an off-the-shelf path? We ingest about 150 events/second today.
