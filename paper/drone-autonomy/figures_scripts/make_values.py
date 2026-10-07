"""Write generated/values.tex (every number used in the prose) and sources.md (where each comes from)."""
import sys

from common import RESULTS, ROOT, VENUE_DIR, rows, summary

sys.path.insert(0, str(ROOT))
from drone_autonomy.methods import ITERS  # noqa: E402
from drone_autonomy.tasks import RANGES  # noqa: E402

PROB = {"tracking_residual": "Res", "tracking_gains": "Gain", "navigation": "Nav"}
METH = {"classical": "Classical", "l1": "Lone", "classical_l1": "Classicallone", "dr": "Dr", "dr_finetune": "Drft",
        "e2e_dr": "Etoe", "e2e_dr_finetune": "Etoeft", "maml": "Maml", "fomaml": "Fomaml", "anil": "Anil",
        "metasgd": "Metasgd", "reptile": "Reptile", "pearl": "Pearl", "rl2": "Rltwo"}

# Fixed settings quoted in the prose: (literal as typed, meaning, where it is set)
SETTINGS = [
    ("500", "physics rate, Hz (physics_dt 0.002 s)", "drone_autonomy/config.py Timing.physics_dt"),
    ("100", "classical controller rate, Hz", "drone_autonomy/config.py Timing.control_dt"),
    ("50", "residual policy rate, Hz", "drone_autonomy/config.py Timing.tracking_policy_dt"),
    ("10", "local planner rate, Hz; also exploratory episodes per adaptation stage (E=10)", "config.py nav_policy_dt; benchmark.py bench_one E=10"),
    ("2.0", "platform mass, kg", "drone_autonomy/config.py Platform.mass"),
    ("0.25", "arm length, m", "drone_autonomy/config.py Platform.arm_length"),
    ("0.0217", "Ixx = Iyy, kg m^2 (PX4 x500 model)", "drone_autonomy/config.py Platform.inertia"),
    ("0.040", "Izz, kg m^2 (PX4 x500 model)", "drone_autonomy/config.py Platform.inertia"),
    ("2.1", "thrust-to-weight ratio (estimate)", "drone_autonomy/config.py Platform.thrust_to_weight"),
    ("40", "motor time constant, ms (estimate)", "drone_autonomy/config.py Platform.motor_tau"),
    ("0.3", "linear drag, N s/m (estimate)", "drone_autonomy/config.py Platform.drag_coeff"),
    ("35", "max tilt, degrees", "drone_autonomy/config.py Platform.max_tilt_deg"),
    ("0.2", "voxel size, m", "drone_autonomy/envs/navigation.py RES"),
    ("1.5", "carrot lookahead, m; crash threshold for tracking error, m", "envs/navigation.py LOOKAHEAD; envs/tracking.py CRASH_ERR"),
    ("0.35", "drone collision radius, m", "drone_autonomy/world.py DRONE_RADIUS"),
    ("0.15", "planning clearance margin, m", "drone_autonomy/envs/navigation.py CLEARANCE"),
    ("87", "depth camera horizontal FOV, degrees", "drone_autonomy/perception.py DepthCamera.hfov_deg"),
    ("58", "depth camera vertical FOV, degrees", "drone_autonomy/perception.py DepthCamera.vfov_deg"),
    ("5", "depth camera max range, m", "drone_autonomy/perception.py DepthCamera.max_range"),
    ("16", "policy depth image columns", "drone_autonomy/perception.py DepthCamera.cols"),
    ("8", "policy depth image rows", "drone_autonomy/perception.py DepthCamera.rows"),
    ("0.008", "depth noise coefficient (std = 0.008 d^2)", "drone_autonomy/perception.py noise_quad"),
    ("14", "room length, m", "drone_autonomy/world.py ROOM"),
    ("3", "room height, m; adaptation stages; RL^2 trial length in episodes", "world.py ROOM; benchmark.py stages=3; rl2.py K=3"),
    ("30", "navigation episode length, s; adaptation episodes after 3 stages", "envs/navigation.py horizon=300 at 10 Hz; 3 x E=10"),
    ("4", "tracking episode length, s (200 steps at 50 Hz)", "drone_autonomy/envs/tracking.py horizon=200"),
    ("1.9", "lowest hanging-obstacle height, m", "drone_autonomy/world.py generate"),
    ("32", "held-out / OOD tasks per split, tracking", "drone_autonomy/benchmark.py N_TASKS"),
    ("24", "held-out / OOD tasks per split, navigation (privileged planner)", "drone_autonomy/benchmark.py N_TASKS"),
    ("12", "rooms per split, full-stack navigation", "drone_autonomy/benchmark.py FULLSTACK_TASKS"),
    ("128", "worlds per training / test pool", "drone_autonomy/rl/nav_problem.py pool_size"),
    ("16", "meta-batch tasks per iteration (gradient methods)", "drone_autonomy/rl/meta/gradient.py meta_batch=16"),
    ("0.1", "MAML-family inner learning rate", "drone_autonomy/rl/meta/gradient.py inner_lr=0.1"),
    ("3e-3", "Adam step for per-task PPO adaptation, tracking", "drone_autonomy/methods.py INNER_LR default"),
    ("3e-4", "Adam step for per-task PPO adaptation, navigation", "drone_autonomy/methods.py INNER_LR"),
    ("2", "training seeds, tracking", "runs/tracking_*/<method>/seed0, seed1"),
    ("1", "training seeds, navigation", "runs/navigation/<method>/seed0"),
    ("7", "number of controller gains / meta-learning algorithms", "config.py Gains.NAMES; methods.py TRAINED"),
    ("95", "interval level, %", "drone_autonomy/figures.py curve (1.96 standard errors)"),
    ("10", "reduction factor of the navigation inner step (3e-3 -> 3e-4)", "drone_autonomy/methods.py INNER_LR"),
    ("12.5", "PX4 x500 model motor time constant up, ms (cited for comparison)", "docs/DRONE-SELECTION.md"),
    ("67", "Jetson Orin Nano Super, TOPS", "docs/DRONE-SELECTION.md (NVIDIA)"),
    ("1.6", "build cost lower bound, k USD (estimate)", "docs/DRONE-SELECTION.md"),
    ("0.5", "goal tolerance, m", "drone_autonomy/envs/navigation.py GOAL_TOL"),
    ("2.5", "upper wind speed in training range, m/s", "drone_autonomy/tasks.py RANGES"),
    ("26", "A* neighbourhood (26-connected voxel grid)", "drone_autonomy/planning.py NEIGH"),
    ("48", "mapping depth image columns", "drone_autonomy/envs/navigation.py map_cam cols=48"),
    ("24", "mapping depth image rows", "drone_autonomy/envs/navigation.py map_cam rows=24"),
    ("2026-10-05", "date platform prices and stock were checked (also '05')", "docs/DRONE-SELECTION.md research date"),
    ("37", "Crazyflie 2.1 Brushless mass with guards, g", "docs/DRONE-SELECTION.md [Bitcraze product page]"),
    ("285", "ModalAI Starling 2 takeoff mass, g", "docs/DRONE-SELECTION.md [ModalAI datasheet]"),
    ("566", "ModalAI Starling 2 Max takeoff mass, g", "docs/DRONE-SELECTION.md [ModalAI datasheet]"),
    ("893", "Holybro PX4 Vision V1.5 mass without battery, g", "docs/DRONE-SELECTION.md [Holybro product page]"),
    ("2.0", "X500 build mass, kg (estimate; also PX4 x500 model mass)", "docs/DRONE-SELECTION.md"),
    ("1.6--2.0", "X500 build cost range, k USD (estimate)", "docs/DRONE-SELECTION.md"),
    ("70", "tilt limit for early termination, degrees", "drone_autonomy/envs/tracking.py CRASH_TILT"),
    ("0.25", "reward length scale exp(-e/0.25), m; residual thrust bound (25% of hover)", "drone_autonomy/envs/tracking.py reward, RESID_THRUST"),
    ("25", "residual thrust bound, % of hover thrust", "drone_autonomy/envs/tracking.py RESID_THRUST"),
    ("15", "share of tracking episodes that are pure hover, %", "drone_autonomy/envs/tracking.py _sample_refs"),
    ("0.5", "yaw-rate residual bound, rad/s; gust correlation time, s", "envs/tracking.py RESID_RATE; dynamics.py GUST_TAU"),
    ("64", "tracking policy hidden units", "drone_autonomy/rl/problems.py hidden=(64, 64)"),
    ("128", "navigation policy first hidden layer / RL2 GRU units / pool size", "rl/nav_problem.py hidden; rl/meta/rl2.py hidden"),
    ("1--3", "price band of the platform search, k USD", "drone_autonomy.md (user answer)"),
    ("9980", "CPU model Intel Core i9-9980HK", "machine used for all runs (sysctl machdep.cpu.brand_string)"),
    ("435", "camera model RealSense D435i", "docs/DRONE-SELECTION.md"),
    ("16", "held-out tasks in the step-size experiment (I-02)", "ideas/experiments/02_nav_step_size/run.py fixed_eval_tasks(16)"),
    ("29", "Starling 2 Max configuration C29 (the one with ToF)", "docs/DRONE-SELECTION.md"),
]


