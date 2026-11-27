#!/usr/bin/env bash
# Convenience wrapper: Qwen2.5-7B-Instruct on one 24 GB GPU (RTX 3090 / 4090).
#
# bf16 (recommended for paper fidelity):
#   bash scripts/serve_qwen_3090.sh
#
# If startup OOMs:
#   ENFORCE_EAGER=1 bash scripts/serve_qwen_3090.sh
#   # or reduce context / concurrency
#   MAX_LEN=4096 MAX_NUM_SEQS=1 bash scripts/serve_qwen_3090.sh
#
# If you need 16k context or more concurrency, use the AWQ checkpoint
# (4-bit, ~5 GB weights; results may differ slightly from bf16):
#   MODEL=Qwen/Qwen2.5-7B-Instruct-AWQ QUANT=awq \
#     MAX_LEN=16384 MAX_NUM_SEQS=8 bash scripts/serve_qwen_3090.sh
set -euo pipefail
cd "$(dirname "$0")/.."

export MAX_LEN="${MAX_LEN:-8192}"
export MAX_NUM_SEQS="${MAX_NUM_SEQS:-4}"
export GPU_MEM="${GPU_MEM:-0.90}"
export DTYPE="${DTYPE:-bfloat16}"
export ENFORCE_EAGER="${ENFORCE_EAGER:-0}"

exec bash scripts/serve_qwen.sh
