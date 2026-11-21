# 笔记语义与效用：文献路线图
### Note Semantics & Utility in LLM Agents · Roadmap v0.1

> 这是一份**策展式**地图，不是系统综述。目标是把"笔记/记忆有没有用"从一个泛问题，拆成已经被回答的部分、仍有争议的部分、和你的可控实验能补上的部分。  
> 方法：以本地 5 篇种子论文（Reflexion、Kim 2026、Honest Lying、ReAct、MPO）的参考文献为起点，做 backward/forward citation 扩展，再按六个 cluster 做定向检索。  
> 标注：`*` 表示 arXiv ID 来自检索结果，投稿前需复核；本地 PDF 及其参考文献是权威来源。
>
> **本地种子 PDF**：[Reflexion](../papers/reflexion.pdf) · [Kim 2026](../papers/Kim2026_SelfWrittenNotes_Preprint_v0.3b.pdf) · [Honest Lying](../papers/Honest_Lying.pdf) · [ReAct](../papers/ReAct.pdf) · [MPO](../papers/MPO.pdf)

---

## 0. 一句话现状

领域已经从 **"memory 有没有用"**（Reflexion 2023）走到 **"哪种表示、对哪个任务、在什么反馈下有用，以及 agent 能不能知道自己有没有用"**（2025–2026）。你的题目正好落在这个转向的中间：**把 note 当成可操纵的文本干预，而不是一个二元的 memory 开关。**

四个已经发生的转向：

1. **从存 trajectory 到蒸馏 insight / workflow / playbook**（ExpeL → AWM → ACE → Hindsight）。
2. **从"更多 memory"到"选择与抽象"**（Hu 2026；Memory Transfer Learning；*When Should Experience Become Parameters*；JITMem）。
3. **从"self-reflection 有益"到"自写 memory 会混淆、会伤害"**（Kim 2026；Honest Lying；Zhao 2026；Huang 2024）。
4. **从 task success 到 memory-specific evaluation**：utility、sufficiency、forgetting、transfer、honesty（*What Is This Memory Useful For?*；MemoryArena；LongMemEval；HaluMem）。

---

## 1. Citation graph（种子 → 主要后代）

```text
Reflexion (2023)
├── Self-Refine (2023)            iterative self-feedback, no persistent memory
├── ReAct (2022)                  thought/action/observation loop
├── ExpeL (2024)                  insights + top-k trajectories
│   ├── Agent Workflow Memory (2025)   reusable workflows
│   ├── ACE (2026)                playbook bullets, brevity bias, context collapse
│   └── Hindsight (2026)          world/experience/observation/opinion networks
├── Honest Lying (2026)           memory confabulation, RRR, feedback granularity
│   ├── Du 2026 survey            write–manage–read loop
│   ├── Zhang 2025 survey         memory taxonomy
│   └── HaluMem / Memory Reward Inflation (2026)
└── Kim 2026 (self-written notes)
    ├── ACE, Hindsight
    ├── Zhao 2026 (repair–generalization gap)
    └── Hu 2026 (experience reuse, abstraction)
        ├── Memory Transfer Learning (2026)
        ├── JITMem (2026)
        └── MemoryArena (2026)
```

**读法**：Reflexion 是共同祖先；2026 年的工作分成两条支线——一条研究 **表示/抽象/选择**（ExpeL→AWM→ACE→Hu→MTL→JITMem），一条研究 **错误/混淆/诚实**（Honest Lying→Zhao→HaluMem）。你的 2×2 正好是这两条支线的交叉点。

---

## 2. 时间线

| 年份 | 关键工作 | 留下的问题 |
|---|---|---|
| 2022 | ReAct, SayCan, WebShop | 如何交错 reasoning 与 acting |
| 2023 | Reflexion, Self-Refine, Generative Agents, MemGPT, MemoryBank, Voyager, CoALA, ExpeL | memory 存什么、怎么取、能否自我改进 |
| 2024 | AWM, Agent-FLAN, Huang et al. critique, LongMemEval, τ-bench | 表示形式、SFT、self-correction 的边界 |
| 2025 | ACE, Hindsight, JITMem, MemoryAgentBench, MemBench | 上下文工程、read-time curation、memory benchmark |
| 2026 | Kim, Honest Lying, Zhao, Hu, MTL, *What Is This Memory Useful For?*, AgentBrew, MemoryArena, MemoryTax | 内容正确性、抽象-迁移、task-conditioned utility、confabulation |

