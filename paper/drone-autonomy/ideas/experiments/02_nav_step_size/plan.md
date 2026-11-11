# I-02 · Is "adaptation hurts navigation" a step-size artefact?

**Hypothesis.** The decline of MAML-family navigation planners with adaptation (C6) is caused by an inner step
too large for 10 sparse-reward episodes, not by gradient adaptation as such.

**Tests claim:** C6. **Supports C6:** every step size declines. **Undercuts C6:** smaller steps hold success near the
pre-adaptation level (then C6 is about the meta-trained step size). **Data-budget variant:** 30 exploration episodes
per stage at the original step.

**Design.** Seed-0 navigation checkpoints of MAML and Meta-SGD (MAML: scalar step 0.1; Meta-SGD: learned per-parameter
steps), inner step scaled by 1, 0.3, 0.1; plus MAML with 30 exploration episodes per stage at scale 1. Privileged
planner, 16 held-out tasks, each episode in its own unseen test room, 3 stages, 4 deterministic evaluation episodes.
Everything else as in the benchmark. **Metrics:** success and collision per stage.
**Compute.** Pilot: 4 tasks × 1 stage = 89 s on the loaded CPU → ≈ 5 min per curve, 7 curves in parallel.
