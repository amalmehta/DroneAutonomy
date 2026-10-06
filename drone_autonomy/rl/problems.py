"""Problems bind an environment, a policy family and a rollout function.

Learners only see this interface:
  problem.policy                      functional policy (GaussianMLP / GainPolicy)
  problem.collect(params, tasks, E, seed, deterministic) -> (batch, stats)
  problem.sample_tasks(n, rng)        training task sampler
"""
from ..envs.tracking import TrackingEnv
from ..tasks import sample_tasks
from .nets import GainPolicy, GaussianMLP
from .rollout import collect_gains, collect_steps


class Problem:
    name = "problem"
    episodic = False   # True: one action per episode (gain tuning)
    log_keys = ("rmse", "crashed")

    def __init__(self):
        self._envs = {}

    def env(self, n):
        if n not in self._envs:
            self._envs[n] = self.make_env(n)
        return self._envs[n]

    def sample_tasks(self, n, rng):
        return sample_tasks(n, rng, "train")


class TrackingResidual(Problem):
    """Combo 1: meta-learned residual policy on top of the geometric controller."""
    name = "tracking_residual"

    def __init__(self, adaptive_base=False, hidden=(64, 64)):
        super().__init__()
        self.adaptive_base = adaptive_base
        self.policy = GaussianMLP(TrackingEnv.obs_dim, TrackingEnv.act_dim, hidden)

    def make_env(self, n):
        return TrackingEnv(n, mode="residual", adaptive=self.adaptive_base)

    def collect(self, params, tasks, E, seed=None, deterministic=False):
        return collect_steps(self.env(len(tasks) * E), self.policy, params, tasks, E, seed, deterministic)


class TrackingGains(Problem):
    """Combo 2: meta-learned classical controller gains."""
    name = "tracking_gains"
    episodic = True

    def __init__(self):
        super().__init__()
        self.policy = GainPolicy()

    def make_env(self, n):
        return TrackingEnv(n, mode="gains")

    def collect(self, params, tasks, E, seed=None, deterministic=False):
        return collect_gains(self.env(len(tasks) * E), self.policy, params, tasks, E, seed, deterministic)


def make_problem(name, **kw):
    if name == "tracking_residual":
        return TrackingResidual(**kw)
    if name == "tracking_gains":
        return TrackingGains()
    if name == "navigation":
        from .nav_problem import Navigation
        return Navigation(**kw)
    raise ValueError(name)


def task_seed(rng):
    return int(rng.integers(0, 2**31 - 1))

