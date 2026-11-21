#!/usr/bin/env bash
# 140 seen ALFWorld tasks (MPO's 71.4 number).
set -euo pipefail
cd "$(dirname "$0")/.."

python -m alfworld_eval.cli \
  --config configs/alfworld_qwen2.5_7b.yaml \
  --split dev \
  "$@"
