#!/bin/sh
# build.sh SKILL_SOURCE_DIR NAME OUT: plugin "jstack" with one build skill (j-build from a jstack commit dir, or staged-build-workflow), plus the probes.
set -eu
here=$(cd "$(dirname "$0")" && pwd); src=$1; name=$2; out=$3
rm -rf "$out"; mkdir -p "$out/.claude-plugin" "$out/skills"
printf '{"name": "jstack", "version": "0.0.0", "description": "j-build probe harness (%s)"}\n' "$name" > "$out/.claude-plugin/plugin.json"
cp -R "$here/source/evals" "$out/evals"; cp -R "$src" "$out/skills/$name"; echo "built $name -> $out"