---

## 3. 六个 cluster

### Cluster A — Reflective / experiential memory mechanisms

| 工作 | 核心机制 | 关键结果 | 对你 |
|---|---|---|---|
| **Reflexion** (Shinn 2023, arXiv:2303.11366) | actor / evaluator / self-reflection；memory 1–3 条 | ALFWorld +22%, HotpotQA +20%, HumanEval +11% | 你的基线架构与术语来源 |
| **Self-Refine** (Madaan 2023, arXiv:2303.17651) | 同模型迭代 self-feedback，无持久 memory | 单轮生成任务有效，边界有限 | "better prompting" 的近亲；不要当 memory |
| **ExpeL** (Zhao 2024, arXiv:2308.10144) | experience pool → insight extraction（ADD/EDIT/UPVOTE/DOWNVOTE）→ top-k 轨迹 | HotpotQA 28→39；更好的 insight LLM 有帮助；把 reflection 混进 insight extraction 反而降到 29.0% | "writer model" 与 "note specificity" 的直接前身 |
| **AWM** (Wang 2025, arXiv:2409.07429) | 从轨迹归纳 reusable workflow，offline/online | Mind2Web +24.6%, WebArena +51.1% | workflow 是 note 的抽象端 |
| **ACE** (Zhang 2026, arXiv:2510.04618) | playbook bullets；generator/reflector/curator；delta updates；grow-and-refine | AppWorld +10.6%；brevity bias、context collapse | note 长度/模板/curator 的直接相关工作 |
| **Hindsight** (Latimer 2026, arXiv:2512.12818) | world/experience/observation/opinion 四网络；retain/recall/reflect；confidence | LongMemEval 39→83.6（20B，vendor claim） | 结构化 note + confidence 的设计参考 |
| **JITMem** (Zhou 2026, arXiv:2609.27334) | 保留 raw trajectory，read-time 生成 task-adaptive briefing | ALFWorld +16.2, WebShop +16.3, τ² +3.9 | "write-time vs read-time" 是 note 研究的关键对照 |
| Generative Agents (Park 2023), MemGPT (Packer 2023), MemoryBank (Zhong 2023), A-MEM (Xu 2025), Mem0 (Chhikara 2025), Voyager (Wang 2023) | memory stream / paging / Ebbinghaus / Zettelkasten / production layer / skill library | 多为对话/长程 assistant memory | 提供 memory 架构词汇，但不是 agentic note 因果研究 |

#### Cluster A2 — Meta-plan / plan optimization（MPO line）

**MPO**（Xiong et al. 2025, EMNLP Findings, arXiv:2503.02682）是"把 plan/guidance 当成可优化 memory"的一条线。它和 Reflexion/ExpeL 的关键区别：优化的是 **per-task-family 的 meta-plan**，不是 per-task reflection。

| 维度 | MPO 的做法 |
|---|---|
| 产物 | 一个 task-family 级别的高层 plan（不是 trajectory，不是 per-task note） |
| Writer | 独立的 meta-plan generator；SFT 初始化，explorer 评估候选 plan，构造偏好对，DPO 优化 |
| 注入 | `query`（追加到 task）、`observation`（追加到每步 observation）、`thought`（作为 assistant 前缀继续生成） |
| 结果 | Qwen2.5-7B 71.4/75.4；Llama-3.1-8B 22.9/28.4；Llama-3.1-70B 78.6/73.9；GPT-4o 78.6/83.6 |
| 关键发现 | 同一 meta-plan 可跨 agent 复用；**低质量 meta-plan 会误导 agent**（SFT 初始化的 plan 反而降低 Qwen 表现）；incorporation type 有影响 |

与相邻工作的区别：

- **MPO vs Reflexion**：Reflexion 是 per-task、per-trial、自生成；MPO 是 per-family、离线优化、writer 与 actor 分离。
- **MPO vs ExpeL**：ExpeL 抽 insight + 检索 trajectory；MPO 优化一个 task-family plan。
- **MPO vs AWM**：AWM 从轨迹归纳 workflow；MPO 用偏好对优化 plan。
- **MPO vs ACE**：ACE 是 online、bullet、grow-and-refine；MPO 是 offline DPO、单 plan。

**对你的意义**：

