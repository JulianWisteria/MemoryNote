#!/usr/bin/env bash
# 134 unseen ALFWorld tasks (the split used by Reflexion and MPO's 75.4 number).
set -euo pipefail
cd "$(dirname "$0")/.."

python -m alfworld_eval.cli \
  --config configs/alfworld_qwen2.5_7b.yaml \
  --split test \
  "$@"
