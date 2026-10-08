# I-05 · Tune the L1 baseline

**Hypothesis.** The default L1 settings (predictor pole 10 1/s, filter 5 rad/s) are not optimal for this vehicle and task
distribution; a tuned L1 narrows the gap to the learned residual.

**Tests claim:** C1 ("2.1x lower than L1"). **Undercuts C1:** tuned L1 approaches 7–8 cm. **Supports C1:** tuned L1 stays well
above the residual.

**Design.** Grid: predictor pole in {5, 10, 20, 40} 1/s × filter bandwidth in {2, 5, 10, 20, 40} rad/s. Select on 32
*training* tasks (seed 0 of the training sampler) × 4 episodes; evaluate the selected setting and the default on the fixed
32 held-out and 32 OOD tasks × 4 episodes. **Metrics:** RMSE (cm), crash rate. **Compute:** 9.8 s per configuration
on 32 × 4 episodes → ≈ 5 min.