- MPO 是你 ALFWorld harness 的来源（1-shot、30 步、13 动作、134 unseen），也是 76.87% baseline 的对照（75.4）。
- 它是"better writer / optimized note"的强 baseline，但**没有回答你的核心问题**：note semantics（correctness × specificity）、wrong/irrelevant 控制、note-level 方差、honesty gap、harm rate。
- Phase 2 可以用 MPO 式 DPO 训练 note writer，但评估必须回到 note semantics，而不是只看 task success。
- MPO 自己报告"低质量 meta-plan 会误导 agent"，这正是你 R-W-S 条件的先声；可以引用它作为 "relevant but wrong can harm" 的佐证。

### Cluster B — Note content, abstraction, transfer

| 工作 | 核心发现 | 对你 |
|---|---|---|
| **Kim 2026** (本地 PDF) | 同一条相关笔记帮 XOR、害 AND；等长无关笔记 inert；三条 replication 从 1/48 到 46/48 | 内容特定性、note-level 方差、负控制的直接证据 |
| **Hu 2026** (arXiv:2604.27003) | (k,v) 框架；abstract procedural memory 比 raw trajectory 更可迁移；negative transfer 集中 hard cases；finer-grained organization 不总是更好；retrieval diversity collapse | specificity/abstraction 轴的核心证据 |
| **Memory Transfer Learning** (Kim et al. 2026, arXiv:2604.14004) | trajectory +1.1%, workflow +1.5%, summary +2.3%, insight +3.7%；低层 trace 造成 negative transfer；94.5% gains 来自 procedural meta-knowledge | 抽象程度的剂量-反应曲线；你的 specificity 轴可以直接借用 |
| **Zhao 2026** (arXiv:2610.22984) | failure-only evolution 有 repair–generalization gap；false-success、misattribution、distorted consolidation、harmful guidance；即使 verified-correct 也不转移；成功轨迹才提升 transfer | correctness 轴 + writer/feedback 的上游原因 |
| ***What Is This Memory Useful For?*** (Yang 2026, arXiv:2611.03930) | task-conditioned utility；answer-bearing memory +0.33 paired reward；task-blind summary/structured record 在固定 context 下不如 raw；gains 不转移到 SWE | sufficiency 轴；你的"relevance"应该升级成"sufficiency" |
| **From Relevant Memories to Sufficient Evidence** (2026, arXiv:2610.22668) | relevance ≠ sufficiency；需要 query-specific evidence set | 第三个轴的直接定义 |
| **Diagnosing Retrieval vs. Utilization** (2026, arXiv:2603.02473) | retrieval precision 与 accuracy r=0.98；检索比 write strategy 更主导 | 检索是必须控制的 moderator |
| **ACE** | brevity bias / context collapse | 长度/抽象端的失败模式 |

### Cluster C — Confabulation, honesty, feedback

| 工作 | 核心发现 | 对你 |
|---|---|---|
| **Honest Lying** (Dixit 2026, arXiv:2605.29463) | memory confabulation；RRR；16 个 frozen ALFWorld 中 0/121 提到正确物体；2/16 memory-harmful，14/16 task-hard；grounded reflection / programmatic extraction 有效；更强模型只是换一种混淆 | 你的 H3 与 "honest lying" 的直接来源 |
| **Huang et al. 2024** (arXiv:2310.01798) | 无 oracle 的 self-correction 会降性能；约 70% 错误来自 verification | 为什么 writer 需要外部反馈 |
| **Illusions of Reflection** (2025, arXiv:2510.18254) | 反思收益常是 resampling；85% 重复同一失败类别 | 反驳"self-reflection 天然有益" |
| **The Mirror Loop** (2025, arXiv:2510.21861) | 自纠正需要独立外部 verifier | 与 Honest Lying 的 feedback granularity 一致 |
| **Memory Reward Inflation** (2026, arXiv:2608.00017) | Echo Gap：自评分虚高 | honesty gap 的定量近亲 |
| **HaluMem** (2026) | memory hallucination 检测 | 评测工具 |
| 认知科学：Johnson & Raye 1998; Schnider 2001; Chrobak & Zaragoza 2009 | source monitoring / confabulation | Honest Lying 的理论底座 |

### Cluster D — Writer / teacher / selection

