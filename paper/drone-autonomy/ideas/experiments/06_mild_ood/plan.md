# I-06 · A "mild OOD" split just beyond the training ranges

**Hypothesis.** Learned methods degrade gracefully just outside the training ranges; the failures in the paper's OOD
split come from conditions far outside them.

**Tests claim:** C8. **Narrows C8:** learned methods stay close to their held-out error on mild OOD while the
classical controller does not crash less. **Strengthens C8:** learned methods already crash more than the classical
controller on mild OOD.

**Design.** Each parameter drawn just beyond its training range: payload ×1.30–1.35, weakest motor 70–75%, drag ×2.0–2.3,
wind 2.5–3.0 m/s, gusts 0.8–0.95 m/s, latency 30–40 ms. 32 tasks (fixed seed 30003) × 4 deterministic episodes, after
0 and 3 adaptation stages, for every tracking method and both seeds 0, 1 (seeds 2–4 of the gain problem are still
training). **Metrics:** RMSE (cm), crash rate. **Compute:** ≈ 40 min on 4 workers.
