# I-11 · Does RL²'s hidden state encode the dynamics?

**Hypothesis.** RL² improves over a trial because its recurrent state infers the task's dynamics.

**Tests:** the explanation offered for RL²'s rise in C6. **Supports:** cross-validated probe R² for the task parameters
rises from episode 1 to episode 3. **Undercuts:** R² near zero or flat (its gain then comes from something else, e.g. room
exploration).

**Design.** Navigation RL² seed-0 checkpoint; 64 held-out tasks (fixed seed), one 3-episode trial each, privileged
planner, each trial in its own unseen room. Record the GRU state at the end of each episode. Ridge regression (5-fold
CV) from the state to each task parameter (mass scale, weakest-motor efficiency, wind speed, latency), per episode
index. Control: the same probe on the state after the first 10 steps of episode 1. **Compute:** ≈ 10 min.