| 工作 | 核心机制 | 对你 |
|---|---|---|
| **AgentBrew** (2026, arXiv:2607.16851) | 强 teacher 读学生失败轨迹，写 student-aware note；Ralph Loop 用 student recovery 认证；append-only skill bank；test time teacher 不在 | "better writer model" 的最直接前身；student-awareness + verification 是两个独立变量 |
| **SKILL-KD** (2026) | contrastive teacher–student trajectory → validated skill patches | 另一种 writer/verification |
| **CAFT** (2026, arXiv:2610.19367) | privileged expert critique + corrected action；训练学生生成 critique 再行动；比 action-only 蒸馏 +8% | 训练式 writer 的对照 |
| **JITMem** (2026) | read-time curator；RL 从 immediate task success 训练；transfer 到 GPT-5.4 | selection/curation 是独立设计变量 |
| ***When Should Experience Become Parameters?*** (2026, Zenodo 21175566) | selection gate（novelty vs recurrence）比 volume 更重要；LoRA 参数化 consolidation | "text note vs parameter" 的分界 |
| **SAMem** (ACL Findings 2026) | state-aware memory，thought–Q-value 排序 | utility prediction 的 RL 版本 |
| **Learning what to Remember** (IEEE 2026) | RL cost-aware write policy；80% less memory | write policy 的 RL 版本 |
| **ExpeL** | 更好的 insight LLM 有帮助；reflection 混入反而有害 | writer capability 的早期证据 |

### Cluster E — Consolidation: text vs parameters

| 工作 | 核心发现 | 对你 |
|---|---|---|
| **Hu 2026** | memory-level stability–plasticity；retrieval competition | 外部 memory 不是"免费"的 continual learning |
| ***When Should Experience Become Parameters?*** | selection not volume；LoRA consolidation | 你的 SFT/LoRA 组应该改成"note utility selector" |
| **From History to State** (2026, arXiv:2605.05413) | task-family LoRA + state tracker；constant context；Qwen3-8B ALFWorld 89.6%；tokens 2–7× 少 | 参数化记忆的强 baseline |
| **PEAM / MoMem / ExpRL** (2026) | parametric/non-parametric mixture | 混合记忆架构 |
| **Agent-FLAN** (2024, arXiv:2403.12881), **AgentTuning** (2023, arXiv:2310.12823), **LUMOS** (2024, arXiv:2311.05657) | agent SFT 的数据/格式/负样本/模块化 | 如果要做 SFT，先读这三篇；不要重复"task SFT 能提升" |

### Cluster F — Evaluation / benchmarks

| 类别 | 代表 | 关键点 |
|---|---|---|
| Agentic | ALFWorld (arXiv:2010.03768), ScienceWorld (arXiv:2203.07540), WebShop (arXiv:2207.01206), τ²-bench (arXiv:2406.12045), WebArena (arXiv:2307.13854), AgentBench (arXiv:2308.03688), BALROG (arXiv:2411.13543), AgentGym | 你的 ALFWorld 属于这一类；任务族难度高度不均 |
| Memory-specific | LongMemEval (arXiv:2410.10813), MemoryAgentBench (arXiv:2507.05257), MemBench (ACL Findings 2025), LoCoMo (arXiv:2402.17753), HaluMem, MemoryArena (arXiv:2602.16313) | 多为对话/多 session；MemoryArena 显示 recall 接近饱和的系统在 interdependent multi-session 任务上只有 0–23% |
| Surveys | Du 2026 (arXiv:2603.07670), Zhang 2025 (TOSEM, arXiv:2404.13501), *From Storage to Experience* (ACL 2026 Findings), *A Unified Representation–Management Perspective* (AACL 2026), *The AI Hippocampus* (arXiv:2601.09113) | 提供 write–manage–read / 3D taxonomy；可作为概念模型的上位框架 |
| Conceptual | CoALA (arXiv:2309.02427) | working / episodic / semantic / procedural memory + decision cycle |

---

## 4. 你的计划 → 已有工作 → 还剩什么

