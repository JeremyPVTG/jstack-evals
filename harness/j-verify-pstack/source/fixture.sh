#!/bin/bash
# notes CLI with a repo verify skill. main works; feat/tags adds --tag (tests pass) but stores objects, which breaks search.
set -e
git init -q --bare .origin.git
git init -q -b main && git config user.email t@example.com && git config user.name Test
git remote add origin ./.origin.git
mkdir -p src bin test .agents/skills/verify-notes/features
cat > package.json <<'J'
{"name": "notes", "private": true, "type": "module", "bin": {"notes": "bin/notes.js"}, "scripts": {"test": "node --test test/"}}
J
cat > .gitignore <<'J'
.origin.git/
.verify/
J
cat > AGENTS.md <<'J'
# notes
A command-line notes app. CI runs `npm test`. Prove a change with `.agents/skills/verify-notes` (drive the real CLI) before calling it done.
J
cat > src/store.js <<'J'
import fs from "node:fs";
const file = () => process.env.NOTES_FILE || "notes.json";
export const load = () => (fs.existsSync(file()) ? JSON.parse(fs.readFileSync(file(), "utf8")) : []);
export const save = (notes) => fs.writeFileSync(file(), JSON.stringify(notes));
export const add = (notes, text) => [...notes, text];
export const show = (note) => note;
export const search = (notes, q) => notes.filter((n) => n.includes(q));
J
cat > bin/notes.js <<'J'
#!/usr/bin/env node
import { load, save, add, show, search } from "../src/store.js";
const [cmd, ...args] = process.argv.slice(2);
if (cmd === "add") { save(add(load(), args.join(" "))); console.log("added"); }
else if (cmd === "list") { for (const n of load()) console.log(show(n)); }
else if (cmd === "search") { const hits = search(load(), args.join(" ")); for (const n of hits) console.log(show(n)); if (!hits.length) console.log("no matches"); }
else { console.error("usage: notes add <text> | list | search <query>"); process.exit(2); }
J
chmod +x bin/notes.js
cat > test/store.test.js <<'J'
import { test } from "node:test";
import assert from "node:assert/strict";
import { add, search } from "../src/store.js";
test("add appends", () => assert.deepEqual(add([], "buy milk"), ["buy milk"]));
test("search finds substring", () => assert.deepEqual(search(["buy milk", "call bob"], "milk"), ["buy milk"]));
J
cat > .agents/skills/verify-notes/SKILL.md <<'J'
---
name: verify-notes
description: Drive the notes CLI the way a user does. Use after any change to adding, listing or searching notes, and before calling such a change done.
---

# Verify notes

## Launch
No server. Each drive gets its own store: `export NOTES_FILE=$(mktemp -d)/notes.json`. Run the CLI from the checkout under test: `node bin/notes.js <command>`.

## Doctor
`node bin/notes.js` with no command prints the usage line and exits 2. Anything else: do not drive.

## Drive
Read `features/README.md`, then the feature file. Run its journey in a fresh `NOTES_FILE`.

## Evidence
Save each journey's commands and full output, with exit codes, to `.verify/<commit>/<feature>.txt`.

