#!/bin/bash
# run_eval.sh VARIANT NAME MODEL RUNS MAXCOST [extra eval args...]
# Runs one plugin-eval pass against build/VARIANT, keeping traces; results go to results/NAME.{json,log}.
set -u
variant=$1; name=$2; model=$3; runs=$4; cap=$5; shift 5
env -u CLAUDE_CONFIG_DIR claude plugin eval "build/$variant" --ablation none --threshold 0 --trust-plugin --no-publish --keep-temp \
  --runs "$runs" -j 4 --model "$model" --max-cost-usd "$cap" "$@" --json "results/$name.json" > "results/$name.log" 2>&1
echo "$name exit $?"
