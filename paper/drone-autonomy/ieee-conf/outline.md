# Outline: Where Does Meta-Learning Help a Quadrotor? Seven Algorithms Combined with Classical Control and Planning

Author: Amal Mehta (\TODO affiliation). Format: IEEEtran conference, two columns, 8 pages including references.

## Page budget (8.0 pages)

| Section | Pages | Carries |
|---|---|---|
| Abstract | 0.25 | C1, C3, C5/C6, C8 headline numbers |
| I. Introduction | 0.85 | problem, gap, 4 contribution bullets (C1–C9) |
| II. Related work | 0.6 | meta-RL; learned adaptation for quadrotors; residual RL; learned vs classical navigation |
| III. System (sim, tasks, stack, three combinations) | 1.3 | Fig. 1, Table I |
| IV. Learners and baselines | 0.7 | shared estimator, the 7 algorithms, baselines, warm start |
| V. Experimental protocol | 0.35 | splits, metrics, seeds, intervals |
| VI. Results | 2.0 | Table II, Table III, Fig. 2, Fig. 3; C1–C8 |
| VII. Real-world platform and test plan | 0.5 | Table IV, C9 |
| VIII. Limitations | 0.3 | seeds, rooms, estimated params, harsh OOD, warm-start confound, no real flights |
| IX. Conclusion + Acknowledgment (AI disclosure) + code availability | 0.3 | — |
| References | 0.85 | ~25 verified entries |

## Section plan

- **I. Introduction.** Quadrotors meet payload, worn motors, wind and latency they weren't tuned for; meta-RL
  promises fast adaptation, while classical stacks (geometric control, L1, mapping + A*) are dependable. Gap: meta-RL
  methods are usually compared with each other on locomotion benchmarks, not against classical controllers and
  planners in the loop. This paper: one simulator and stack, three insertion points, seven algorithms, classical and
  non-meta baselines, held-out and out-of-distribution tasks. Contributions:
  1. an open simulation suite (X500-parameterised dynamics, D435i depth model, occupancy mapping, A*) with three
     classical+meta combinations (Sec. III);
  2. a benchmark of MAML, FOMAML, ANIL, Meta-SGD, Reptile, PEARL and RL² against nominal, L1, domain-randomised
     and fine-tuning baselines (Sec. VI): C1–C4, C7;
  3. findings on where adaptation helps and hurts: gain tuning (C3, hedged), navigation (C5 hedged, C6), and OOD
     brittleness (C8);
  4. a hardware recommendation and staged sim-to-real plan (Sec. VII, C9).
- **II. Related work.** Group by idea; end each group with how this paper differs. Only verified citations.
- **III. System.** Dynamics (CTBR interface, PX4-style rate loop and mixer, motor lag, drag, OU gusts, latency);
  platform parameters marked published vs estimated; task distribution (Table I: train/test and OOD ranges);
  perception, mapping, planning; the three combinations (residual on controller, gains, local planner outputting
  velocity to the classical controller); Fig. 1 pipeline.
- **IV. Learners.** Shared per-task linear baseline + GAE; MAML-family inner PG step with PPO-clipped outer loss;
  Reptile with inner PPO; PEARL (encoder + SAC); RL² (GRU, recurrent PPO); DR baseline and DR + fine-tune; for
  gains, a parameter-exploring Gaussian over log-gains. Warm start for navigation gradient learners; the Reptile
  re-run with a 10× smaller inner step (reported, not hidden).
- **V. Protocol.** 32 held-out tasks (navigation 24, unseen rooms), OOD tasks; 3 adaptation stages; full-stack
  navigation on 12 unseen rooms; 2 seeds tracking, 1 navigation; 95% normal intervals over tasks × seeds; CPU-only.
- **VI. Results.** One paragraph per claim, each opening with the takeaway: C1+C2 (Table II, Fig. 2a), C3 (Table II,
  Fig. 2b, hedged), C4 (Table II), C6 (Fig. 2c, Table III), C5 (Table III, hedged), C7 (Table III), C8 (Tables II–III).
- **VII. Platform.** Requirements → comparison (Table IV) → pick and test stages; no real flights yet.

## Figure and table plan

| ID | Takeaway (caption's first sentence) | Data | Script | Width |
|---|---|---|---|---|
| Fig. 1 | Meta-learning plugs into three places of one classical stack. | — (diagram) | `figures/pipeline.tex` (TikZ) | text |
| Fig. 2 | Adaptation helps when it tunes gains, barely moves a learned residual, and degrades learned navigation planners; only RL² improves with experience. | results/*/ *.json (test split) | `figures_scripts/adaptation_curves.py` | text |
| Fig. 3 | The classical stack maps an unseen room from depth and replans around obstacles it discovers. | website/data/demo.json | `figures_scripts/example_flights.py` | column |
| Table I | Task distribution: training/held-out ranges and OOD ranges. | drone_autonomy/tasks.py RANGES | `figures_scripts/task_table.py` | column |
| Table II | Tracking: residual and gain-tuning results, test and OOD. | results/summary.json | `figures_scripts/tracking_table.py` | text |
| Table III | Navigation: privileged-planner adaptation and full-stack success/collisions. | results/summary.json | `figures_scripts/navigation_table.py` | text |
| Table IV | Candidate platforms (compact). | docs/DRONE-SELECTION.md | hand-written table, every cell traced in sources.md | column |
| values.tex | every in-text number | results/summary.json, tasks.py, config.py | `figures_scripts/make_values.py` | — |

## Required statements

- Acknowledgment with full factual AI-use disclosure (researcher's choice): code, simulator, experiments, figures,
  benchmark and draft produced with an AI coding assistant (Claude Code) under the author's direction; citation
  metadata checked against arXiv/Crossref by script; the author reviewed results and is responsible for all claims.
- Code availability: https://github.com/amalmehta/DroneAutonomy.

## Changelog
- 2026-10-06 — first outline.
- 2026-10-06 — first full draft compiled (7 pages); reviewer read fixed Fig. 1 label overlap, Fig. 3 caption overclaim, "planner must use height" wording, OOD-change claim now from data (`\valOodAdaptMaxDelta`); Crazyflie status "listed" (stock not verified).
- 2026-10-08 — final revision for top-tier polish: problem formulation section, results organised by research question, claims rewritten against the corrected benchmark (5 gain seeds, 2 navigation seeds, distinct rooms), training-budget table, Table II shows one set of numbers for the classical controller, reference capitalisation, balanced last page. 8 pages, all checks pass except the affiliation TODO.
