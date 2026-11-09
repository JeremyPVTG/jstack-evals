#!/bin/bash
# run_eval.sh BUILD_VARIANT_DIR NAME MODEL RUNS MAXCOST [extra eval args...]
# One plugin-eval pass, traces kept; results in results/NAME.{json,log}.
# Billing: the Claude Platform key at Infisical /research (ANTHROPIC_API_KEY). Other research
# keys are removed; TYPESAFE_API_KEY is kept only when KEEP_TYPESAFE=1 (for builds with the hook).
set -u
target=$1; name=$2; model=$3; runs=$4; cap=$5; shift 5
drop=(-u CLAUDE_CONFIG_DIR -u ANTHROPIC_BASE_URL -u ANTHROPIC_AUTH_TOKEN -u EXA_API_KEY -u FIRECRAWL_API_KEY -u OPENROUTER_API_KEY -u TAVILY_API_KEY)
[ "${KEEP_TYPESAFE:-0}" = 1 ] || drop+=(-u TYPESAFE_API_KEY)
pass=()  # plugin evals forward only allowlisted and EVAL_* variables; the hook reads EVAL_TYPESAFE_API_KEY
[ "${KEEP_TYPESAFE:-0}" = 1 ] && pass=(bash -c 'export EVAL_TYPESAFE_API_KEY="$TYPESAFE_API_KEY"; exec "$@"' _)
/Users/jeremy/.local/bin/infisical run --silent --projectId dbb4c6c1-6800-4479-8cfd-fd65c2d5966d --env prod --path /research -- \
  ${pass[@]+"${pass[@]}"} env "${drop[@]}" \
  claude plugin eval "$target" --ablation none --threshold 0 --trust-plugin --no-publish --keep-temp \
  --runs "$runs" -j 4 --model "$model" --max-cost-usd "$cap" "$@" --json "results/$name.json" > "results/$name.log" 2>&1
echo "$name exit $?"
