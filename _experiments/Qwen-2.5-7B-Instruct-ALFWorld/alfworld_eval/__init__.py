"""ALFWorld evaluation harness for a Qwen2.5-7B-Instruct 1-shot ReAct agent.

This is a clean reimplementation of the ALFWorld baseline used by
MPO (arXiv:2503.02682, EMNLP 2025 Findings), which reports
Qwen2.5-7B-Instruct at 71.4 (seen) / 75.4 (unseen).

Submodules are intentionally *not* imported here so that
``python -m alfworld_eval.cli --check`` works without alfworld/openai/vllm.
"""

__version__ = "0.1.0"
