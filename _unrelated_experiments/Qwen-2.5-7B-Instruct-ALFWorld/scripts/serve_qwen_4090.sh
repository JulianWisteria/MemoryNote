#!/usr/bin/env bash
# RTX 4090 (24 GB) entry point. Same memory budget as the 3090 wrapper.
#   bash scripts/serve_qwen_4090.sh
#   CUDA_VISIBLE_DEVICES=1 ...   # to use the second card
set -euo pipefail
exec bash "$(dirname "$0")/serve_qwen_3090.sh" "$@"
