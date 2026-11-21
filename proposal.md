# 自写笔记的语义如何决定其效用
### 一个受控的 Agent 记忆研究 · Proposal v0.1

---

## 1. 问题

Reflexion 类 agent 在失败后写一段自然语言反思，存入 memory 并在后续 trial 中复用；社区默认这套机制有益。两篇 2026 年的工作动摇了这个前提：

- **Kim 2026**（GPT-OSS-20B，合成 XOR/AND 世界）用配对因果设计证明：同一条自写笔记让 XOR 的 miss 从 27/48 降到 7/48，却让 AND 从 5/24 升到 23/24；等长无关笔记则完全无效（27 vs 27）。三条复现链的结果从 1/48 到 46/48 剧烈分化。
- **Honest Lying**（Reflexion，ALFWorld/WebShop/HotpotQA/HumanEval）发现 agent 会把自信但错误的自我诊断写入 memory 并跨 trial 复用：16 个 frozen 环境中 0/121 条反思提到正确目标物体；其中 2/16 移除 memory 反而解得更好。换更强模型并未消除问题，只是把 task-identity 混淆换成 action-space 混淆。

两篇留下同一个空白：**笔记的效用不是二元属性，而是由语义决定的、高方差的干预；"内容是否正确"与"模型是否知道它有用"从未被分开测量。**

本文论点：自写笔记是高方差、内容依赖的干预；效应符号可由 **相关性 × 正确性 × 具体性** 预测；模型无法预判自身笔记的效用（honesty gap），且该失败与内容混淆可分离。

**三个可证伪假设**

- **H1（语义因果）**：在长度、格式、位置、反馈粒度全部匹配的前提下，相关性、正确性、具体性各自独立地决定效应符号。
- **H2（方差即现象）**：以单条笔记为分析单位，效应分布跨任务族剧烈分化；条件均值会掩盖它。
- **H3（诚实差距）**：stated / predicted utility 与 behavioral utility 解耦，且该 gap 与 RRR、object-mention rate 仅弱相关。

---

## 2. 设计

### 2.1 两个臂

| 臂 | 做法 | 回答 | 阶段 |
|---|---|---|---|
| **注入臂** | 笔记由我们构造或筛选，绕过生成直接注入 | 语义的因果效应 | 主线，Phase 0–1 |
| **生成臂** | 模型自己写（actor-writer / Reflexion） | 真实场景下效应是否仍在 | 外部效度，Phase 2 |

先注入、后生成。Kim 的教训是"整条笔记的效应"无法归因到具体措辞；只有注入臂能一次只动一个维度。

### 2.2 固定设置

- **架构**：actor-writer（行动 → 环境反馈 → 写笔记 → 下次带笔记再行动）。Reflexion 三件套仅作消融，因为多一个 LLM evaluator 就多一个混淆源，而环境本身已提供 evaluator。
- **模型**：Qwen3-8B / 14B Instruct。规模是 **moderator**（8B vs 14B 的交互项），不是独立实验组。可选 gpt-4o-mini 在 30 个 env 上做 anchor。
- **任务**：ALFWorld `eval_out_of_distribution`，134 env。自动判定 success，无需 LLM judge；二值反馈是"记忆有害"的已知触发条件。
- 主实验 T=0；子集 T=0.7 × 3 seeds 做方差检查。

### 2.3 条件

| 组 | 条件 | 操纵 |
|---|---|---|
| 基线 | N0 无记忆 | — |
| | N1 强提示（CoT + 失败后反思重试，无持久记忆） | prompt |
| | N2 填充笔记（等长、无语义内容） | 长度/格式负控制 |
| 语义 2×2 | R-C-S 相关·正确·具体 | 上界参照 |
| | R-C-G 相关·正确·泛泛 | 具体性 |
| | R-W-S 相关·错误·具体 | **有害** |
| | R-W-G 相关·错误·泛泛 | 交互 |
| 无关 | I-C-S 无关·正确·具体（跨任务族） | 相关性 |
| 锚点 | A1 自生成笔记 | 生态效度 |
| | A2 人类 oracle 笔记 | 上界 |

