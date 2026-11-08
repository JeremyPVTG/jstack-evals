#!/bin/sh
# Assemble two plugins that differ only in j-research: build/with-skill and
# build/tools-only. Both are named "jstack", declare the same MCP servers and
# share the same cases and mocks, so the score gap is the skill's contribution.
# Usage: build.sh JSTACK_REPO COMMIT
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$1; commit=$2
build=${BUILD_DIR:-$here/build}
rm -rf "$build"
for variant in with-skill tools-only; do
  out="$build/$variant"
  mkdir -p "$out/.claude-plugin"
  printf '{"name": "jstack", "version": "0.0.0", "description": "j-research eval harness (%s, jstack %s)"}\n' "$variant" "$commit" > "$out/.claude-plugin/plugin.json"
  cp "$here/source/mcp.json" "$out/.mcp.json"
  cp -R "$here/source/evals" "$out/evals"
  cp -R "$here/source/trigger-evals" "$out/trigger-evals"
  cp -R "$here/source/heldout-evals" "$out/heldout-evals"
  for extra in heldout-cases heldout-cases-2 trigger-evals-2 test-set-1; do [ -d "$here/source/$extra" ] && cp -R "$here/source/$extra" "$out/$extra"; done
done
mkdir -p "$build/with-skill/skills"
git -C "$repo" archive "$commit" skills/j-research | tar -x -C "$build/with-skill"
if [ "${HOOK:-0}" = 1 ]; then  # add j-research's prompt hook to the with-skill plugin
  mkdir -p "$build/with-skill/hooks"
  printf '%s\n' '{"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/skills/j-research/scripts/research_hook.py", "timeout": 5}]}]}}' > "$build/with-skill/hooks/hooks.json"
fi
echo "$commit${HOOK:+ hook=$HOOK}" > "$build/COMMIT"
echo "built j-research harness from $commit"
