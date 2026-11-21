#!/usr/bin/env bash
# One-time setup on the remote RTX 3090 host.
# Creates the two conda envs and downloads ALFWorld data.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found; install Miniconda first" >&2
  exit 1
fi
if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "warning: nvidia-smi not found; vLLM will not start" >&2
fi

echo "== creating eval env (alfworld + openai) =="
conda env create -f environment-eval.yml || echo "eval env already exists?"

echo "== creating serve env (vllm) =="
conda env create -f environment-serve.yml || echo "serve env already exists?"

echo
echo "Next:"
echo "  conda activate alfworld-qwen-eval"
echo "  alfworld-download"
echo "  export ALFWORLD_DATA=\$HOME/.cache/alfworld"
echo "  python -m alfworld_eval.cli --check"
echo
echo "Then, in two terminals:"
echo "  conda activate alfworld-qwen-serve && bash scripts/serve_qwen_3090.sh"
echo "  conda activate alfworld-qwen-eval  && bash scripts/pilot.sh"