| 计划项 | 最接近的已有工作 | 已经确立 | 你的剩余空间 |
|---|---|---|---|
| **Better prompting** | ReAct, CoT, Self-Refine, Reflexion, ExpeL, ACE | prompt/representation 会大幅改变结果；1-shot vs 0-shot 约 5–15pp；self-refine 边界有限 | 不作为贡献；作为 control（固定 1-shot；0-shot 作为 robustness） |
| **Better writer model** | ExpeL（更好 insight LLM）、AgentBrew（teacher→student）、SKILL-KD、CAFT、JITMem、**MPO**（DPO 优化 per-family meta-plan） | 更强 writer/teacher 可以有帮助；student-aware + verification 很关键；memory 对弱模型帮助更大（MemoryTax） | writer capability × note semantics 的受控交互；student-aware vs teacher-level；actor 是否跟随；MPO-style 优化 plan 作为强 baseline |
| **Correctness × specificity 矩阵** | Kim 2026（内容特定）、MTL（trajectory/workflow/summary/insight）、Hu 2026（raw vs insight）、ACE（brevity）、Honest Lying（confabulation） | 抽象影响 transfer；正确性影响 harm；过具体导致 negative transfer | **完整 2×2 + 匹配长度/格式/位置 + realistic agentic task + note-level 方差 + harm rate**——这是最清楚的空白 |
| **Note length / template** | ACE（brevity bias）、Reflexion（1–3 条）、Honest Lying（grounded reflection）、结构化模板、**MPO**（query/observation/thought 三种注入方式） | 格式/长度会影响效果；不是越长越好；注入位置/方式有影响 | 匹配长度的因果测试；template/注入方式作为单因素 |
| **Irrelevant note** | Kim 2026 的 Mjunk | irrelevant ≈ inert | 在 ALFWorld 复现为负控制/harness sanity check |
| **Relevant-but-wrong** | Kim 2026、Honest Lying、Zhao 2026 | 可以伤害；会持久化 | 受控注入、harm rate、note-following |
| **Self-generated vs injected** | Reflexion、ExpeL、AgentBrew、JITMem | 生成可以有益；会 confabulate；read-time curation 更强 | 同一语义下生成 vs 注入的对照；writer 臂 |
| **Honesty gap** | Honest Lying（行为/RRR）、*What Is This Memory Useful For?*（utility）、Memory Reward Inflation（Echo Gap） | 行为层混淆已测；task-conditioned utility 已测 | **stated / predicted / behavioral 三分**；校准；note-level；与 RRR 的相关 |
| **Utility prediction / selection** | *What Is This Memory Useful For?*、JITMem、SAMem、MemRL、*When Should Experience Become Parameters* | task-conditioned；read-time curation；selection > volume | 训练/评估 note utility predictor；AUROC/calibration；跨任务 |
| **SFT / LoRA** | Agent-FLAN、AgentTuning、LUMOS、*When Should Experience Become Parameters*、*From History to State* | task SFT/RL 可以提升 agent；LoRA consolidation 可行 | 不要做 task SFT；做 **note utility selector**（小分类器/LoRA ranker），或 text vs parameter 对照 |
| **Model scale** | Reflexion（GPT-3.5/4）、MPO（7B/14B）、Honest Lying（3.5/4o-mini）、MemoryTax | scale 与 memory/harness 交互 | 同家族 7B vs 14B、固定 harness；note 敏感性 |
| **Architecture** | Reflexion（actor/evaluator/reflector）、ExpeL（insight LLM）、AgentBrew（teacher/student）、JITMem（curator）、**MPO**（generator/explorer/actor 分离） | 角色分离与反馈粒度重要；writer 与 actor 可以是不同模型 | 隔离 writer vs evaluator；actor-writer 简化；MPO 的 generator/explorer 分工 |
| **Cross-task transfer** | Hu 2026、MTL、ExpeL、AWM、ACE | 抽象帮助 transfer；hard/distant 任务负迁移 | note semantics × task distance 的 transfer matrix |
| **Conceptual model** | CoALA、Du 2026、Zhang 2025 | taxonomy / lifecycle | **因果 note-semantics 模型 + utility triple + 测量框架** |

---

## 5. 什么是真空白

把你的贡献压成三条，避免和已有工作重叠：

1. **受控的语义因果**：在同一 harness、匹配 length/format/position 下，操纵 **correctness × specificity**（并区分 relevance vs sufficiency），测 note-level 的 help/inert/harm 分布。已有工作分别研究了抽象（Hu/MTL）、正确性（Kim/Honest Lying/Zhao）、sufficiency（What Is This Memory Useful For），但没有把这个 2×2 在 realistic agentic task 上做成完整的受控设计。
2. **Utility 三分**：**stated utility**（用完后自评）、**predicted utility**（用前预测）、**behavioral utility**（配对 Δ）分开测，定义 honesty gap 并与 RRR/object-mention 解耦。Honest Lying 测了行为/RRR；What Is This Memory Useful For 测了 task-conditioned utility；没有人把三者放在同一 note-level 数据集上。
3. **Writer 侧的机制**：writer capability、student-awareness、verification 三个变量分开；检验"更强 writer"是否真的通过 correctness/specificity 提升 utility，还是只是换了一种 confabulation。AgentBrew 最接近，但它优化的是"学生能否恢复"，不是 note semantics 的因果分解。

