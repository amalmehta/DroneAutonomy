# I-06 findings: just outside the training ranges

Source: `results/*.json` (32 mild-OOD tasks × 4 episodes; seeds 0 and 1; RMSE after the last adaptation stage).

| Method | RMSE (cm) | Crash rate |
|---|---|---|
| Classical (nominal) | 61.5 | 9% |
| Classical + L1 | 51.5 | 24% |
| DR residual | 41.1 | 18% |
| MAML / FOMAML / ANIL / Meta-SGD residual | 46.7 / 42.7 / 45.4 / 45.1 | 18 / 14 / 16 / 16% |
| Reptile / PEARL / RL² residual | 50.4 / 42.2 / 45.7 | 7 / 11 / 11% |
| Gains: DR + fine-tune / MAML / Meta-SGD | 53.3 / 51.0 / 47.1 | 21 / 19 / 17% |

**What it shows.** "Mild" is already hard: every method more than triples its held-out error, mostly because latency
starts at the training maximum (30–40 ms). The learned residuals keep a 15–20 cm advantage over the nominal controller,
but most of them crash about twice as often (14–18% vs 9%). Meta-SGD's gain tuning is again the clearest adapter
(54.8 → 47.1 cm). PEARL adapts here too (48.4 → 42.2 cm).

**Effect on the paper.** It **supports C8's crash finding** at milder conditions (higher crash rates than the classical
controller already appear just outside the range) and **refines** it: the learned methods still track better when they
don't crash. This can be stated as a trade-off of accuracy against safety margin.
