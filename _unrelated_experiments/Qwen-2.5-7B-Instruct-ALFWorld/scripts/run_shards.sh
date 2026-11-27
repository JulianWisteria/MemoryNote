#!/usr/bin/env bash
# Run N shards in parallel against one vLLM server.
# Each shard gets its own output dir (separate log/summary); task JSONs do not collide.
set -euo pipefail
cd "$(dirname "$0")/.."

N="${N:-4}"
SPLIT="${SPLIT:-test}"
BASE_OUT="${BASE_OUT:-runs}"

pids=()
for i in $(seq 0 $((N - 1))); do
  python -m alfworld_eval.cli \
    --config configs/alfworld_qwen2.5_7b.yaml \
    --split "${SPLIT}" \
    --num-shards "${N}" \
    --shard-index "${i}" \
    --output-dir "${BASE_OUT}/shard${i}" \
    "$@" &
  pids+=("$!")
done

status=0
for pid in "${pids[@]}"; do
  wait "${pid}" || status=$?
done
exit "${status}"