**注意**：无关笔记不是待检验的条件，而是 harness 的负控制。若 I-C-S ≠ N0，说明长度/格式/显著性有混淆，先修 harness 再谈科学。

Phase 0 只跑 5 个条件：N0、N2、R-C-S、R-W-S、I-C-S。Phase 1 补全因子。

### 2.4 指标与统计

- **主指标**：10 trials 内是否解出；trials-to-solve。
- **机制指标**：note-following rate（注入指向特定动作的笔记，测动作是否转向）、RRR、object-mention rate。
- **元认知指标**：stated utility（用后问）、predicted utility（用前问）；honesty gap = P(说有用 | 行为有害) + P(说没用 | 行为有益)。
- **统计**：env 配对 McNemar；混合效应 logistic（env 随机截距）；TTS 用配对 bootstrap；报告 note-level 效应分布与 ICC；主对比预注册，Holm 校正。

### 2.5 必须锁死的混淆

1. **长度/格式**：所有笔记 token 数匹配到自生成笔记中位数，报告分布。
2. **放置**：固定位置、always-on，不做检索。
3. **反馈粒度**：所有条件同一种反馈，不混用 "Nothing happens" 与 unit test。
4. **难度分层**：只保留 pilot 中 0.15 < p_solve < 0.85 的 env。
5. **答案泄漏**：笔记只到策略级（"先 open 再 take"），不到答案级（"mug 在咖啡机里"）。

---

## 3. 要做什么

| 阶段 | 周 | 内容 | 产出 | 算力 | 决策门 |
|---|---|---|---|---|---|
| P0a | 1 | 20 env × 10 trials，无记忆，仅 8B | p_solve 分布、token 长度、错误指令顺从率 | 2–4 GPU·h | 中间难度 env ≥ 40 个，否则换 14B 或换任务 |
| P0b | 2 | 16 frozen + 16 matched，5 条件，8B | 注入臂是否有信号、负控制是否干净 | 8–12 GPU·h | I-C-S ≈ N0；否则修 harness |
| P1 | 3–6 | 134 env × 8 条件 × 10 trials × 2 模型 | 主结果 + H1/H2 | 80–150 GPU·h | — |
| P1.5 | 6 | GSM8K 500 题 × 全因子 | 泛化 | <5 GPU·h | — |
| P2 | 7–10 | 生成臂、架构消融、笔记效用预测器 | 机制与缓解 + H3 | 30–60 GPU·h | 预测 AUC > 0.65 才值得训筛选器 |

**预算**：单卡 A100 约 20–25 GPU·h/天，全量 150–250 GPU·h；4 卡约一周，租卡约 $300–600。**瓶颈是 harness 工程，不是算力。**

**本周三件事**（可并行）：
1. 搭 ALFWorld + vLLM 的 ReAct harness，预留 note 注入接口（owner：___）。
2. 写 note taxonomy v0 + 50 条样例；两人独立标注 relevance/correctness/specificity，报告 Cohen's κ（owner：___）。
3. 跑 P0a，产出 p_solve 与 token 长度表（owner：___）。

---

## 4. 风险

| 风险 | 对策 |
|---|---|
| 8B 在 ALFWorld 上 floor/ceiling | P0a 决策门；回退 14B 或只取中间难度子集 |
| 笔记长度成为真正自变量 | token 匹配 + N2 填充控制 + 报告分布 |
| 反馈粒度混淆 | 所有条件共用同一反馈生成器 |
| honesty 测量对 prompt 敏感 | 三种测量三角互证，先在 50 条笔记上定格式 |
| 多重比较 | 预注册 3 个主对比（R-W-S vs R-C-S、I-C-S vs N0、R-C-G vs R-C-S） |

**成功标准**：P1 结束时，若 H1 成立（R-W-S 显著劣于 R-C-S，且 I-C-S ≈ N0），且 H3 的 honesty gap 可测，即构成一篇 workshop 论文；P2 的预测器把它推成主会投稿。
