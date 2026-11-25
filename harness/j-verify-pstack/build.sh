#!/bin/sh
# build.sh new|none OUT: plugin "jstack" with j-verify (new, from the jstack checkout) or no skill, plus the probes.
set -eu
here=$(cd "$(dirname "$0")" && pwd); which=$1; out=$2
# jstack skills to test: $JSTACK_SKILLS, else the sibling jstack checkout. Recorded results name the jstack commit they used.
J=${JSTACK_SKILLS:-$(cd "$here/../../.." && pwd)/jstack/skills}
rm -rf "$out"; mkdir -p "$out/.claude-plugin" "$out/skills"
printf '{"name": "jstack", "version": "0.0.0", "description": "j-verify probe harness (%s)"}\n' "$which" > "$out/.claude-plugin/plugin.json"
cp -R "$here/source/evals" "$out/evals"
for c in "$out"/evals/*/; do cp "$here/source/fixture.sh" "$c/fixture.sh"; done
if [ "$which" = new ]; then cp -R "$J/j-verify" "$out/skills/"; fi
echo "built $which -> $out"
