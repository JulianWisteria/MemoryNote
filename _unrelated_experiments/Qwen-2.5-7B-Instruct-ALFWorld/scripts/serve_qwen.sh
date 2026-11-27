#!/usr/bin/env bash
# Serve Qwen2.5-7B-Instruct with an OpenAI-compatible endpoint.
# Run this in the *serve* env (see environment-serve.yml).
#
# Defaults are tuned for a single 24 GB RTX 3090:
#   bf16 7B (~15.2 GB) + 8k context + 4 sequences fits with headroom.
# For a 40/80 GB card, raise MAX_LEN and MAX_NUM_SEQS.
set -euo pipefail

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
SERVED_NAME="${SERVED_NAME:-Qwen2.5-7B-Instruct}"
PORT="${PORT:-8000}"
MAX_LEN="${MAX_LEN:-8192}"          # 1-shot ICL + 30 turns fits in 8k
GPU="${GPU:-0}"
GPU_MEM="${GPU_MEM:-0.90}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-4}"
DTYPE="${DTYPE:-bfloat16}"
ENFORCE_EAGER="${ENFORCE_EAGER:-0}" # set 1 if startup OOMs
QUANT="${QUANT:-}"                  # e.g. awq when using an AWQ checkpoint
EXTRA_ARGS="${EXTRA_ARGS:-}"

args=(
  --served-model-name "${SERVED_NAME}"
  --port "${PORT}"
  --max-model-len "${MAX_LEN}"
  --dtype "${DTYPE}"
  --gpu-memory-utilization "${GPU_MEM}"
  --max-num-seqs "${MAX_NUM_SEQS}"
)

if [[ "${ENFORCE_EAGER}" == "1" ]]; then
  args+=(--enforce-eager)
fi
if [[ -n "${QUANT}" ]]; then
  args+=(--quantization "${QUANT}")
fi
if [[ -n "${EXTRA_ARGS}" ]]; then
  read -r -a extra <<< "${EXTRA_ARGS}"
  args+=("${extra[@]}")
fi

echo "serving ${MODEL} as ${SERVED_NAME} on :${PORT}"
echo "  GPU=${GPU} dtype=${DTYPE} max_len=${MAX_LEN} max_num_seqs=${MAX_NUM_SEQS} gpu_mem=${GPU_MEM}"
echo "  quant=${QUANT:-none} enforce_eager=${ENFORCE_EAGER}"
CUDA_VISIBLE_DEVICES="${GPU}" vllm serve "${MODEL}" "${args[@]}"
