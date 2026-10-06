"""Command-line entry point: `drone-autonomy <command> ...`."""
import argparse


def main(argv=None):
    ap = argparse.ArgumentParser(prog="drone-autonomy", description="Drone Autonomy: meta-RL + classical stack")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("train", help="train one method on one problem")
    t.add_argument("--problem", required=True, choices=["tracking_residual", "tracking_gains", "navigation"])
    t.add_argument("--method", required=True)
    t.add_argument("--seed", type=int, default=0)
    t.add_argument("--iters", type=int, default=None)

    s = sub.add_parser("sweep", help="train many (problem, method, seed) runs in parallel")
    s.add_argument("--problems", nargs="+", default=["tracking_residual", "tracking_gains", "navigation"])
    s.add_argument("--methods", nargs="+", default=None, help="default: every trained method of each problem")
    s.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    s.add_argument("--workers", type=int, default=8)
    s.add_argument("--skip-done", action="store_true")

    b = sub.add_parser("bench", help="evaluate adaptation on held-out and out-of-distribution tasks")
    b.add_argument("--problems", nargs="+", default=["tracking_residual", "tracking_gains", "navigation"])
    b.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    b.add_argument("--workers", type=int, default=8)
    b.add_argument("--methods", nargs="+", default=None, help="default: every method of each problem")
    b.add_argument("--quick", action="store_true", help="fewer tasks, for smoke tests")

    sub.add_parser("figures", help="make paper/website figures from results/")

    d = sub.add_parser("demo", help="record full-stack flights for the website replay (website/data/demo.json)")
    d.add_argument("--seed", type=int, default=0)

    a = ap.parse_args(argv)
    if a.cmd == "train":
        from .train import train
        train(a.problem, a.method, a.seed, a.iters)
    elif a.cmd == "sweep":
        from .sweep import sweep
        sweep(a.problems, a.methods, a.seeds, a.workers, a.skip_done)
    elif a.cmd == "bench":
        from .benchmark import bench_all
        bench_all(a.problems, a.seeds, a.workers, a.quick, a.methods)
    elif a.cmd == "figures":
        from .figures import make_all
        make_all()
    elif a.cmd == "demo":
        from .demo import demo
        demo(a.seed)


if __name__ == "__main__":
    main()
