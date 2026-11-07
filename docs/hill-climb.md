# Hill-climb loop

1. Select one observed failure or cost problem from the public development set. Write a falsifiable hypothesis and choose the primary outcome before editing the skill.
2. Freeze the starting jstack commit, evaluation commit, case IDs, model/host settings, budget, trial count, and grader version. Record the baseline and candidate conditions. Keep project and host instructions identical.
3. Make one coherent skill change. Commit it in jstack; pin that revision here. Use isolated fresh workspaces for paired trials and randomize condition order.
4. Grade actual outputs and resulting state. Record every planned trial, including failures, timeouts, interventions, and retries. Mark infrastructure failures separately. Check regressions across related skills and pack discovery, not only the targeted case.
5. Accept a candidate only when it improves the chosen outcome or gives equivalent quality at lower cost, introduces no critical failure, and satisfies the protocol's release gates. Report ties and inconclusive results. Reject a patch whose only improvement is a grader loophole.
6. Save an experiment record with hypothesis, both skill revisions, evaluation revision, case IDs, results, artifact hashes, and accept/reject/inconclusive rationale. An accepted development candidate is not automatically a release.
7. Run a frozen confirmation set outside the tuning loop before making generalization claims. Make release changes only through the usual authorized review process.

Do not lower quality to improve speed, use extra tools only for the candidate, or compare a fresh candidate with an easier baseline fixture. If the task or grader was wrong, repair and version it, then rerun all matched conditions.

## Holdout boundary

No holdout set currently exists. Reserve distinct task families or fixture variants, with separately maintained grader material, before tuning. Keep them in private evaluator storage or an independently controlled evaluation service. A directory called holdout in this public repository is not hidden.

The evaluated agent receives only its task and allowed fixtures, never grading keys or result expectations. Restrict workspace and tool access accordingly; merely asking it not to read a grader is insufficient isolation.

Release holdout results sparingly. Once inspected and used to revise a skill, that case becomes development/regression material. Repeatedly selecting patches on the same confirmation set turns it into another hill-climb target.
