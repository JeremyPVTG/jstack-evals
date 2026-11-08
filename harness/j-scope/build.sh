#!/bin/sh
# build.sh JSTACK_REPO COMMIT OUT_DIR: a plugin "jstack" containing only skills/j-scope at COMMIT, plus the cases.
set -eu
here=$(cd "$(dirname "$0")" && pwd); repo=$1; commit=$2; out=$3
rm -rf "$out"; mkdir -p "$out/.claude-plugin" "$out/skills"
printf '{"name": "jstack", "version": "0.0.0", "description": "j-scope eval harness (jstack %s)"}\n' "$commit" > "$out/.claude-plugin/plugin.json"
cp -R "$here/source/evals" "$out/evals"
git -C "$repo" archive "$commit" skills/j-scope | tar -x -C "$out"
echo "$commit" > "$out/COMMIT"; echo "built j-scope harness from $commit -> $out"
