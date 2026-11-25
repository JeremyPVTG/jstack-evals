#!/bin/sh
# build.sh new|old|none OUT: plugin "jstack" with the rebuilt j-review + j-deliver (new, from the jstack checkout) or the six personal pr-* skills (old), plus the probes.
set -eu
here=$(cd "$(dirname "$0")" && pwd); which=$1; out=$2
# jstack skills to test: $JSTACK_SKILLS, else the sibling jstack checkout. Recorded results name the jstack commit they used.
J=${JSTACK_SKILLS:-$(cd "$here/../../.." && pwd)/jstack/skills}
rm -rf "$out"; mkdir -p "$out/.claude-plugin" "$out/skills"
printf '{"name": "jstack", "version": "0.0.0", "description": "j-review/j-deliver probe harness (%s)"}\n' "$which" > "$out/.claude-plugin/plugin.json"
cp -R "$here/source/evals" "$out/evals"
if [ "$which" = none ]; then :; elif [ "$which" = new ]; then cp -R "$J/j-review" "$J/j-deliver" "$out/skills/"; else for s in pr-review-verdict pr-review-and-fix pr-stale-review-threads pr-test-and-publish pr-ci-failure-fix pr-merge-readiness; do cp -R "$HOME/.claude/skills/$s" "$out/skills/"; done; fi
echo "built $which -> $out"
