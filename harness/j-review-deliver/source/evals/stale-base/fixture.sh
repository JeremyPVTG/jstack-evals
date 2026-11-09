#!/bin/bash
set -e
git init -q --bare .origin.git
git init -q -b main && git config user.email t@example.com && git config user.name Test
git remote add origin ./.origin.git
mkdir -p src test
cat > package.json <<'J'
{"name": "cal", "private": true, "type": "module", "scripts": {"test": "node --test test/"}}
J
cat > AGENTS.md <<'J'
# cal
CI runs `npm test`. To bring a branch up to date with main, merge origin/main into it; never rebase or force-push. The remote is `origin` (local). Push the PR branch when it is green.
J
cat > .gitignore <<'J'
.origin.git/
J
cat > src/date.js <<'J'
// ISO week day, Monday = 1 ... Sunday = 7.
export const isoDay = (d) => d.getUTCDay();
J
cat > test/date.test.js <<'J'
import { test } from "node:test";
import assert from "node:assert/strict";
import { isoDay } from "../src/date.js";
test("sunday is 7", () => assert.equal(isoDay(new Date(Date.UTC(2026, 10, 8))), 7));
J
git add -A && git commit -qm "cal" && git push -q origin main
git checkout -qb feat/greet
cat > src/greet.js <<'J'
export const greet = (name) => "Hello, " + name;
J
cat > test/greet.test.js <<'J'
import { test } from "node:test";
import assert from "node:assert/strict";
import { greet } from "../src/greet.js";
test("greet", () => assert.equal(greet("Ann"), "Hello, Ann"));
J
cat > ci-log.txt <<'J'
Run npm test
✔ greet (0.4ms)
✖ sunday is 7 (0.9ms)
  AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:
  0 !== 7
      at test/date.test.js:4
ℹ pass 1
ℹ fail 1
Error: Process completed with exit code 1.
J
git add -A && git commit -qm "feat: greet (CI log attached)" && git push -q -u origin feat/greet
git checkout -q main
cat > src/date.js <<'J'
// ISO week day, Monday = 1 ... Sunday = 7.
export const isoDay = (d) => d.getUTCDay() || 7;
J
git commit -qam "fix: isoDay returns 7 for Sunday" && git push -q origin main
git checkout -q feat/greet
git update-ref -d refs/remotes/origin/main
