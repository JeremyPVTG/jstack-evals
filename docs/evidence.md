# Evidence contract

A published experiment is an auditable observation under stated conditions, not proof of universal superiority.

Each experiment must identify:

- Exact jstack baseline and candidate commits, this evaluation repository's commit, suite and grader revisions, and a run ID.
- Model/provider and version, host and version, reasoning settings, tool contracts, project instructions, skill-loading mode, and access boundary.
- Planned case IDs, split (development or separately held-out), trial counts, stopping/retry rule, and budget fixed before execution.
- Per-trial observed outcomes, assertion results with evidence locations, critical attempts/effects, interventions, time, tokens, cost when available, and infrastructure failures. Missing values are null.
- Fixture hashes, sanitized tool-call transcripts, resulting artifact hashes, and grader output. Do not publish private source text or hidden reasoning traces. Preserve original private evidence outside the public repository where appropriate.
- Paired differences, complete denominators, limitations, and the final accept/reject/inconclusive decision. Include losses and regressions.

Raw private logs and active workspaces stay outside Git. Publish reviewed, sanitized evidence bundles and a content-hash manifest only after execution. No sample result here may be presented as an actual run.

A repeatable run command and pinned environment will be required when agent adapters are implemented. They do not exist yet. Manual trials may be recorded honestly, but cannot be called automated or independently reproduced until their execution evidence supports that claim.
