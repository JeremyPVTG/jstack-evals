# jstack-evals

Reproducible evaluations and improvement experiments for jstack in T3 Code, across models. Maintained independently from the skills themselves.

This repository has two jobs: give each change a repeatable development target, and provide inspectable evidence for claims about the resulting stack. Public development scores alone do not prove generalization.

## Current state

15 public task specifications and nine routing sketches have been moved here. Executable task fixtures, graders, agent adapters, and held-out cases still need implementation. No model performance results have been published. Revision pinning has deterministic tests; that is tooling evidence only.

## Relationship to jstack

Keep sibling checkouts named jstack and jstack-evals. jstack owns skills and installation tests; this repository owns behavioral evaluation. Neither repository vendors the other. The exact subject revision is stored in subject.lock.json. GitHub remotes have not been configured yet.

```sh
python3 scripts/subject.py pin --repo ../jstack --output subject.lock.json
python3 scripts/subject.py verify --repo ../jstack --lock subject.lock.json
python3 -m unittest discover -s tests
```

Pin requires a clean committed subject and records its full commit, tree, and tracked file hashes. Verify fails when the subject changes or becomes dirty. Pinning refuses to overwrite an existing lock; create a new versioned lock for each experiment. Pins do not prove a test was run; each future run must additionally record this repository's clean commit and its own execution artifacts.

## Evaluate and improve

- [T3 model matrix](docs/t3-matrix.md): primary host, provider capability differences, and transfer gates.
- [Protocol](PROTOCOL.md): comparison conditions, scoring, budgets, and release gates.
- [Development suite](suites/development.json): visible task specifications for iteration.
- [Routing sketches](suites/routing-sketches.json): early selection examples, not a completed discovery suite.
- [Hill-climb rules](docs/hill-climb.md): experiment discipline and promotion.
- [Evidence contract](docs/evidence.md): what a published result must contain.
- [Status](STATUS.md): completed versus unexecuted work.

There is no aggregate SOTA score. Report task success, material failures, findings quality, interventions, time, and cost separately, with complete denominators and limitations.
