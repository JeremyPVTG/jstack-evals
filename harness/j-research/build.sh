#!/bin/sh
# Assemble two plugins that differ only in j-research: build/with-skill and
# build/tools-only. Both are named "jstack", declare the same MCP servers and
# share the same cases and mocks, so the score gap is the skill's contribution.
# Usage: build.sh JSTACK_REPO COMMIT
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$1; commit=$2
rm -rf "$here/build"
for variant in with-skill tools-only; do
  out="$here/build/$variant"
  mkdir -p "$out/.claude-plugin"
  printf '{"name": "jstack", "version": "0.0.0", "description": "j-research eval harness (%s, jstack %s)"}\n' "$variant" "$commit" > "$out/.claude-plugin/plugin.json"
  cp "$here/source/mcp.json" "$out/.mcp.json"
  cp -R "$here/source/evals" "$out/evals"
  cp -R "$here/source/trigger-evals" "$out/trigger-evals"
  cp -R "$here/source/heldout-evals" "$out/heldout-evals"
done
mkdir -p "$here/build/with-skill/skills"
git -C "$repo" archive "$commit" skills/j-research | tar -x -C "$here/build/with-skill"
echo "$commit" > "$here/build/COMMIT"
echo "built j-research harness from $commit"
