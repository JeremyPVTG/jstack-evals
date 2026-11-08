#!/bin/bash
set -e
git init -q && git config user.email t@example.com && git config user.name Test
mkdir -p src dist bin test scripts
cat > package.json <<'J'
{"name": "greeter", "version": "1.2.0", "private": true, "type": "module",
 "bin": {"greeter": "bin/greeter.js"},
 "scripts": {"build": "node scripts/build.js", "test": "node --test test/"}}
J
cat > AGENTS.md <<'J'
# greeter
A small CLI, installed as the `greeter` command. Tests: `npm test`. Branch names: feat/<slug>. No remote; do not push.
J
cat > src/greet.js <<'J'
export function greeting(name) {
  return "Hello, " + name;
}
J
cat > src/cli.js <<'J'
import { greeting } from "./greet.js";
const [cmd, name] = process.argv.slice(2);
if (cmd !== "greet" || !name) { console.error("usage: greeter greet <name>"); process.exit(2); }
console.log(greeting(name));
J
cat > scripts/build.js <<'J'
import { cpSync, mkdirSync } from "node:fs";
mkdirSync("dist", { recursive: true });
for (const f of ["greet.js", "cli.js"]) cpSync("src/" + f, "dist/" + f);
console.log("built dist/");
J
cat > bin/greeter.js <<'J'
#!/usr/bin/env node
import "../dist/cli.js";
J
chmod +x bin/greeter.js
cp src/greet.js src/cli.js dist/
cat > test/greet.test.js <<'J'
import { test } from "node:test";
import assert from "node:assert/strict";
import { greeting } from "../src/greet.js";
test("plain", () => assert.equal(greeting("Ann"), "Hello, Ann"));
J
git add -A && git commit -qm "greeter 1.2.0"
