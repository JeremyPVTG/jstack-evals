#!/bin/bash
# run_eval.sh BUILD_DIR NAME MODEL RUNS MAXCOST [extra args...]: one j-build probe pass (fixtures on, traces kept), billed to the Platform key at Infisical /research.
set -u
target=$1; name=$2; model=$3; runs=$4; cap=$5; shift 5
/Users/jeremy/.local/bin/infisical run --silent --projectId dbb4c6c1-6800-4479-8cfd-fd65c2d5966d --env prod --path /research -- \
  env -u CLAUDE_CONFIG_DIR -u ANTHROPIC_BASE_URL -u ANTHROPIC_AUTH_TOKEN -u EXA_API_KEY -u FIRECRAWL_API_KEY -u OPENROUTER_API_KEY -u TAVILY_API_KEY -u TYPESAFE_API_KEY \
  claude plugin eval "$target" --ablation none --threshold 0 --trust-plugin --no-publish --keep-temp --scaffold \
  --runs "$runs" -j 4 --model "$model" --max-cost-usd "$cap" "$@" --json "results/$name.json" > "results/$name.log" 2>&1
echo "$name exit $?"
