# I-02 findings: the navigation decline is a step-size and data-budget effect

Source: `results/*.json` (seed-0 checkpoints, 16 held-out tasks × 4 episodes, each episode in its own unseen test room,
privileged planner; wall time 385–558 s per configuration).

| Configuration | Success by stage 0 → 1 → 2 → 3 | Collisions at stage 3 |
|---|---|---|
| MAML, step ×1, 10 ep./stage (as in the paper) | 69 → 58 → 39 → 25% | 69% |
| MAML, step ×0.3 | 69 → 75 → 64 → 66% | 34% |
| MAML, step ×0.1 | 69 → 72 → 70 → 72% | 28% |
| MAML, step ×1, 30 ep./stage | 69 → 75 → 62 → 64% | 36% |
| Meta-SGD, learned steps ×1 (as in the paper) | 67 → 64 → 50 → 38% | 58% |
| Meta-SGD, ×0.3 | 67 → 69 → 67 → 73% | 27% |
| Meta-SGD, ×0.1 | 67 → 70 → 69 → 70% | 30% |

**What it shows.** The decline reproduces at the meta-trained step size with 10 episodes per update. It disappears
with a 3–10× smaller step, or with 3× more exploration episodes at the original step. Those variants hold success
roughly at or a little above the pre-adaptation level (+3 to +6 points at best), so adaptation then neither helps nor
hurts much.

**Effect on the paper.** This **undercuts C6 as worded** ("gradient-based adaptation degrades learned navigation
planners"). The supported version: with the step size meta-learned on tracking-scale budgets and 10 sparse-reward
episodes per update, adaptation degrades the planner; a smaller step or more data removes the degradation but gives
little gain. The noisy-gradient explanation in the draft fits: the problem is the size of noisy updates, not the
direction of adaptation. One seed and 16 tasks; the re-benchmark under the corrected room protocol is still running.