**附带贡献**：note-level 方差作为现象（不是噪声）；hard-family harm rate；note utility predictor 的 calibration；ICL 与 note 的替代/交互。

---

## 6. 什么不要重做

| 不要做 | 原因 | 替代 |
|---|---|---|
| Reflexion vs no-memory | 已确立（+20% 量级） | 固定 1-shot，作为 baseline |
| abstract vs raw 的再证明 | Hu 2026 / MTL 已做 | 作为 specificity 轴的控制，不再当主贡献 |
| MPO-style meta-plan optimization 提升 task success | MPO 已证（per-family plan 可大幅提升弱模型） | 作为 Phase 2 的强 baseline，不再当主贡献 |
| task SFT 提升 agent | Agent-FLAN/AgentTuning/LUMOS 已做 | 训 note utility selector |
| generic better prompting | ReAct/CoT/Self-Refine 已做 | 作为 control |
| 跨论文绝对分数比较 | harness 差异可达 5×（13–75%） | 同 harness paired delta |
| "memory 可能有害" 的泛泛主张 | Honest Lying/Kim/Zhao 已证 | 给出机制、剂量-反应、harm rate |

---

## 7. Roadmap

### Phase 0 — Harness & baselines（已完成）

- ALFWorld 134 unseen，Qwen2.5-7B，1-shot **76.87%**，0-shot **70.15%**（−6.72pp，McNemar p=0.12）。
- 双 4090，vLLM 两实例；4-shard 并行。
- 关键 harness 控制：`put`→`move` 适配、lenient parser、30 步、8k、task-mix 分层。
- 结论：134 对 ~7pp 的效应功效不足；Phase 1 需要 note-level / within-task 设计。

### Phase 1 — Injection arm：因果语义（2–4 周）

**目标**：在 35 个 hard tasks（look_at_obj 18 + pick_two_obj 17）上做 2×2，再扩到 134。

**条件**（每个 task 注入同一位置、等长、同模板）：

| 条件 | 语义 |
|---|---|
| N0 | 无笔记 |
| N2 | 等长 filler（无语义） |
| I-C-S | 无关、正确、具体（跨任务族） |
| R-C-G | 相关、正确、泛泛 |
| R-C-S | 相关、正确、具体 |
| R-W-G | 相关、错误、泛泛 |
| R-W-S | 相关、错误、具体 |
| R-C-Suf | 相关、正确、**answer-bearing / sufficient** |

**测量**：success、steps、note-following、help/inert/harm、stated/predicted utility、honesty gap。

**分析**：paired by task；note-level 分布；mixed-effects（task random intercept）；McNemar；3 seeds 或 within-task 多 note。

**Gate**：如果 R-W-S 在 hard families 上不产生 harm，或 R-C-S 不产生 help，先检查 note 构建/注入位置/任务难度，不要直接扩到 134。

**要引**：Kim 2026、Honest Lying、Hu 2026、MTL、ACE、*What Is This Memory Useful For?*、*From Relevant Memories to Sufficient Evidence*。

### Phase 2 — Writer arm：生成、writer 质量、验证（4–6 周）

- 同一 task 重试 N 次；writer = 同 7B / 14B / 更强 teacher；
- 对照：teacher-level note vs student-aware note；verified（Ralph Loop）vs unverified；
- 自生成 vs 注入同一语义；
- note selection：top-k、utility predictor、calibration；
- **MPO 式 writer 训练**：用 explorer/执行反馈构造偏好对，DPO 优化 per-family meta-plan；作为 "optimized note" 强 baseline，与手写 R-C-S 对比；
- 测 confabulation：object-mention、RRR、false-success、harm。

**Gate**：如果 14B writer 不比 7B 好，检查是 correctness、specificity 还是 student-awareness 的锅。

**要引**：Reflexion、ExpeL、AgentBrew、SKILL-KD、CAFT、JITMem、Memory Reward Inflation、MemoryTax。

### Phase 3 — Consolidation & generalization（可选，4–8 周）

- text note vs LoRA selector；cross-family transfer；abstraction levels；retrieval；
- negative transfer matrix（task distance × specificity）；
- 不要做 task SFT；做 **note utility selector**。

**要引**：Hu 2026、*When Should Experience Become Parameters?*、*From History to State*、JITMem、MTL。

### Phase 4 — Measurement / conceptual paper

