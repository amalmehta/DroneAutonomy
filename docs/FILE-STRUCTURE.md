# File Structure

```
drone_autonomy/              Python package
  config.py                  X500 V2 platform parameters, timing, nominal controller gains
  tasks.py                   task distribution: payload, motor wear, drag, wind, gusts, latency (train / test / OOD)
  dynamics.py                batched rigid-body quadrotor sim (Numba), CTBR interface, PX4-style mixer
  control.py                 geometric position controller and L1 adaptive augmentation (Numba)
  world.py                   procedural rooms (pillars, boxes, hanging ducts), collision checks, true occupancy
  perception.py              RealSense D435i depth camera model (ray casting, noise, dropouts)
  mapping.py                 log-odds 3D occupancy map from depth
  planning.py                inflation, A*, line-of-sight shortcutting, carrots, Dijkstra distance fields
  envs/tracking.py           trajectory tracking env (residual or gain-tuning modes)
  envs/navigation.py         point-to-point navigation env with the full modular stack
  rl/nets.py                 functional Gaussian MLP and gain policies (per-task parameter batches)
  rl/rollout.py              batched rollouts, per-task linear baselines + GAE, PG / PPO losses
  rl/problems.py             binds env + policy + rollout for each problem
  rl/nav_problem.py          navigation problem and world pools
  rl/meta/gradient.py        MAML, FOMAML, ANIL, Meta-SGD, Reptile, domain-randomised PPO, fixed baselines
  rl/meta/pearl.py           PEARL (context encoder + SAC)
  rl/meta/rl2.py             RL² (GRU policy, recurrent PPO over multi-episode trials)
  methods.py                 registry: methods per problem, labels, iteration budgets
  train.py, sweep.py         single training run; parallel sweeps
  benchmark.py               adaptation curves on fixed test / OOD tasks, full-stack navigation scoring
  demo.py                    records full-stack flights for the website
  figures.py                 README / paper / website figures and the results summary
  cli.py                     `drone-autonomy` command
tests/test_core.py           fast checks of physics, perception, mapping, planning and learners
website/index.html           project site with the flight replay viewer
website/data/demo.json       recorded flights it replays
website/data/results.json    benchmark summary the results section reads
website/images/              adaptation figures shown on the site
results/                     benchmark output per (problem, method, seed) and summary.json
docs/                        instructions, system design, drone selection, this file, images
.github/workflows/pages.yml  deploys website/ to GitHub Pages
scripts/queue_nav_meta.sh    starts navigation meta-training once the DR planner exists
drone_autonomy.md            project brief, open questions and changelog
runs/, logs/                 training outputs (not committed)
```