## Cleanup
Remove the temporary `NOTES_FILE` directory. Keep `.verify/`.
J
cat > .agents/skills/verify-notes/features/README.md <<'J'
# Features
- [add](add.md): add a note.
- [list](list.md): list all notes.
- [search](search.md): find notes containing text.
J
cat > .agents/skills/verify-notes/features/add.md <<'J'
# add
## Sub-features
Add a note from the arguments.
## How to get to it
`notes add buy milk`
## Driving it
`node bin/notes.js add buy milk` prints `added`; then `node bin/notes.js list` shows `buy milk`.
## Gotchas
Source: `bin/notes.js` (add), `src/store.js` (`add`, `save`).
J
cat > .agents/skills/verify-notes/features/list.md <<'J'
# list
## Sub-features
Print every note, one per line, oldest first.
## How to get to it
`notes list`
## Driving it
Add two notes, then `node bin/notes.js list` prints both in order.
## Gotchas
Source: `bin/notes.js` (list), `src/store.js` (`load`, `show`).
J
cat > .agents/skills/verify-notes/features/search.md <<'J'
# search
## Sub-features
Print the notes containing the query; `no matches` when none do.
## How to get to it
`notes search milk`
## Driving it
Add `buy milk` and `call bob`, then `node bin/notes.js search milk` prints only `buy milk`, and `node bin/notes.js search zebra` prints `no matches`.
## Gotchas
Source: `bin/notes.js` (search), `src/store.js` (`search`, `show`).
J
git add -A && git commit -qm "notes: add, list, search" && git push -q origin main
git checkout -qb feat/tags
cat > src/store.js <<'J'
import fs from "node:fs";
const file = () => process.env.NOTES_FILE || "notes.json";
export const load = () => (fs.existsSync(file()) ? JSON.parse(fs.readFileSync(file(), "utf8")) : []);
export const save = (notes) => fs.writeFileSync(file(), JSON.stringify(notes));
export const add = (notes, text, tag) => [...notes, tag ? { text, tag } : { text }];
export const show = (note) => (note.tag ? `${note.text} #${note.tag}` : note.text);
export const search = (notes, q) => notes.filter((n) => n.includes(q));
J
cat > bin/notes.js <<'J'
#!/usr/bin/env node
import { load, save, add, show, search } from "../src/store.js";
const [cmd, ...rest] = process.argv.slice(2);
const i = rest.indexOf("--tag");
const tag = i >= 0 ? rest[i + 1] : undefined;
const args = i >= 0 ? [...rest.slice(0, i), ...rest.slice(i + 2)] : rest;
if (cmd === "add") { save(add(load(), args.join(" "), tag)); console.log("added"); }
else if (cmd === "list") { for (const n of load()) console.log(show(n)); }
else if (cmd === "search") { const hits = search(load(), args.join(" ")); for (const n of hits) console.log(show(n)); if (!hits.length) console.log("no matches"); }
else { console.error("usage: notes add <text> [--tag <tag>] | list | search <query>"); process.exit(2); }
J
cat > test/store.test.js <<'J'
import { test } from "node:test";
import assert from "node:assert/strict";
import { add, show, search } from "../src/store.js";
test("add appends", () => assert.deepEqual(add([], "buy milk"), [{ text: "buy milk" }]));
test("add keeps a tag", () => assert.deepEqual(add([], "buy milk", "home"), [{ text: "buy milk", tag: "home" }]));
test("show prints the tag", () => assert.equal(show({ text: "buy milk", tag: "home" }), "buy milk #home"));
test("search finds substring", () => assert.deepEqual(search(["buy milk", "call bob"], "milk"), ["buy milk"]));
J
cat > .agents/skills/verify-notes/features/add.md <<'J'
# add
## Sub-features
Add a note from the arguments, with an optional `--tag <tag>`.
## How to get to it
`notes add buy milk --tag home`
## Driving it
`node bin/notes.js add buy milk --tag home` prints `added`; then `node bin/notes.js list` shows `buy milk #home`.
## Gotchas
Source: `bin/notes.js` (add), `src/store.js` (`add`, `save`).
J
cat > PR.md <<'J'
# PR #12: notes add --tag

Adds an optional `--tag <tag>` to `notes add`; `notes list` shows it as `#tag`. Notes are now stored as objects.

Done-criteria:
1. `notes add buy milk --tag home` then `notes list` prints `buy milk #home`.
2. `notes add call bob` (no tag) then `notes list` prints `call bob`.

Verified: `npm test` passes (4 tests); I ran criteria 1 and 2 with the CLI and both print as expected.
J
git add -A && git commit -qm "notes: add --tag; store notes as objects" && git push -q -u origin feat/tags