def fmt_cm(v):
    return "%.1f" % (100 * v)


def fmt_pc(v):
    return "%d" % round(100 * v)


def main():
    lines, src = [], []

    def put(name, value, meaning, how):
        lines.append("\\newcommand{\\%s}{%s}" % (name, value))
        src.append("| `\\%s` | %s | %s | %s |" % (name, value, meaning, how))

    for problem, P in PROB.items():
        for r in rows(problem):
            M = METH[r["method"]]
            base = "results/summary.json -> %s / %s" % (problem, r["method"])
            if problem == "navigation":
                put(f"val{P}{M}Pre", fmt_pc(r["test_pre"]), "held-out success before adapting, %", base + " test_pre")
                put(f"val{P}{M}Post", fmt_pc(r["test_post"]), "held-out success after 3 stages, %", base + " test_post")
                put(f"val{P}{M}Coll", fmt_pc(r["test_collision"]), "held-out collisions after 3 stages, %", base + " test_collision")
                put(f"val{P}{M}Ood", fmt_pc(r["ood_post"]), "OOD success after 3 stages, %", base + " ood_post")
                put(f"val{P}{M}FullPre", fmt_pc(r["full_test_success_pre"]), "full-stack success before adapting, %", base + " full_test_success_pre")
                put(f"val{P}{M}FullPost", fmt_pc(r["full_test_success_post"]), "full-stack success after 1 stage, %", base + " full_test_success_post")
                put(f"val{P}{M}FullColl", fmt_pc(r["full_test_collision_post"]), "full-stack collisions after 1 stage, %", base + " full_test_collision_post")
            else:
                put(f"val{P}{M}Pre", fmt_cm(r["test_pre"]), "held-out RMSE before adapting, cm", base + " test_pre x100")
                put(f"val{P}{M}Post", fmt_cm(r["test_post"]), "held-out RMSE after 3 stages, cm", base + " test_post x100")
                put(f"val{P}{M}Ci", fmt_cm(r["test_post_ci"]), "95% half-interval of held-out RMSE after adapting, cm", base + " test_post_ci x100")
                put(f"val{P}{M}Ood", fmt_cm(r["ood_post"]), "OOD RMSE after 3 stages, cm", base + " ood_post x100")
                put(f"val{P}{M}OodCrash", fmt_pc(r["ood_crash"]), "OOD crash rate after 3 stages, %", base + " ood_crash")

    # ranges quoted from the task distribution
    def rng(name, i, scale=1.0, fmt="%.2f"):
        lo, hi = RANGES[name][i]
        return fmt % (lo * scale), fmt % (hi * scale)
    for key, name, scale, fmt in (("Mass", "mass_scale", 1, "%.2f"), ("Motor", "motor_eff_min", 100, "%d"),
                                  ("Drag", "drag_scale", 1, "%.1f"), ("Wind", "wind_speed", 1, "%.1f"),
                                  ("Gust", "gust_std", 1, "%.1f"), ("Lat", "latency_steps", 10, "%d")):
        for i, split in ((0, "Train"), (1, "Ood")):
            lo, hi = rng(name, i, scale, fmt)
            put(f"valTask{key}{split}Lo", lo, f"{name} {split.lower()} range low", "drone_autonomy/tasks.py RANGES")
            put(f"valTask{key}{split}Hi", hi, f"{name} {split.lower()} range high", "drone_autonomy/tasks.py RANGES")

    # derived comparisons used in the prose
    s = {p: {r["method"]: r for r in summary()[p]} for p in PROB}
    tr = s["tracking_residual"]
    put("valResRatioClassical", "%.1f" % (tr["classical"]["test_post"] / tr["dr"]["test_post"]),
        "RMSE ratio classical / DR residual", "summary.json tracking_residual classical.test_post / dr.test_post")
    put("valResRatioLone", "%.1f" % (tr["l1"]["test_post"] / tr["dr"]["test_post"]),
        "RMSE ratio L1 / DR residual", "summary.json tracking_residual l1.test_post / dr.test_post")
    learned = ["dr", "dr_finetune", "maml", "fomaml", "anil", "metasgd", "pearl"]
    put("valResOodCrashLearnedLo", fmt_pc(min(tr[m]["ood_crash"] for m in learned)), "lowest OOD crash rate among learned residuals (excl. Reptile, RL2), %", "summary.json min ood_crash over " + ",".join(learned))
    put("valResOodCrashLearnedHi", fmt_pc(max(tr[m]["ood_crash"] for m in learned)), "highest OOD crash rate among learned residuals, %", "summary.json max ood_crash over same set")
    allood = [r["ood_post"] for p in ("tracking_residual", "tracking_gains") for r in summary()[p]]
    put("valOodRmseMin", fmt_cm(min(allood)), "lowest OOD RMSE of any tracking method, cm", "summary.json min ood_post over tracking problems")
    deltas = [abs(r["ood_post"] - r["ood_pre"]) for p in ("tracking_residual", "tracking_gains")
              for r in summary()[p] if r["ood_episodes"] > 0]
    put("valOodAdaptMaxDelta", "%.0f" % (100 * max(deltas)), "largest change in OOD RMSE from adapting (any adaptive tracking method), cm",
        "summary.json max |ood_post - ood_pre| over tracking methods with ood_episodes > 0")
    navood = [r["ood_post"] for r in summary()["navigation"]]
    put("valNavOodMax", fmt_pc(max(navood)), "highest OOD success of any navigation method, %", "summary.json max navigation ood_post")
    nv = s["navigation"]
    learned_nav = [m for m in nv if not m.startswith("classical")]
    put("valNavFullLearnedLo", fmt_pc(min(nv[m]["full_test_success_post"] for m in learned_nav)), "lowest full-stack success, learned planners, %", "summary.json min full_test_success_post")
    put("valNavFullLearnedHi", fmt_pc(max(nv[m]["full_test_success_post"] for m in learned_nav)), "highest full-stack success, learned planners, %", "summary.json max full_test_success_post")
    put("valNavFullCollLo", fmt_pc(min(nv[m]["full_test_collision_post"] for m in learned_nav)), "lowest full-stack collision rate, learned planners, %", "summary.json min full_test_collision_post")
    put("valNavFullCollHi", fmt_pc(max(nv[m]["full_test_collision_post"] for m in learned_nav)), "highest full-stack collision rate, learned planners, %", "summary.json max full_test_collision_post")

    # navigation success after one adaptation stage (the MAML family's meta-trained horizon)
    for m, r in nv.items():
        if r.get("test_episodes", 0) > 0:
            put(f"valNav{METH[m]}StageOne", fmt_pc(r["test_curve"][1]), "held-out success after 1 adaptation stage, %",
                f"results/summary.json -> navigation / {m} test_curve[1]")

    # training budgets in environment steps (millions): iterations x env steps per iteration.
    # Per-iteration steps follow each learner's rollouts (all envs run the full horizon):
    #   DR: 16 tasks x 10 episodes; MAML family: 2 x that (pre + post); Reptile: 3 x that;
    #   PEARL: 2 episodes x 8 tasks (+ one warm-up episode on 32 tasks); RL2: 48 trials x 3 episodes.
    H = {"tracking_residual": 200, "tracking_gains": 200, "navigation": 300}
    per_iter = {"dr": 160, "e2e_dr": 160, "maml": 320, "fomaml": 320, "anil": 320, "metasgd": 320,
                "reptile": 480, "pearl": 16, "rl2": 144}
    for problem, P in PROB.items():
        for m in ("dr", "maml", "reptile", "pearl", "rl2"):
            if m not in ITERS[problem]:
                continue
            steps = ITERS[problem][m] * per_iter[m] * H[problem] + (32 * H[problem] if m == "pearl" else 0)
            put(f"valSteps{P}{METH[m]}", "%.1f" % (steps / 1e6), f"{problem} {m} training budget, million env steps",
                f"drone_autonomy/methods.py ITERS[{problem}][{m}]={ITERS[problem][m]} x {per_iter[m]} episodes/iter x horizon {H[problem]}"
                + (" + 32-task warm-up" if m == "pearl" else "") + " (rl/meta/*.py rollout sizes)")

    # idea experiments (paper/drone-autonomy/ideas/experiments/*/results)
    import json
    from common import HERE
    exp = HERE.parent / "ideas" / "experiments"
    l1 = json.loads((exp / "05_l1_tuning" / "results" / "l1_tuning.json").read_text())
    put("valLoneTunedTest", fmt_cm(l1["tuned_test_rmse"]), "tuned L1 held-out RMSE, cm", "ideas/experiments/05_l1_tuning/results/l1_tuning.json tuned_test_rmse")
    put("valLoneDefaultTest", fmt_cm(l1["default_test_rmse"]), "default L1 held-out RMSE on the same episodes, cm", "l1_tuning.json default_test_rmse")
    put("valLoneTunedCutoff", "%d" % l1["best"]["cutoff"], "tuned L1 filter bandwidth, rad/s", "l1_tuning.json best.cutoff")
    put("valLoneTunedPole", "%d" % l1["best"]["a_s"], "tuned L1 predictor pole, 1/s", "l1_tuning.json best.a_s")
    ss = lambda m, s, E: json.loads((exp / "02_nav_step_size" / "results" / f"{m}_scale{s}_E{E}.json").read_text())
    for key, (m, s, E) in {"MamlOne": ("maml", 1.0, 10), "MamlTenth": ("maml", 0.1, 10), "MamlThird": ("maml", 0.3, 10),
                           "MamlData": ("maml", 1.0, 30), "MetasgdOne": ("metasgd", 1.0, 10), "MetasgdTenth": ("metasgd", 0.1, 10)}.items():
        d = ss(m, s, E)
        put(f"valStep{key}Pre", fmt_pc(d["success"][0]), f"I-02 {m} step x{s}, {E} ep/stage: success before adapting, %", f"ideas/experiments/02_nav_step_size/results/{m}_scale{s}_E{E}.json success[0]")
        put(f"valStep{key}Post", fmt_pc(d["success"][-1]), f"I-02 {m} step x{s}, {E} ep/stage: success after 3 stages, %", f"{m}_scale{s}_E{E}.json success[3]")
    mild = {}
    for f in (exp / "06_mild_ood" / "results").glob("*.json"):
        d = json.loads(f.read_text())
        mild.setdefault((d["problem"], d["method"]), []).append(d)
    avg = lambda k, i, key: sum(x[key][i] for x in mild[k]) / len(mild[k])
    put("valMildClassicalRmse", fmt_cm(avg(("tracking_residual", "classical"), -1, "rmse")), "mild-OOD RMSE, classical, cm", "ideas/experiments/06_mild_ood/results mean over seeds rmse[-1]")
    put("valMildClassicalCrash", fmt_pc(avg(("tracking_residual", "classical"), -1, "crashed")), "mild-OOD crash rate, classical, %", "06_mild_ood crashed[-1]")
    put("valMildDrRmse", fmt_cm(avg(("tracking_residual", "dr"), -1, "rmse")), "mild-OOD RMSE, DR residual, cm", "06_mild_ood dr rmse[-1]")
    resid = ["dr", "maml", "fomaml", "anil", "metasgd"]
    put("valMildResidCrashLo", fmt_pc(min(avg(("tracking_residual", m), -1, "crashed") for m in resid)), "mild-OOD crash rate, lowest of DR/MAML-family residuals, %", "06_mild_ood min over " + ",".join(resid))
    put("valMildResidCrashHi", fmt_pc(max(avg(("tracking_residual", m), -1, "crashed") for m in resid)), "mild-OOD crash rate, highest of DR/MAML-family residuals, %", "06_mild_ood max over same set")

    (VENUE_DIR / "generated").mkdir(parents=True, exist_ok=True)
    (VENUE_DIR / "generated" / "values.tex").write_text("% generated by figures_scripts/make_values.py; do not edit\n" + "\n".join(lines) + "\n")
    md = ["# Sources", "", "Every number in the paper, where it comes from. Regenerate with `make_all.py`.", "",
          "## Value macros (generated/values.tex)", "", "| Macro | Value | Meaning | Computed from |", "|---|---|---|---|"] + src
    md += ["", "## Tables and figures", "",
           "| Output | Script | Data |", "|---|---|---|",
           "| generated/tables/tracking.tex | figures_scripts/tracking_table.py | results/summary.json |",
           "| generated/tables/navigation.tex | figures_scripts/navigation_table.py | results/summary.json |",
           "| generated/tables/tasks.tex | figures_scripts/task_table.py | drone_autonomy/tasks.py RANGES |",
           "| generated/tables/stepsize.tex | figures_scripts/step_size_table.py | ideas/experiments/02_nav_step_size/results/*.json |",
           "| figures/adaptation_curves.pdf | figures_scripts/adaptation_curves.py | results/<problem>/*_seed*.json |",
           "| figures/example_flights.pdf | figures_scripts/example_flights.py | website/data/demo.json |",
           "", "## Fixed settings quoted in the text", "", "| Literal | Meaning | Where it is set |", "|---|---|---|"]
    md += ["| %s | %s | %s |" % row for row in SETTINGS]
    (VENUE_DIR / "sources.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