- note-level utility triple + benchmark + causal framework；
- 定位：Kim 2026（content-specific）、Honest Lying（confabulation/feedback）、Hu/MTL（abstraction）、What Is This Memory Useful For（task-conditioned utility）、ACE（context engineering）、AgentBrew（teacher-written notes）、JITMem（read-time curation）。

---

## 8. 先读这 11 篇

1. **Reflexion** (arXiv:2303.11366) — 术语与基线架构。
2. **Kim 2026**（本地 PDF）— note 内容特定性、负控制、方差。
3. **Honest Lying** (arXiv:2605.29463) — confabulation、RRR、feedback granularity。
4. **Hu 2026** (arXiv:2604.27003) — abstraction/transfer、negative transfer。
5. **Memory Transfer Learning** (arXiv:2604.14004) — trajectory→insight 的剂量-反应。
6. **Zhao 2026** (arXiv:2610.22984) — repair–generalization gap、failure misinterpretation。
7. **ACE** (arXiv:2510.04618) — brevity bias、context collapse、curator。
8. ***What Is This Memory Useful For?*** (arXiv:2611.03930) — task-conditioned utility、sufficiency。
9. **AgentBrew** (arXiv:2607.16851) — teacher-written、student-aware、verified notes。
10. **CoALA** (arXiv:2309.02427) + **Du 2026 survey** (arXiv:2603.07670) — 概念词汇与 write–manage–read 框架。
11. **MPO** (arXiv:2503.02682) — per-family meta-plan + DPO；你的 harness 与 75.4 baseline；"低质量 plan 会误导"的先声。

---

## 9. Bibliography（分组）

### Seeds
- Shinn et al. 2023. *Reflexion: Language Agents with Verbal Reinforcement Learning.* NeurIPS 2023. arXiv:2303.11366.
- Kim 2026. *Self-Written Notes Causally Steer Hypothesis Revision in a Small Language Model.* Preprint v0.3b.
- Dixit, Kamal, Oates 2026. *Honest Lying: Understanding Memory Confabulation in Reflexive Agents.* arXiv:2605.29463.
- Yao et al. 2022. *ReAct: Synergizing Reasoning and Acting in Language Models.* arXiv:2210.03629.
- Xiong et al. 2025. *MPO: Boosting LLM Agents with Meta Plan Optimization.* EMNLP 2025 Findings. arXiv:2503.02682.

### Reflective / experiential memory
- Madaan et al. 2023. *Self-Refine.* arXiv:2303.17651.
- Zhao et al. 2024. *ExpeL: LLM Agents Are Experiential Learners.* AAAI 2024. arXiv:2308.10144.
- Wang et al. 2025. *Agent Workflow Memory.* ICML 2025. arXiv:2409.07429.
- Zhang et al. 2026. *Agentic Context Engineering (ACE).* ICLR 2026. arXiv:2510.04618.
- Latimer et al. 2026. *Hindsight is 20/20.* ACL 2026 Demo. arXiv:2512.12818.
- Zhou et al. 2026. *Just-in-Time Memory.* arXiv:2609.27334.
- Park et al. 2023. *Generative Agents.* arXiv:2304.03442.
- Packer et al. 2023. *MemGPT.* arXiv:2310.08560.
- Zhong et al. 2023. *MemoryBank.* arXiv:2305.10250.
- Xu et al. 2025. *A-MEM.* arXiv:2502.12110.
- Chhikara et al. 2025. *Mem0.* arXiv:2504.19413.
- Wang et al. 2023. *Voyager.* arXiv:2305.16291.

### Content / abstraction / transfer
- Hu, Long, Wang 2026. *When Continual Learning Moves to Memory.* arXiv:2604.27003.
- Kim et al. 2026. *Memory Transfer Learning.* EMNLP 2026. arXiv:2604.14004.
- Zhao et al. 2026. *Self-Evolving Agents Can Repair Failures but Struggle to Generalize from Them.* arXiv:2610.22984.
- Yang et al. 2026. *What Is This Memory Useful For?* arXiv:2611.03930.
- *From Relevant Memories to Sufficient Evidence.* 2026. arXiv:2610.22668.*
- *Diagnosing Retrieval vs. Utilization Bottlenecks.* 2026. arXiv:2603.02473.*
- *Memory Reward Inflation in Self-Improving LLM Agents.* 2026. arXiv:2608.00017.*
- *MemoryTax: The Bitter Lesson of Agent Memory.* 2026. arXiv:2610.29823.*

