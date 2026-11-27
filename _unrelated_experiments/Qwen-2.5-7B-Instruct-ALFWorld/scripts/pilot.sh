#!/usr/bin/env bash
# Cheap pilot: N envs per task type (default 4 -> 24 envs across 6 types).
# Use this before committing to 134/140 envs. Gate:
#   0.25 <= success_rate <= 0.75  (ideal 0.35-0.65)
#   parse_errors low; invalid_actions understood
set -euo pipefail
cd "$(dirname "$0")/.."

PER_TYPE="${PER_TYPE:-4}"
OUT="${OUT:-runs/pilot}"

python -m alfworld_eval.cli \
  --config configs/alfworld_qwen2.5_7b.yaml \
  --split "${SPLIT:-test}" \
  --limit-per-type "${PER_TYPE}" \
  --output-dir "${OUT}" \
  "$@"
