# Qwen2.5-7B-Instruct · ALFWorld 1-shot ReAct

A faithful, runnable reimplementation of the ALFWorld baseline in
**MPO** (arXiv:2503.02682, EMNLP 2025 Findings), which reports
Qwen2.5-7B-Instruct at **71.4 seen / 75.4 unseen** with 1-shot ReAct,
30 steps, temperature 0.

The prompt builder is **byte-for-byte identical** to MPO's
`prompt_with_icl` for all six task types (verified against the upstream
source). 37 dependency-free unit tests cover parsing, prompting, note
injection, the episode loop, resume, and sharding.

## 中文速览

- 这是 MPO 的 ALFWorld baseline：每个 task type 一条完整 ICL 轨迹、30 步上限、temperature 0。
- 建议拆成两个 conda env：`eval`（alfworld + openai）和 `serve`（vllm），避免 torch 依赖冲突。
- 单卡 RTX 3090/4090 用 `scripts/serve_qwen_3090.sh` 或 `serve_qwen_4090.sh`（默认 8k ctx / 4 seqs）；OOM 时看下面的 24 GB 内存表。
- 先 `--check`，再 `--dry-run`，再 `--limit-per-type 4` 跑 24 个 env 的 pilot，最后跑 134/140。
- 结果在 `runs/<name>/tasks/*.json` 和 `summary.json`；支持断点续跑。
- 已留好笔记注入钩子：`--notes notes.jsonl --note-mode query|observation`，默认关闭。

## Layout

```text
alfworld_eval/
  agent.py       OpenAI-compatible client (vLLM), retries, token-param fallback
  cli.py         argparse entry point; --check / --list-tasks / --dry-run / run
  config.py      dataclass config + validation + shard math
  env.py         one ALFWorld episode: step, parse, invalid-action accounting
  notes.py       note lookup by task_id / task_type / task_name
  parsing.py     lenient and strict_mpo Action parsers
  prompting.py   MPO prompt template + 1-shot ICL assembly
  runner.py      task loop, resume, per-task JSON, summary metrics
  tasks.py       ALFWorld env creation, splits, task-type detection, sharding
configs/alfworld_qwen2.5_7b.yaml
prompts/         verbatim MPO instruction + ICL assets (Apache-2.0, see ATTRIBUTION)
scripts/         serve (3090 defaults), run_test, run_seen, pilot, shards, merge
tests/           37 stdlib-only tests
```

## Setup

ALFWorld and vLLM disagree about some heavy dependencies, so use two envs.

### Evaluation env (ALFWorld + client)

```bash
conda env create -f environment-eval.yml
conda activate alfworld-qwen-eval
alfworld-download                       # default: ~/.cache/alfworld
export ALFWORLD_DATA=~/.cache/alfworld  # or set env.alfworld_data
```

If you already have ALFWorld installed, `requirements-eval.txt` is sufficient:

```bash
pip install -r requirements-eval.txt
```

### Serving env (vLLM)

```bash
conda env create -f environment-serve.yml
conda activate alfworld-qwen-serve
bash scripts/serve_qwen_3090.sh         # 24 GB-safe: 8k ctx, 4 seqs
```

`--served-model-name` must equal `model.name` in the config
(`Qwen2.5-7B-Instruct` by default). For a 40/80 GB card, call
`scripts/serve_qwen.sh` directly with `MAX_LEN=16384 MAX_NUM_SEQS=8`.

### Remote RTX 3090 / 4090 (24 GB)

7B bf16 is ~15.2 GB of weights; the rest is KV cache + activations.
For Qwen2.5-7B (28 layers, 4 KV heads, head_dim 128), KV cache is roughly
**56 KiB per token per sequence**:

| `MAX_LEN` | `MAX_NUM_SEQS` | KV cache | Fit on 24 GB |
|---:|---:|---:|---|
| 8192 | 4 | ~1.8 GiB | comfortable |
| 16384 | 2 | ~1.8 GiB | comfortable |
| 16384 | 4 | ~3.5 GiB | tight; may OOM |
| 32768 | 4 | ~7.0 GiB | OOM |

