# Core grader and fixture fixes (2026-11-08)

Under the hill-climb protocol's defect rule (shown from the spec or reality, recorded before regrading, applied to every variant).

## lookup-control: fixture contradicted reality

The frozen nodejs.org page said Node.js 24 was Active LTS on 2026-11-07. Under Node's release schedule, Node 24 entered Active LTS in October 2025 and moves to Maintenance a year later, when Node 26 (released April 2026) becomes Active LTS. Opus noticed the contradiction and wrote a longer, hedged answer, failing a check that combined correctness with length. Shown from reality, not from traces: the page and the schedule disagree.

Fix: the page now says Node.js 26 is Active LTS (v26.2.0, 2026-10-28), Node 24 and 22 are Maintenance LTS, Node 27 is Current. The answer grader checks correctness and the source only; brevity is a separate grader (`brevity.md`), reported on its own line.

## compile-into-vault: grader demanded what the skill excuses

`spend.md` required a `spend` field in the log call. The skill says to record approximate paid spend and the jvault tool says to omit it when there is none; every call in the eval is a free mock. Fix: `spend.md` removed. Stored scores are recomputed without it (it had weight 0.5); originals are kept in the results files.

Correction (2026-11-07, evening): the fixed page said Node.js 27 is Current and Node 26 entered Active LTS on 2026-10-20. The live release index (nodejs.org/dist/index.json, checked 2026-11-07) shows Node 27 only as v27.0.0-alpha and Node 26 entering Active LTS on 2026-10-28. Fixture corrected in every copy; the lookup grader checks only the Active LTS line, so scores are unaffected.
