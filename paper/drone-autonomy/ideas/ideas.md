# Improvement ideas: Where Does Meta-Learning Help a Quadrotor?

> Mode: own draft · Generated 2026-10-06 · Budget: CPU, ≤ 30 min per experiment, ≤ 2 h per round (shared, loaded machine) ·
> Excluded because already running: extra seeds for C3, 48-room full-stack evaluation and a second navigation seed for C5.

## Ranked ideas

| # | Idea | Type | Impact | Effort | Compute | Literature | Status |
|---|---|---|---|---|---|---|---|
| I-01 | Position against MAVEN, RAPTOR and RL gain-tuning work missing from Related Work | reviewer | High | 1 h | none | related work | applied |
| I-02 | Is "adaptation hurts navigation" a step-size artefact? Sweep the inner step at test time | evidence | High | 2 h | ≈ 30 min | related work | done |
| I-03 | Report training samples per method; check that DR didn't simply see more data | reviewer | High | 1 h | none | not applicable (presentation) | applied |
| I-04 | Paired per-task test for C3 instead of overlapping intervals | evidence | High | 1 h | < 1 min | not applicable (presentation) | done |
| I-05 | Tune the L1 baseline as carefully as the learners | reviewer | High | 1.5 h | ≈ 5 min | related work | done |
| I-06 | Add a "mild OOD" split just beyond the training ranges | evidence | Medium | 2 h | ≈ 40 min | no close match | done |
| I-07 | Say in the text that MAML-family methods were meta-trained for one inner step, and report stage 1 separately | writing | Medium | 0.5 h | none | not applicable (presentation) | applied |
| I-08 | Put "in simulation" into the title and contributions | writing | Medium | 0.2 h | none | not applicable (presentation) | applied |
| I-09 | Cite or soften the "usually compared on locomotion benchmarks" gap statement | writing | Medium | 0.3 h | none | related work | applied |
| I-10 | Split Fig. 2 so the context methods' 1-episode stages aren't read on the 10-episode axis | writing | Medium | 1 h | < 1 min | not applicable (presentation) | applied |
| I-11 | Probe the RL² hidden state for task parameters to explain why it alone improves | direction | Medium | 2 h | ≈ 10 min | related work | done |
| I-12 | Stress-test with aerodynamics the learners never saw (quadratic drag, ground effect) | reviewer | Medium | 3 h | ≈ 30 min | related work | proposed |
| I-13 | Meta-learn a residual on top of L1 instead of the nominal controller | direction | Medium | 3 h | ≈ 3 h (over budget; 1-seed shortened pilot ≈ 30 min) | related work | proposed |
| I-14 | Gate gradient adaptation on navigation with a safety check (reject updates that raise exploration collisions) | direction | Medium | 3 h | ≈ 30 min | related work | proposed |

## Details