### Confabulation / critique
- Huang et al. 2024. *Large Language Models Cannot Self-Correct Reasoning Yet.* ICLR 2024. arXiv:2310.01798.
- *Illusions of Reflection.* 2025. arXiv:2510.18254.*
- *The Mirror Loop.* 2025. arXiv:2510.21861.*
- Johnson & Raye 1998; Schnider 2001; Chrobak & Zaragoza 2009 (cognitive science of confabulation).
- *HaluMem* 2026 (memory hallucination benchmark).*

### Writer / selection / consolidation
- *AgentBrew: Lifelong Knowledge Brewing from Strong Teachers to Weak LLM Agents.* 2026. arXiv:2607.16851.*
- *SKILL-KD: Contrastive Skill Distillation for LLM Agents.* 2026.*
- *BEYOND CORRECTED ACTIONS: Training LLM Agents on Textual Critiques (CAFT).* 2026. arXiv:2610.19367.*
- *When Should Experience Become Parameters? Selection, Not Volume.* 2026. Zenodo 21175566.
- *From History to State: Constant-Context Skill Learning.* NeurIPS 2026. arXiv:2605.05413.
- *SAMem: State-Aware Memory.* ACL Findings 2026.*
- *Learning what to Remember: RL for Cost-Aware Memory.* IEEE 2026.*
- Agent-FLAN. ACL Findings 2024. arXiv:2403.12881.
- AgentTuning. 2023. arXiv:2310.12823.
- LUMOS. ACL 2024. arXiv:2311.05657.

### Benchmarks / surveys
- ALFWorld. arXiv:2010.03768.
- ScienceWorld. arXiv:2203.07540.
- WebShop. arXiv:2207.01206.
- HotpotQA. arXiv:1809.09600.
- HumanEval. arXiv:2107.03374.
- τ²-bench. arXiv:2406.12045.
- AgentBench. arXiv:2308.03688.
- WebArena. arXiv:2307.13854.
- BALROG. arXiv:2411.13543.
- AgentGym. arXiv:2406.04151.*
- LongMemEval. arXiv:2410.10813.
- MemoryAgentBench. arXiv:2507.05257.
- MemBench. ACL Findings 2025.*
- LoCoMo. arXiv:2402.17753.
- MemoryArena. 2026. arXiv:2602.16313.*
- Du 2026. *Memory for Autonomous LLM Agents.* arXiv:2603.07670.
- Zhang et al. 2025. *A Survey on the Memory Mechanism of LLM-based Agents.* TOSEM. arXiv:2404.13501.
- *From Storage to Experience.* ACL 2026 Findings.*
- *LLM Agent Memory: A Unified Representation–Management Perspective.* AACL 2026.*
- *The AI Hippocampus.* arXiv:2601.09113.*

### Conceptual
- Sumers et al. 2023. *Cognitive Architectures for Language Agents (CoALA).* arXiv:2309.02427.
- Tulving 1972/1983 (episodic/semantic memory).
- Baddeley & Hitch 1974 (working memory).
- Johnson, Hashtroudi, Lindsay 1993 (source monitoring).
- McClelland, McNaughton, O'Reilly 1995 (complementary learning systems).
- Graves et al. 2016 (Neural Turing Machine); Ramsauer et al. 2021 (Hopfield networks).
- Lewis et al. 2020 (RAG).
- von Oswald et al. 2023 (in-context learning as gradient descent).

---

## 10. 仍然开放的问题

1. **Correctness 还是 specificity 是主效应？** 两者是否有交互（wrong-specific 最毒）？
2. **correct-generic 到底有没有用？** 如果没用，那"泛泛的正确建议"就是一种 inert note。
3. **sufficiency 能否解释大部分方差？** 相关但不够的笔记是否和无关笔记一样 inert？
4. **1-shot ICL 与 note 是替代还是互补？** note 效应是否在 0-shot 下更大？
5. **更强 writer 的提升来自 correctness、specificity，还是 student-awareness？**
6. **actor 能否预测 note utility？** honesty gap 是否跨模型稳定？
7. **negative transfer 是否随 task distance 单调上升？** hard cases 是否最敏感？
8. **note-level 方差有多大？** 条件均值是否系统性地误导？
9. **text note vs LoRA selector**：在相同信息量下，哪种 substrate 更有效？
10. **evaluation**：能否做一个 note-level benchmark，同时报告 behavioral/stated/predicted utility 和 harm rate？
