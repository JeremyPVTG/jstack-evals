# jstack commit IDs before and after 2026-11-21

On 2026-11-21 jstack's history was rewritten to remove AI attribution trailers from commit messages. File contents and trees did not change; commit IDs did. READMEs, the climb log and the lock files in this repository use the new IDs. Recorded run logs and result file names under `harness/*/results/` keep the IDs they were written with; use this table to find the matching commit.

48 of 51 public commits changed ID; the earlier ones had no trailers and kept theirs.

| Old | New | Subject |
|---|---|---|
| f6f4ac7 | 956dda8 | Rebuild j-research around landscape, scope, and a compounding vault; add j-scope |
| aac82be | e8843a6 | Prune j-research after dogfooding; add vault lint script; X via browser cookies |
| f30eeab | 2a69bbc | Add vault sync script with iCloud eviction and mass-deletion guards |
| 763fc86 | dd7d024 | Add jvault: personal remote MCP server for the research vault and skills |
| 8769869 | 468dad7 | j-research: use the vault MCP server when available, local folder otherwise |
| 5ed47f0 | d3c6801 | sources: note X cookie setup can need a re-run |
| c6324a6 | 4e21c0e | j-bookmarks: weekly X bookmark triage into the research vault |
| d378ae9 | 365c259 | j-bookmarks: launchd cannot read browser cookies on macOS; say how to schedule |
| f468c7b | 71312e3 | j-research: fan out lanes, coverage line, trim; adopt Skill-Size and Evidence trailers |
| 9a1e5f6 | d0c1723 | j-scope: status quo, prior decisions, falsifiable positions, external proof |
| 6592ca8 | 06237a1 | j-bookmarks: learn from owner corrections, reassign rows, flag aging queue |
| 7ac8f5b | 509cbe2 | j-research: route search lanes across Exa, Tavily and Firecrawl |
| a9437b7 | ff5cdb7 | j-research sources: Reddit cannot be read by Firecrawl or Exa fetch |
| a4c547a | 13e1bc2 | j-research: experiment lane, council pointer, spend, typed links, stale flags |
| 1fa56a6 | 6a0d4d8 | j-research: description that triggers on research questions |
| dcb2cd8 | b2e2044 | vault: union-merge index and log; sync logs why git failed |
| 64bb066 | 77e6d0c | jvault: semantic search through Cloudflare AI Search |
| c94d800 | e095936 | j-research: lane brief for subagents |
| cd94fee | 285ef52 | j-research: fire on build and reliance questions; visible evidence status; one-source lookups |
| c27c3d0 | 7b1245f | j-research: name vendor, blog and forum claims in the description |
| c10c566 | 1aad68d | j-research: every-run checklist; reuse a fresh vault page without searching the web |
| 64c86a5 | 10b4f65 | j-research: research_hook.py, a UserPromptSubmit hook that reminds the agent to use the skill |
| a7f940a | 62cdced | research_hook: read EVAL_TYPESAFE_API_KEY, the only form plugin evals pass through |
| b58df5c | ec280b6 | j-research: open vault pages before relying on them |
| d93de69 | ba87dac | j-research: open a vault page with the read tool before citing it |
| 92b7492 | 52d77da | jvault: stamp captures and log lines in the owner's time zone |
| 7d928c2 | 919268b | research_hook: skip host-delivered task results and notices |
| 2ad54c7 | 75be255 | j-research: write the cost cap without $2, which Claude Code read as an argument |
| 2e993ad | 60e986e | vault lint: warn when a scope decision page lacks j-scope's template sections |
| e516f35 | db762cf | j-scope: decision template and an 'Against the recommendation' line |
| dafe3ae | 2da38b1 | j-daily: collect a day's work from the vault, PRs, commits and T3 (#1) |
| 045cb6a | 7b0011c | j-build: staged build workflow, generic, sized to the task |
| 9a23004 | 9055a84 | j-build: fold in the HerdSense pilot's feedback |
| 3231f63 | a04a372 | j-daily: turn a day's record into a draft daily-log PR with questions for the owner (#2) |
| 2fb657c | f8eb93f | j-build: fold in pilot 2 (HerdSense issue 588) feedback |
| ecdddbb | 4457f16 | j-build: council round 1 fixes |
| d654e29 | 090fbac | j-build: council round 2 fixes |
| cceb4f8 | a3fe000 | tests: j-build review verdicts; j-research hook firing log |
| 8f4b99d | a612abf | j-build: done-criteria in the brief, a verdict per criterion in Verify |
| 811bc70 | 0367eb5 | hosts: pin T3 Code reference to 09a54f0 |
| 35ed5a8 | 848e0a2 | j-review, j-deliver: rebuild to replace the pr-* skills (#3) |
| 88dcdab | b9fcfcb | docs: dated measurement plans for j-evidence, j-skill-audit and j-bookmarks (#4) |
| d77739a | 83f8d0f | Revise README for clarity and consistency |
| 98c7a51 | a9180e4 | Audit fixes: hook on Python 3.9, jvault path check, j-daily private-repo check, docs (#5) |
| 08668be | ac57fcb | feat(j-build): require inspectable demonstration proof |
| 296a501 | 0acc16a | feat(j-build): require inspectable demonstration proof (#6) |
| 367fcc2 | db1c979 | Link the published evals and drop casts and intersections in vault-server |
| 9290b7f | d47e326 | Add MIT licence with notices for adapted gstack, Matt Pocock and pstack material |
