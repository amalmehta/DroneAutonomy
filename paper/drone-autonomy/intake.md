# Intake: Meta-learning meets classical control and planning for quadrotor adaptation (working title)

Sources read: `results/summary.json`, `results/<problem>/<method>_seed<k>.json` (benchmark output),
`runs/*/*/seed*/log.jsonl` (training logs), `drone_autonomy/` (code), `docs/SYSTEM-DESIGN.md`,
`docs/DRONE-SELECTION.md`, `website/data/demo.json`, `drone_autonomy.md`.

Metric conventions (from code): tracking RMSE in metres over a 4 s episode (200 steps at 50 Hz) (`envs/tracking.py:metrics`),
crashed episodes count 1.5 m error for their remaining steps; navigation success = within 0.5 m of goal
before collision or 30 s timeout. Means are over tasks × seeds; ± is a 95% normal interval over tasks × seeds
(`figures.py:curve`). "After adapting" = after 3 stages (gradient methods: 30 episodes; PEARL / RL²: 3 episodes).

## Claims

| # | Claim | Evidence (file → fields) | Status |
|---|---|---|---|
| C1 | A learned residual on top of the geometric controller cuts held-out tracking error about 3× vs the nominal controller and 2× vs L1 adaptive control (21.4 / 15.5 → 7.3 cm). | summary.json → tracking_residual: classical, l1, dr `test_post` | supported (2 seeds; classical/L1 deterministic, 1 run) |
| C2 | Gradient meta-learners (MAML, FOMAML, ANIL, Meta-SGD) improve with adaptation (8.5–8.7 → 7.7–7.8 cm after 30 episodes) but do not beat the non-adapting domain-randomised residual (7.3 cm); intervals overlap. DR + fine-tuning gets slightly worse (7.3 → 8.0 cm). | tracking_residual: maml/fomaml/anil/metasgd/dr/dr_finetune `test_pre`, `test_post`, `test_post_ci` | supported |
| C3 | Meta-learning helps most when it tunes the classical controller's gains: Meta-SGD 15.6 → 11.3 cm vs 14.2 cm for DR-tuned gains + fine-tuning; MAML/FOMAML 13.7/13.9 cm. | tracking_gains: all rows | **partial** — Meta-SGD vs DR intervals (±2.0, ±1.9 cm) barely separate; 2 seeds |
| C4 | Context-based meta-RL adapts with far less data on the residual task: PEARL 10.5 → 9.0 cm from 3 episodes; RL² 18.4 → 17.4 cm. | tracking_residual: pearl, rl2 | supported |
| C5 | On the full stack (online mapping + A*) in unseen rooms, the classical local planner is the most reliable: 83% success, 0 collisions; learned local planners reach 17–75% with 25–83% collisions. | navigation: `full_test_success_post`, `full_test_collision_post` | **partial** — 12 rooms, 1 seed (one room = 8 points) |
| C6 | Gradient-based adaptation makes learned navigation planners worse as it proceeds (MAML 79 → 45%, FOMAML 80 → 36%, ANIL 83 → 47%, Meta-SGD 76 → 42%, Reptile 80 → 62%, DR fine-tune 82 → 72%), while RL² is the only method that improves with experience (55 → 71%). | navigation: `test_pre`, `test_post`; per-stage curves in results/navigation/*.json | supported for this setup (1 seed, 24 tasks) |
| C7 | A map + planner matters: end-to-end RL without them reaches 50% vs 82% for the same learner with the planner (privileged-planner setting), 42% vs 67% on the full stack. | navigation: e2e_dr vs dr | supported (1 seed) |
| C8 | Out of distribution, every method fails (tracking error ≥ 63 cm, navigation success ≤ 21%), and learned residuals crash more often (43–52%) than the plain controller (34%). | tracking_residual `ood_post`, `ood_crash`; navigation `ood_post` | supported |
| C9 | Recommended real platform: Holybro X500 V2 + Jetson Orin Nano Super + RealSense D435i, because PX4 offboard accepts the policies' thrust + body-rate commands and the camera matches the simulated sensor; with a staged sim-to-real plan. | docs/DRONE-SELECTION.md (desk research, sources cited there) | supported as a recommendation; **no real flights** |

## Facts I still need from you
- **Author list and affiliations** (or should the draft carry placeholders?).
- **Title** (working title above is mine).
- **Which venue/cycle**, if any: a specific conference (e.g. ICRA 2027, IROS 2027) sets the page limit and review mode, or a generic IEEE conference-format preprint.
- **AI-use disclosure:** the code, simulator, experiments and benchmark were built and run with Claude Code in this project, and the draft will be written with the paper-writer skill. The disclosure has to say this; confirm how you want it worded.

## Disagreements between inputs
- **Combo 3 action space.** The early plan said the RL local policy outputs thrust + body rates; the code outputs a velocity command tracked by the classical controller (`envs/navigation.py`). The paper will describe the code.
- **Unequal starting points on navigation.** MAML/FOMAML/ANIL/Meta-SGD/Reptile start from the trained DR planner (`methods.py: WARM_START`); PEARL and RL² train from scratch. Must be stated as a confound.
- **Navigation Reptile was re-run** with a 10× smaller inner step after diverging (failed run in `runs/failed/`); DR fine-tune on navigation also uses the smaller step. Must be reported.
- **"Domain-randomised PPO" on the gains problem** is a parameter-exploring policy gradient with a PPO-clipped surrogate over the 7 gains, not PPO over a step policy. The paper should name it accordingly.
- **Simulator parameters** for the X500 are partly estimated (thrust-to-weight, motor lag, drag) — DRONE-SELECTION.md marks them.
- **Seeds:** tracking 2, navigation 1; classical and L1 baselines are deterministic controllers evaluated once.

## Status after the corrected benchmark (2026-10-08)
- C3: **firm** — 5 seeds; paired improvement 3.5 cm (95% bootstrap 2.8–4.3), Meta-SGD better on 83% of pairs.
- C5: **firm** — classical planner 73% success / 7% collisions over 96 unseen-room flights (48 rooms × 2 seeds); learned 31–55%.
- C6: **restated** — degradation holds at the meta-trained step size with 10 episodes/update (I-02 step-size sweep); RL² part **dropped** (60 → 55%, no improvement).
- C7: **revised** — carrot/planner helps a learned planner with the privileged planner (72 vs 52%) but not on the online map (44 vs 51%).
- C1: confirmed against a tuned L1 baseline (14.0 cm).
