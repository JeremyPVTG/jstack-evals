#!/bin/bash
set -e
git init -q && git config user.email t@example.com && git config user.name Test
mkdir -p src test
cat > package.json <<'J'
{"name": "greeter", "private": true, "type": "module", "scripts": {"test": "node --test test/"}}
J
cat > AGENTS.md <<'J'
# greeter
A tiny CLI: `node cli.js greet <name> [--shout]`. Tests: `npm test`. No remote; do not push.
J
cat > src/greet.js <<'J'
export function greeting(name, shout = false) {
  const text = "Hello, " + name;
  return shout ? text.toUpperCase() + "!" : text;
}
J
cat > cli.js <<'J'
import { greeting } from "./src/greet.js";
const [cmd, name, ...flags] = process.argv.slice(2);
if (cmd !== "greet" || !name) { console.error("usage: node cli.js greet <name> [--shout]"); process.exit(2); }
const shout = flags.includes("--shout");
console.log(greeting(name, shout));
J
cat > test/greet.test.js <<'J'
import { test } from "node:test";
import assert from "node:assert/strict";
import { greeting } from "../src/greet.js";
test("plain", () => assert.equal(greeting("Ann"), "Hello, Ann"));
test("shout", () => assert.equal(greeting("Ann", true), "HELLO, ANN!"));
J
git add -A && git commit -qm "greet command"
git checkout -qb feat/shout && git commit -q --allow-empty -m "feat: --shout flag"
