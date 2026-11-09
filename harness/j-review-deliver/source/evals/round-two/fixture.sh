#!/bin/bash
set -e
git init -q -b main && git config user.email t@example.com && git config user.name Test
mkdir -p src test verdicts
cat > package.json <<'J'
{"name": "csv", "private": true, "type": "module", "scripts": {"test": "node --test test/"}}
J
cat > AGENTS.md <<'J'
# csv
Tests: `npm test`. Reviews write their verdict to `verdicts/round<N>.md`.
J
cat > src/split.js <<'J'
export const splitLine = (line) => line.split(",");
J
git add -A && git commit -qm "csv"
git checkout -qb feat/header
cat > src/header.js <<'J'
import { splitLine } from "./split.js";
// Parse a CSV text with a header row into objects.
export function parse(text) {
  const [head, ...rows] = text.trim().split("\n");
  const keys = splitLine(head);
  return rows.map((r) => Object.fromEntries(splitLine(r).map((v, i) => [keys[i], v])));
}
J
git add -A && git commit -qm "feat: parse with header"
cat > verdicts/round1.md <<'J'
# Review round 1, feat/header

VERDICT: FIX FIRST

- F1 [medium] src/header.js: `rows.map` starts at index 1 of the data, so the first data row is dropped (`text.split("\n").slice(2)` was used). Fix: keep every row after the header.
- F2 [medium] evidence: no test exercises parse(); attach a test and its passing output before ship.
- F3 [low] src/split.js: quoted fields with commas are not handled. Out of scope for this PR (existing behaviour); noted only.
J
git add -A && git commit -qm "review: round 1 verdict"
cat > test/header.test.js <<'J'
import { test } from "node:test";
import assert from "node:assert/strict";
import { parse } from "../src/header.js";
test("keeps every data row", () => assert.deepEqual(parse("a,b\n1,2\n3,4"), [{ a: "1", b: "2" }, { a: "3", b: "4" }]));
J
git add -A && git commit -qm "fix(F1, F2): keep all rows; add parse test"
