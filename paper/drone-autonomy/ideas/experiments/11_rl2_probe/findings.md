# I-11 findings: no evidence that RL²'s state encodes the dynamics; RL² did not improve in this run

Source: `results/rl2_probe.json` (seed-0 navigation checkpoint, 64 tasks drawn from the training ranges with seed 40004,
one 3-episode trial per task, all three episodes in the same unseen test room).

- **Success per episode of the trial:** 56% → 59% → 58%. The benchmark's rise from 55% to 71% did **not** reproduce here.
  Two differences may matter: these tasks are a fresh draw, and under the corrected protocol each trial stays in one room,
  whereas in the original benchmark every episode was drawn at random from the pool.
- **Probe R² (ridge, 5-fold CV, 128-d state, 64 tasks):** negative for every parameter at every point (end of episode
  1: mass −0.51, weakest motor −1.44, wind −0.84, latency −1.11; similar after episodes 2 and 3 and after 10 steps).
  The linear probe predicts worse than the mean.

**Caveats.** 64 samples for a 128-dimensional state makes the probe weak (negative CV R² can also mean overfitting at
λ = 1); a negative result is not proof that no task information is present.

**Effect on the paper.** This **undercuts the RL² half of C6** ("RL² is the only method that improves with
experience") and gives no support to the task-inference explanation. The re-benchmark under the corrected protocol
(distinct rooms, still running) will decide what the paper can say about RL².
