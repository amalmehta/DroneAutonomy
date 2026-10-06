"""Combo 3: meta-RL local planner inside the modular navigation stack."""
from ..envs.navigation import NavEnv, WorldPool
from .nets import GaussianMLP
from .problems import Problem
from .rollout import collect_steps

TRAIN_POOL_SEED, TEST_POOL_SEED = 1, 2


class Navigation(Problem):
    name = "navigation"
    log_keys = ("success", "collision")
    _pools = {}

    def __init__(self, planner="oracle", pool_size=128, hidden=(128, 64), split="train", local="policy",
                 adaptive=False):
        super().__init__()
        self.planner, self.local, self.adaptive = planner, local, adaptive
        self.pool = self.get_pool(split, pool_size)
        self.policy = GaussianMLP(NavEnv.obs_dim, NavEnv.act_dim, hidden)

    @classmethod
    def get_pool(cls, split, size):
        key = (split, size)
        if key not in cls._pools:
            cls._pools[key] = WorldPool(size, TRAIN_POOL_SEED if split == "train" else TEST_POOL_SEED)
        return cls._pools[key]

    def make_env(self, n):
        return NavEnv(n, self.pool, planner=self.planner, local=self.local, adaptive=self.adaptive)

    def collect(self, params, tasks, E, seed=None, deterministic=False):
        return collect_steps(self.env(len(tasks) * E), self.policy, params, tasks, E, seed, deterministic)