Recommended remote workflow (both processes on the 3090 host):

```bash
# one-time, on the remote host
bash scripts/setup_remote.sh
conda activate alfworld-qwen-eval && alfworld-download
export ALFWORLD_DATA=$HOME/.cache/alfworld

# terminal 1
conda activate alfworld-qwen-serve && bash scripts/serve_qwen_3090.sh

# terminal 2
conda activate alfworld-qwen-eval && bash scripts/pilot.sh
```

If vLLM startup OOMs: `ENFORCE_EAGER=1 bash scripts/serve_qwen_3090.sh`, or
`MAX_LEN=4096 MAX_NUM_SEQS=1 ...`. If you need 16k+ context, switch to the AWQ
checkpoint:

```bash
MODEL=Qwen/Qwen2.5-7B-Instruct-AWQ QUANT=awq \
  MAX_LEN=16384 MAX_NUM_SEQS=8 bash scripts/serve_qwen_3090.sh
```

AWQ changes the weights, so report it separately from the bf16 number.

If ALFWorld runs on your laptop and only vLLM runs remotely:

```bash
REMOTE=user@host bash scripts/ssh_tunnel.sh   # local 8000 -> remote 8000
```

Keep `api_base: http://localhost:8000/v1`; prefer the tunnel over exposing the
vLLM port publicly.

## Quickstart

```bash
# 1. validate config + prompt assets, no model / no alfworld needed
python -m alfworld_eval.cli --check

# 2. build real prompts for the first few tasks, no model calls
python -m alfworld_eval.cli --dry-run --dry-run-n 3

# 3. 24-env pilot (4 per task type)
bash scripts/pilot.sh

# 4. full splits
bash scripts/run_test.sh     # 134 unseen  -> compare to 75.4
bash scripts/run_seen.sh     # 140 seen    -> compare to 71.4
```

Pilot gate before spending a full run:

| metric | target | if missed |
|---|---|---|
| `success_rate` | 0.25–0.75 (ideal 0.35–0.65) | <0.15: switch to 14B or another task; >0.85: harder split |
| `parse_errors` | low | inspect `--verbose` raw outputs; tighten the parser |
| `invalid_actions` | understood | if huge, the model is emitting inadmissible commands |

## Outputs

```text
runs/qwen2.5-7b-alfworld/
  log.txt
  summary.json
  tasks/0000.json ...
```

Each task JSON contains the prompt, the full state, and diagnostics:

```json
{
  "task_id": 0,
  "task_name": "pick_and_place/...",
  "task_type": "pick_and_place",
  "split": "eval_out_of_distribution",
  "prompt": "...",
  "state": {
    "steps": 12,
    "reward": 1.0,
    "success": true,
    "terminate_reason": "success",
    "parse_errors": 0,
    "invalid_actions": 2,
    "actions": ["go to cabinet 1", "..."],
    "history": ["..."]
  }
}
```

`summary.json` reports:

- `success_rate` — mean `success`; ALFWorld is binary, so this equals mean reward.
- `avg_reward`, `avg_steps`.
- `terminate_reasons` — `success`, `max_steps`, `max_bad_steps`, `api_error`.
- `by_task_type` — success rate and diagnostics per task family.
- `config` — the full run snapshot.

## Fidelity notes (read before comparing numbers)

1. **1-shot** means one *full trajectory* per task type, taken as the first of
   three examples in `prompts/alfworld_icl.json`. It is not one turn.
2. **9 advertised actions vs 13 environment commands.** The prompt lists nine
   templates (`go/take/put/open/close/toggle/clean/heat/cool`). ALFWorld's
   admissible command set is larger (`use`, `look`, `inventory`, ...), and
   `use` appears only in the `look_at_obj` ICL example. That is how MPO's
   Table 1 gets 13 while its prompt shows 9. Do not "fix" this if you want
   their number.
