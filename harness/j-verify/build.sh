#!/bin/sh
# build.sh SKILL_DIR|none NAME OUT: plugin "jstack" with one skill (or none, for the baseline), plus the probes.
set -eu
here=$(cd "$(dirname "$0")" && pwd); src=$1; name=$2; out=$3
rm -rf "$out"; mkdir -p "$out/.claude-plugin" "$out/skills"
printf '{"name": "jstack", "version": "0.0.0", "description": "j-verify probe harness (%s)"}\n' "$name" > "$out/.claude-plugin/plugin.json"
cp -R "$here/source/evals" "$out/evals"
[ "$src" = none ] || cp -R "$src" "$out/skills/$name"
echo "built $name -> $out"
