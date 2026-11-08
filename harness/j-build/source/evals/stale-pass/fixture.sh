#!/bin/bash
set -e
git init -q && git config user.email t@example.com && git config user.name Test
mkdir -p src test
cat > package.json <<'J'
{"name": "calc", "private": true, "type": "module", "scripts": {"test": "node --test test/"}}
J
cat > AGENTS.md <<'J'
# calc
Tiny library. Run `npm test` before claiming anything works. Commit on a branch named fix/<slug>; do not push (no remote).
J
cat > src/stats.js <<'J'
export function average(xs) {
  if (xs.length === 0) return 0;
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}
J
cat > src/report.js <<'J'
import { average } from "./stats.js";
export const summary = (xs) => `mean=${average(xs)}`;
J
cat > test/stats.test.js <<'J'
import { test } from "node:test";
import assert from "node:assert/strict";
import { average } from "../src/stats.js";
import { summary } from "../src/report.js";
test("avg", () => assert.equal(average([2, 4]), 3));
test("summary", () => assert.equal(summary([2, 4]), "mean=3"));
J
git add -A && git commit -qm init
