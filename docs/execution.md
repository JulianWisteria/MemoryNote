Model = Qwen-2.5-7B-Instruct,  Qwen-2.5-14B-Instruct [Optional]

Harness = 1-shot ReAct

Task = 134 held-out ALFWorld (6 task family)

Baseline = no note 



Core Experiment: Clarity * Correctness 矩阵



Clarity 有 (ambiguity, operational, over-specify) 三个维度。

例子 (look_at task)：

- Ambiguous: Make sure the object is properly lit before you check it.
- Operational: Pick up the object, go to the desklamp, and use the desklamp while holding it.
- Over-specific: Pick up bowl 1 from desk 2, go to shelf 3, and use desklamp 1.

Correctness 有 (correct, wrong) 两个维度。

例子 (look_at task)：

- Correct: Pick up the object, go to the desklamp, and use it while holding the object.
- Wrong: Turn on the desklamp first; you do not need to pick up the object.



具体实验过程是：对每个 clarity * correctness 等级有六个对不同 task_family 的笔记，当 agent 执行每个 task 的时候把对应 task_family 的笔记 inject 到 task instruction 后面。

这意味着写笔记的同学需要写 36 条笔记，这不算困难，每个笔记只有一两句话。但是一定要手写英文！一定至少要看过每个 task_family 是什么任务和典型解决方案是什么，可以看 agent 交互轨迹或者找 ALFWorld 官网。

可以写完一个 clarity * correctness 等级后就提交到github，做实验的同学可以马上开展实验，不用等到 6 个等级都写完。



笔记例子：(Operational + Correct)

| Task family               | Note                                                                                                                                                                                                                           |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **pick_and_place**        | "Find the object the task asks for. Pick it up, go to the place where it should go, and put it there. If a container is closed, open it first."                                                                                |
| **look_at_obj**           | "Find the object the task asks for. Pick it up, go to the desklamp, and use the desklamp while you are still holding the object."                                                                                              |
| **pick_clean_then_place** | "Find the object, pick it up, and go to a sinkbasin. Clean the object with the sinkbasin, then go to the place named in the task and put it there."                                                                            |
| **pick_heat_then_place**  | "Find the object, pick it up, and go to a microwave. Heat the object with the microwave, then go to the place named in the task and put it there."                                                                             |
| **pick_cool_then_place**  | "Find the object, pick it up, and go to a fridge. Cool the object with the fridge, then go to the place named in the task and put it there."                                                                                   |
| **pick_two_obj**          | "Find one object, pick it up, and put it in the place named in the task. Then look for a second object of the same kind, pick it up, and put it there too. Check your hands to make sure you are not still holding something." |

