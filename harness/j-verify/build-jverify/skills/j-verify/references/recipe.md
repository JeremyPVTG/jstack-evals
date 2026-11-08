# The repository's verify recipe

A project skill named `verify` that drives this repository's app the way a user does. It is read cold, mid-task, by an agent that has never seen the app, so every step is a real command or selector from this repo, never a placeholder. Claude Code (2.1.286 and later) runs a project skill named `verify` before each commit except docs-only or tests-only changes, so keep each drive fast enough to bear that, and put slow journeys behind a feature file the agent reads only when the change touches it.

## Find out from the repo, not the owner

- **Surface:** what a user touches (web UI, CLI, API, worker, library). Pick the primary one; note the rest.
- **Run:** the repo's own dev command (package scripts, Makefile, README), ports, environment variables, seed data, auth.
- **Drive:** existing harnesses first (Playwright specs, CLI fixtures, curl-able routes); only then a generic one: a browser for web, a PTY or tmux session for CLI, HTTP for services.
- **Observe:** screenshots, transcripts, response bodies, logs, exit codes, database rows, files written.
- **Isolate:** can a second instance run beside the owner's (ports, data directories)? If not, the recipe refuses to drive a shared instance.

Ask the owner only what the repo cannot tell you (a test account, which seed data is safe). If the checkout does not start as is, fix that or report it before writing the recipe.

## Sections of `verify/SKILL.md`

Frontmatter: `name: verify` and a description naming the app, its surface and when to use it.

- **Launch:** the command that starts the app for verification from an empty data directory, including migrations and seed data, and how to tell it is usable (not just that a port answers). For a short-lived CLI: build once, run each drive in its own session.
- **Doctor:** one read-only check that this instance is worth driving: process up, the build you just made, port owned by this run, auth valid.
- **Drive:** the harness recipe with real selectors, commands and routes. Prefer stable handles (ARIA labels, data attributes, route paths, prompt strings) over coordinates.
- **Evidence:** what to capture and where. Exercise the real user path, not internal setters or test-only endpoints; capture the action and the resulting state; check side effects (rows, files, messages) as well as the screen; mock only at a boundary production already isolates. A dry-run or test mode is checked by observing what it really skips.
- **Cleanup:** stop what this run started (never kill by process name) and remove scratch state, never the evidence.
- **Features:** `features/<feature>.md`, one per user-facing feature (start with the 3 to 5 the change touches or that matter most): how a user reaches it, how to drive it, the observable end state that proves it works, and gotchas. If seed data lacks a precondition, the journey fails and the gotcha says why; never weaken the journey.

## Prove it

Run the recipe once end to end (launch, doctor, drive one feature, capture evidence, clean up) and confirm the evidence survives cleanup. Fix and rerun until it does, cleaning up after every failed attempt. If you proved it somewhere other than its real target (a container instead of the runner), list what the stand-in did that the target will not.

Keep the recipe in sync: when a change adds or alters a user-facing feature, update its feature file in the same change.
