# I-05 findings: tuning the L1 baseline

Source: `results/l1_tuning.json` (wall time 79 s).

- **Grid (20 settings, 32 training tasks × 4 episodes).** Best: predictor pole 10 1/s, filter bandwidth 40 rad/s,
  14.0 cm training RMSE, against 15.3 cm for the default (10 1/s, 5 rad/s). Error falls as the filter bandwidth rises
  and flattens at the top of the grid (cutoff 20 → 40 rad/s: 14.3 → 14.0 cm at pole 10), so a wider grid would gain
  little more. No setting crashed on the training tasks.
- **Held-out (32 tasks × 4 episodes, same episodes for both):** default 14.9 cm → tuned 14.0 cm, no crashes.
- **OOD:** default 66.9 cm (44% crashes) → tuned 63.5 cm (45% crashes).

**For the paper.** Tuning improves L1 by about 1 cm on held-out tasks, so C1 stands: the DR residual (7.3 cm in the
benchmark) is still about 2× better than a tuned L1. The default L1 in this experiment scores 14.9 cm rather than the
benchmark's 15.5 cm because its reference trajectories come from a different random draw; compare default and tuned only
with each other. Suggested change: report the tuned L1 alongside the default (one sentence plus a sources row), and
keep the 2× claim with "tuned".
