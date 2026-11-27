#!/usr/bin/env bash
# Run N shards, alternating between two vLLM servers (ports 8000 and 8001).
# Use this when GPU0 and GPU1 each serve the same model:
#   bash scripts/serve_qwen_3090.sh                 # GPU 0 -> :8000
#   CUDA_VISIBLE_DEVICES=1 PORT=8001 bash scripts/serve_qwen_3090.sh
#   N=4 SPLIT=test bash scripts/run_shards_dual.sh
# Then merge:
#   python scripts/merge_shards.py --dirs runs/shard0 runs/shard1 runs/shard2 runs/shard3
set -euo pipefail
cd "$(dirname "$0")/.."

N="${N:-4}"
SPLIT="${SPLIT:-test}"
BASE_OUT="${BASE_OUT:-runs}"
BASE_PORT="${BASE_PORT:-8000}"

pids=()
for i in $(seq 0 $((N - 1))); do
  port=$((BASE_PORT + i % 2))
  python -m alfworld_eval.cli \
    --config configs/alfworld_qwen2.5_7b.yaml \
    --split "${SPLIT}" \
    --num-shards "${N}" \
    --shard-index "${i}" \
    --output-dir "${BASE_OUT}/shard${i}" \
    --api-base "http://localhost:${port}/v1" \
    "$@" &
  pids+=("$!")
done

status=0
for pid in "${pids[@]}"; do
  wait "${pid}" || status=$?
done
exit "${status}"
