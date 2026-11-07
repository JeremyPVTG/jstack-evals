# Working on jstack-evals

This repository evaluates the separate jstack repository. Do not install the skills or change a user's agent configuration to run a fixture. Use isolated temporary workspaces and local fake services.

Public development cases are tuning material. Held-out cases must remain outside evaluated agents' readable workspaces. A public repository is not a secrecy boundary. Do not claim holdout coverage until an independent set exists and has actually been run.

Pin both repository revisions, model and host versions, tools, and budget. Preserve failures and retries. Do not edit graders or thresholds to turn a candidate's existing run into a win; version a new experiment instead.

Run `python3 -m unittest discover -s tests` for pinning-tool changes. No dependency installation or paid agent runs are necessary for metadata tooling tests. Do not report metadata validation as model performance.