### I-01 · Position against MAVEN, RAPTOR and RL gain-tuning work missing from Related Work
- **Type:** reviewer · **Impact:** High · **Effort:** 1 h · **Compute:** none
- **Motivated by:** Related Work (Sec. II) cites only 2021–2023 flight-adaptation work; the second gap claim in the Introduction says meta-RL methods are "usually compared with each other on locomotion benchmarks".
- **Idea:** *A reviewer may say* recent work already applies meta-RL to quadrotors with varying dynamics and tunes controller gains with RL → add a positioning paragraph citing MAVEN (meta-RL for varying-dynamics agile flight), RAPTOR (one adaptive policy across many quadrotors), RL-predicted PID/PD gains for quadrotors, and safe-control-gym as a related benchmark, stating that this paper's difference is the head-to-head of seven meta-learners against classical and L1 baselines at three insertion points of one stack. Verify each record with paper-writer's citation check before citing.
- **Why it matters:** novelty is the first thing robotics reviewers check; missing 2024–2026 quadrotor meta-RL work reads as unawareness.
- **Literature:** related work — [MAVEN, arXiv:2603.10714](https://arxiv.org/abs/2603.10714) (closest: meta-RL across varying quadrotor dynamics); [RAPTOR, arXiv:2509.11481](https://arxiv.org/abs/2509.11481) (adaptive foundation policy for quadrotor control); [Sönmez et al., arXiv:2502.04552](https://arxiv.org/abs/2502.04552) (RL predicts PID gains for quadrotors, related to Combination 2); [Multi-Task RL for Quadrotors, doi:10.48550/arxiv.2412.12442](https://doi.org/10.48550/arxiv.2412.12442); [safe-control-gym, doi:10.1109/lra.2022.3196132](https://doi.org/10.1109/lra.2022.3196132) (benchmark for learning-based control).
- **Status:** applied — Related Work cites MAVEN, RAPTOR, multi-task RL, RL-predicted PID gains and safe-control-gym, with a positioning sentence (7 new entries, all verified)

### I-02 · Is "adaptation hurts navigation" a step-size artefact? Sweep the inner step at test time
- **Type:** evidence · **Impact:** High · **Effort:** 2 h · **Compute:** ≈ 30 min (pilot: 4 tasks × 1 stage = 89 s on the loaded CPU)
- **Motivated by:** Results, "Adaptation hurts learned navigation planners, except RL²": MAML 79 → 45%, FOMAML 80 → 36% (Table III), explained as "noisy policy gradients from 10 sparse-reward episodes per task overwriting a competent planner".
- **Idea:** For the MAML-family navigation checkpoints, re-run the privileged-planner adaptation curve with the inner step scaled by 1, 0.3 and 0.1 (and one stage with 3× more exploration episodes). Run it in `ideas/experiments/`; the originals stay untouched.
- **Why it matters:** C6 is the paper's most surprising claim and currently rests on one step size.
- **What would change the conclusion:** if smaller steps stop the decline (success stays near the pre-adaptation level), C6 becomes "with the meta-trained step size, adaptation hurts", a tuning issue rather than a property of gradient adaptation. If every step size declines, C6 strengthens and the noisy-gradient explanation gains support. If more episodes fix it, the claim is about the data budget.
- **Literature:** related work — [Safe Meta-RL via Information Space Reachability, arXiv:2609.15915](https://arxiv.org/abs/2609.15915) and [MESA, arXiv:2112.03575](https://arxiv.org/abs/2112.03575) (both treat unsafe behaviour during adaptation as a problem to constrain); [Arndt et al., doi:10.1109/icra40945.2020.9196540](https://doi.org/10.1109/icra40945.2020.9196540) (meta-RL adaptation for sim-to-real).
- **Status:** done — decline only at the meta-trained step with 10 ep./update (MAML 69→25%); ×0.1–0.3 steps or 3× data hold 64–73%. Undercut C6 as worded; user chose to restate C6 and add the sweep as Table V. See experiments/02_nav_step_size/findings.md

### I-03 · Report training samples per method; check that DR didn't simply see more data
- **Type:** reviewer · **Impact:** High · **Effort:** 1 h · **Compute:** none (read from configs and logs)
- **Motivated by:** Results, "Gradient-based meta-learning adds little to the residual": DR reaches 7.3 cm vs 7.7–7.8 cm; the paper never states environment steps per method (`methods.py: ITERS` differs: DR 300 iterations, MAML 150, Reptile 120, PEARL 300, RL² 150).
- **Idea:** *A reviewer may say* DR wins because it was trained longer → add a column or sentence with environment steps per method, computed from iterations × tasks × episodes × horizon (e.g. DR 300 × 16 × 10 × 200 and MAML 150 × 2 × 16 × 10 × 200 are both 9.6M steps). If budgets differ materially (PEARL, RL²), say so in Limitations.
- **Why it matters:** C1/C2 compare methods trained with different budgets; equal or reported budgets answer the most likely soundness objection.
- **Literature:** not applicable (presentation)
- **Status:** applied — Learners section reports training budgets in env steps from `\valSteps…` macros; Limitations notes PEARL/RL² saw less data

### I-04 · Paired per-task test for C3 instead of overlapping intervals
- **Type:** evidence · **Impact:** High · **Effort:** 1 h · **Compute:** < 1 min
- **Motivated by:** Results: "Meta-SGD's interval (±2.0 cm) only just separates from the fine-tuned DR gains (±1.9 cm)".
- **Idea:** Every method is scored on the same 32 tasks, so compare Meta-SGD and DR + fine-tune per task (paired differences, bootstrap 95% CI over tasks and seeds). Add it to the values script and report the paired CI. Run it once the extra C3 seeds finish.
- **Why it matters:** a paired test removes between-task variance, which dominates these intervals; it can settle C3 with the same data.
- **What would change the conclusion:** a paired CI excluding zero makes C3 a firm claim; one including zero means it should stay hedged or be dropped.
- **Literature:** not applicable (presentation)
- **Status:** done — with 5 seeds, Meta-SGD improves on fine-tuned DR gains by 3.5 cm (95% bootstrap 2.8–4.3 cm; wins on 83% of 160 task–seed pairs); C3 now stated firmly via `\valGainPaired…` macros

### I-05 · Tune the L1 baseline as carefully as the learners
- **Type:** reviewer · **Impact:** High · **Effort:** 1.5 h · **Compute:** ≈ 5 min (pilot: one L1 configuration on 32 tasks = 9.8 s)
- **Motivated by:** `control.py: L1_AS = 10.0, L1_CUTOFF = 5.0` are fixed hand-picked values, while every learner is trained; L1 scores 15.5 cm vs 7.3 cm for DR (Table II).
- **Idea:** *A reviewer may say* the classical adaptive baseline is a straw man → grid-search the predictor pole and filter bandwidth (e.g. 4 × 5 values) on *training* tasks, then evaluate the best setting on the held-out and OOD sets. Report both the default and the tuned L1.
- **Why it matters:** C1's "2× lower than L1" ratio depends on how strong L1 is.
- **What would change the conclusion:** if tuned L1 approaches 7–8 cm, C1 weakens to "matches tuned L1"; if it stays near 15 cm, C1 stands with a fairer baseline.
- **Literature:** related work — [Adaptive Outer-Loop Control of Quadrotors via RL, arXiv:2605.16015](https://arxiv.org/abs/2605.16015) (RL adaptation layered over classical control); [Bisheban & Lee, doi:10.1109/cdc.2018.8619390](https://doi.org/10.1109/cdc.2018.8619390) (geometric adaptive control against wind, an alternative classical adaptive baseline).
- **Status:** done — tuned L1 14.0 vs default 14.9 cm; added to the C1 paragraph. See experiments/05_l1_tuning/findings.md

### I-06 · Add a "mild OOD" split just beyond the training ranges
- **Type:** evidence · **Impact:** Medium · **Effort:** 2 h · **Compute:** ≈ 40 min (tracking, eval only)
- **Motivated by:** Limitations: "our OOD tasks proved harsh enough that every method fails on them"; C8 rests on this single harsh split.
- **Idea:** Add a split that exceeds each training range by 10–20% (e.g. payload ×1.3–1.35, latency 30–35 ms) and evaluate every tracking method. Plot error against distance outside the training range.
- **Why it matters:** it separates "fails just outside the range" from "fails only far outside", which is what a practitioner needs; it also tests whether the learned residual's higher crash rate (C8) appears early.
- **What would change the conclusion:** if learned methods degrade gracefully on mild OOD, C8 narrows to extreme conditions; if they already crash more than the classical controller, C8 strengthens.
- **Literature:** no close match in searched sources (not proof of novelty). The closest hit, a 2025 RA-L study of what matters for zero-shot sim-to-real quadrotor RL, came back only as a supplementary-file DOI, so it isn't cited here.
- **Status:** done — learned residuals track 15–20 cm better than classical just outside the ranges but crash ~2× as often; added to the OOD paragraph. See experiments/06_mild_ood/findings.md

### I-07 · Say that MAML-family methods were meta-trained for one inner step, and report stage 1 separately
- **Type:** writing · **Impact:** Medium · **Effort:** 0.5 h · **Compute:** none
- **Motivated by:** `results/navigation/maml_seed0.json` per-stage success 0.79 → 0.71 → 0.40 → 0.45; meta-training uses one inner step (Learners section) but evaluation applies three.
- **Idea:** State in Protocol that stages 2–3 go beyond the meta-trained horizon, and report the one-step (trained) result next to the three-step result in the text.
- **Why it matters:** readers will otherwise read the drop as a failure of the trained procedure rather than of extrapolating it.
- **Literature:** not applicable (presentation)
- **Status:** applied — Protocol says the MAML family is meta-trained for one update; one-update navigation values (`\valNav…StageOne`) ready for Results once the re-benchmark lands

### I-08 · Put "in simulation" into the title and contributions
- **Type:** writing · **Impact:** Medium · **Effort:** 0.2 h · **Compute:** none
- **Motivated by:** Title "Where Does Meta-Learning Help a Quadrotor?" while Limitations says "no real flights have been made".
- **Idea:** e.g. "… a Quadrotor? A Simulation Study of Seven Algorithms Combined with Classical Control and Planning", and "in simulation" in the first contribution bullet.
- **Why it matters:** robotics reviewers penalise titles that imply hardware results.
- **Literature:** not applicable (presentation)
- **Status:** applied — title now '… A Simulation Study of Seven Algorithms with Classical Control and Planning'; findings bullet says 'simulation findings'

### I-09 · Cite or soften the gap statement
- **Type:** writing · **Impact:** Medium · **Effort:** 0.3 h · **Compute:** none
- **Motivated by:** Introduction: "meta-reinforcement-learning algorithms are usually compared with each other on locomotion benchmarks, not against classical controllers".
- **Idea:** Cite a benchmark that shows the pattern (Meta-World) and the meta-RL tutorial, or rephrase as an observation about the cited methods' own evaluations.
- **Why it matters:** an uncited generalisation is an easy reviewer target.
- **Literature:** related work — [Meta-World, arXiv:1910.10897](https://arxiv.org/abs/1910.10897) (manipulation, not locomotion: the sentence should be broadened to "simulated robot benchmarks"); [A Tutorial on Meta-RL, doi:10.1561/2200000080](https://doi.org/10.1561/2200000080).
- **Status:** applied — gap statement now cites Meta-World and the meta-RL tutorial and says 'simulated robot benchmarks such as locomotion and manipulation suites'

### I-10 · Split Fig. 2 so 1-episode and 10-episode stages aren't read on one axis
- **Type:** writing · **Impact:** Medium · **Effort:** 1 h · **Compute:** < 1 min
- **Motivated by:** Fig. 2 caption: "PEARL and RL² use one episode per stage, the gradient-based methods ten"; both share one symlog axis, and 13 methods share one legend.
- **Idea:** Either plot against adaptation stage (0–3) with the episodes per stage in the legend, or give panel (c) its own row with fewer methods (the gradient family, DR fine-tune, RL², PEARL).
- **Why it matters:** the key visual (the navigation decline vs RL²'s rise) is currently the hardest to read.
- **Literature:** not applicable (presentation)
- **Status:** applied — Fig. 2 plots against adaptation stage (0–3), legend states episodes per stage, end-to-end planners moved out of panel (c)

### I-11 · Probe the RL² hidden state for task parameters
- **Type:** direction · **Impact:** Medium · **Effort:** 2 h · **Compute:** ≈ 10 min
- **Motivated by:** Results: "RL² is the only method that improves with experience, from 55% to 71%", with no evidence about why.
- **Idea:** First experiment: run RL² trials on the 24 held-out navigation tasks, record the GRU state at the end of each episode, and fit a linear probe to the task parameters (mass scale, weakest motor, wind, latency). Rising probe R² across episodes would show the recurrent state infers the dynamics.
- **Why it matters:** turns an observation into a mechanism and motivates context-based adaptation for flight.
- **What would change the conclusion:** high, rising R² supports "RL² infers the task"; flat R² suggests its gain comes from something else (e.g. exploration of the room).
- **Literature:** related work — [Off-Policy Meta-RL With Belief-Based Task Inference, doi:10.1109/access.2022.3170582](https://doi.org/10.1109/access.2022.3170582) (explicit task inference in meta-RL); [A Tutorial on Meta-RL, doi:10.1561/2200000080](https://doi.org/10.1561/2200000080).
- **Status:** done — RL² did not improve in this run (56→59→58%) and probes found no linear task encoding (weak probe); user chose to let the corrected re-benchmark decide the RL² claim. See experiments/11_rl2_probe/findings.md

### I-12 · Stress-test with aerodynamics the learners never saw
- **Type:** reviewer · **Impact:** Medium · **Effort:** 3 h · **Compute:** ≈ 30 min (eval only)
- **Motivated by:** Limitations: "The aerodynamics are simple (linear drag, no ground effect or rotor drag)".
- **Idea:** *A reviewer may say* learned methods may exploit the simulator's simple physics → add an evaluation-only model mismatch (quadratic drag; a simple ground-effect thrust boost near the floor) and re-score the tracking methods. Model mismatch, not task parameters, is the sim-to-real risk.
- **Why it matters:** a cheap proxy for sim-to-real robustness before hardware.
- **What would change the conclusion:** if learned residuals lose their advantage under unmodelled physics while classical control doesn't, the deployment recommendation should favour Combination 2 over Combination 1.
- **Literature:** related work — [The Power of Input: zero-shot sim-to-real RL benchmarking, doi:10.1109/iros58592.2024.10802831](https://doi.org/10.1109/iros58592.2024.10802831).
- **Status:** proposed

### I-13 · Meta-learn a residual on top of L1 instead of the nominal controller
- **Type:** direction · **Impact:** Medium · **Effort:** 3 h · **Compute:** ≈ 3 h for 2 seeds (over budget); a 1-seed, 60-iteration pilot ≈ 30 min
- **Motivated by:** Table II: L1 halves part of the gap on its own (21.4 → 15.5 cm) and crashes most OOD (52%); the code already supports an L1 base (`TrackingResidual(adaptive_base=True)`).
- **Idea:** First experiment: train DR and MAML residuals with the L1-augmented controller underneath (one seed, shortened) and compare with residuals on the nominal controller.
- **Why it matters:** tests whether classical adaptation and learned residuals are complementary — the paper's own thesis of combining the two.
- **What would change the conclusion:** if the combination beats both, the recommended deployment becomes "L1 + residual"; if not, L1 adds nothing once a residual exists.
- **Literature:** related work — [Adaptive Outer-Loop Control of Quadrotors via RL, arXiv:2605.16015](https://arxiv.org/abs/2605.16015); [Self-Supervised Meta-Learning for All-Layer DNN-Based Adaptive Control, arXiv:2410.07575](https://arxiv.org/abs/2410.07575) (meta-learning combined with adaptive control).
- **Status:** proposed

### I-14 · Gate gradient adaptation on navigation with a safety check
- **Type:** direction · **Impact:** Medium · **Effort:** 3 h · **Compute:** ≈ 30 min
- **Motivated by:** Results: "Collision rates rise as success falls, so the updates trade safety away."
- **Idea:** First experiment: after each inner update, compare collision rates on a few validation episodes with the pre-update policy and reject updates that raise them; re-run the MAML navigation curve.
- **Why it matters:** converts a negative finding into a practical rule for deploying gradient adaptation on a real vehicle.
- **What would change the conclusion:** if gating keeps success at the pre-adaptation level, the paper can recommend gated adaptation; if it rejects nearly every update, gradient adaptation simply has no useful signal at this budget.
- **Literature:** related work — [All-time safety and sample-efficient meta update for online safe meta-RL, doi:10.1007/s10994-025-06810-4](https://doi.org/10.1007/s10994-025-06810-4); [Safe Meta-RL via Information Space Reachability, arXiv:2609.15915](https://arxiv.org/abs/2609.15915).
- **Status:** proposed

## Literature searched

Services: arXiv, Semantic Scholar, Crossref and OpenAlex answered for every group; no search failed. All queries passed the draft guard (`--guard-text ieee-conf/sections`).

| Group | Queries | Results |
|---|---|---|
| meta_quadrotor | "meta reinforcement learning quadrotor adaptation"; "meta-learning adaptive control quadrotor wind" | [literature/meta_quadrotor.md](literature/meta_quadrotor.md) |
| residual_gains | "residual reinforcement learning adaptive control quadrotor"; "learning controller gain tuning quadrotor" | [literature/residual_gains.md](literature/residual_gains.md) |
| negative_adaptation | "MAML adaptation degrades performance reinforcement learning"; "safe meta reinforcement learning adaptation" | [literature/negative_adaptation.md](literature/negative_adaptation.md) |
| rl2_probe | "recurrent meta reinforcement learning task inference hidden state" | [literature/rl2_probe.md](literature/rl2_probe.md) |
| robustness_benchmarks | "quadrotor reinforcement learning unmodeled aerodynamics sim-to-real"; "benchmark meta reinforcement learning robotics" | [literature/robustness_benchmarks.md](literature/robustness_benchmarks.md) |

## Log
- 2026-10-08 — extra seeds and corrected-room benchmarks landed. I-04 done (C3 firm). Corrected benchmark: RL² does not improve (60→55%), so its claim was dropped as agreed; C5 firm (classical 73% over 96 unseen-room flights); C7 revised (planner helps only with a good map).
- 2026-10-06 — I-02, I-06, I-11 finished. I-02 and I-11 undercut parts of C6; reported to the user before any claim edit. User chose: restate C6 with the step-size table; let the corrected re-benchmark decide the RL² claim. Folded I-02 (Table V), I-05 and I-06 into Results via generated values.
- 2026-10-06 — user approved I-01–I-11 edits and experiments (I-12–I-14 not selected). Applied I-01, I-03, I-07, I-08, I-09, I-10; ran I-05; launched I-02, I-06, I-11; I-04 waits for the extra seeds. The I-02 sweep first failed to start (shell word-splitting) and was relaunched.
- 2026-10-06 — generated 14 ideas; pilots timed for I-02 (89 s for 4 tasks × 1 stage) and I-05 (9.8 s per L1 configuration).