3. **30 steps**, from `configs/task/alfworld.json` in MPO. The original ReAct
   notebook loops to 49 (community default often 50). Change `env.max_steps`
   to compare against ReAct rather than MPO.
4. **Room description is dropped.** MPO keeps only `Your task is to: ...` from
   the reset observation. Set `env.keep_room_description: true` to keep the
   first paragraph.
5. **Two parsers.** `lenient` (default) takes the first line after `Action:`
   and cuts `Observation:`/`Task:`/`---`. `strict_mpo` reproduces MPO's
   `re.findall(r"Action:\\s?(.*)", re.DOTALL)`, including trailing junk.
   Record which one produced a number.
6. **Temperature 0, one run per task.** There are no error bars. For the
   research design, add seeds or a temperature-0.7 subset.
7. **512 completion tokens.** Long thoughts can be truncated into a parse
   error. Check `parse_errors`; raise `model.max_tokens` only if you also
   report the deviation.
8. **`put` vs `move`.** ALFWorld 0.4.x (TextWorld 1.7) advertises
   `move X to Y`, while the MPO prompt/ICL uses `put X in/on Y`. With
   `env.action_syntax: auto` (default), a `put`/`place` action is rewritten to
   `move` only when the environment's `admissible_commands` contains it. Set
   `put` for older installs that accept the MPO wording, or `move` to force the
   rewrite. Without this, every placement returns "Nothing happens".
9. The 71.4/75.4 numbers are harness-specific. Any change above can move the
   result by many points; that is why the pilot gate exists.

## Note injection hook

The baseline is `--notes` unset. For the controlled note experiments, pass a
JSON or JSONL file:

```jsonl
{"task_id": 12, "note": "When an action returns 'Nothing happens', check whether you are holding the object."}
{"task_type": "pick_and_place", "note": "..."}
```

```bash
python -m alfworld_eval.cli --split test \
  --notes notes.jsonl --note-mode query \
  --output-dir runs/RCS
```

- `query` appends `Additional note:\n...` after the task in the initial prompt.
- `observation` appends the note to every observation instead.
- `none` disables notes even if a file is provided.

Lookup order is `task_id` → `task_type` → `task_name`. This is the hook for the
proposal's N0/N2/R-C-S/R-W-S/I-C-S conditions; note length/format matching is
the caller's responsibility.

## Sharded runs

```bash
N=4 SPLIT=test bash scripts/run_shards.sh
python scripts/merge_shards.py --dirs runs/shard0 runs/shard1 runs/shard2 runs/shard3
```

Each shard writes its own output dir (separate log/summary); task JSONs are
keyed by global `task_id` and merge cleanly.

## Troubleshooting

| symptom | cause / fix |
|---|---|
| `alfworld is not installed` | use Python 3.9/3.10; `pip install "alfworld[full]"` |
| `ALFWorld data not found` | run `alfworld-download`; set `ALFWORLD_DATA` |
| every action → `Nothing happened` | parser is emitting junk; run `--verbose` and inspect raw output |
| `max_completion_tokens` rejected | auto-fallback to `max_tokens`; or set `model.token_param: max_tokens` |
| context-length error | on 24 GB, lower `MAX_LEN`/`MAX_NUM_SEQS` or use AWQ; do not raise blindly |
| Qwen3 thinking mode (later) | add `model.extra_body: {"chat_template_kwargs": {"enable_thinking": false}}` |

## Tests

```bash
python tests/run_tests.py        # 37 tests, stdlib only
```

They do not require ALFWorld, vLLM, or an API key.

## Attribution

- `prompts/alfworld_inst.txt` and `prompts/alfworld_icl.json` are copied
  verbatim from [WeiminXiong/MPO](https://github.com/WeiminXiong/MPO)
  (Apache-2.0; see `prompts/MPO_LICENSE_APACHE2.txt`).
- ALFWorld protocol: Shridhar et al., *ALFWorld* (arXiv:2010.03768).
- ReAct protocol: Yao et al., *ReAct* (arXiv:2210.03629).
