#!/bin/bash
# climb/screen.sh TAG RUNS VARIANT_DIR... : run the targeted cases for each variant on both models, interleaved.
# Targets are lines "eval-dir case" in climb/targets.txt.
set -u
tag=$1; runs=$2; shift 2
for m in sonnet opus; do
  while read -r dir case; do
    [ -z "$dir" ] && continue
    for v in "$@"; do
      KEEP_TYPESAFE=1 ./run_eval.sh "$v/with-skill" "climb-$tag-$(basename "$v")-$m-$case" "$m" "$runs" 6 --eval-dir "$dir" --case "$case" &
    done
    wait
  done < climb/targets.txt
done
