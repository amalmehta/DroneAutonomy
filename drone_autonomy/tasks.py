"""Task distribution for meta-learning: dynamics and disturbance variations.

A *task* is one physical condition the drone must adapt to: payload (mass),
degraded motors, drag, steady wind plus gusts, and command latency. These are
exactly the axes of the sim-to-real gap, so adapting to them in simulation is
a rehearsal for adapting on the real drone.
"""
from dataclasses import dataclass

import numpy as np

# name: (train/in-distribution range, out-of-distribution range)
RANGES = {
    "mass_scale": ((0.85, 1.3), (1.3, 1.4)),
    "motor_eff_min": ((0.75, 1.0), (0.65, 0.75)),
    "drag_scale": ((0.5, 2.0), (2.0, 3.0)),
    "wind_speed": ((0.0, 2.5), (2.5, 4.0)),
    "gust_std": ((0.0, 0.8), (0.8, 1.5)),
    "latency_steps": ((0, 3), (3, 5)),  # x 10 ms controller ticks, inclusive
}


@dataclass
class TaskBatch:
    """Per-env task parameters, each an array with leading dim n."""
    mass_scale: np.ndarray
    motor_eff: np.ndarray      # (n, 4)
    drag_scale: np.ndarray
    wind: np.ndarray           # (n, 3) steady wind velocity, m/s
    gust_std: np.ndarray
    latency_steps: np.ndarray  # int

    def __len__(self):
        return len(self.mass_scale)

    def repeat(self, k: int) -> "TaskBatch":
        """Repeat each task k times consecutively (task-major layout)."""
        return TaskBatch(**{f: np.repeat(getattr(self, f), k, axis=0) for f in self.__dataclass_fields__})

    def index(self, idx) -> "TaskBatch":
        return TaskBatch(**{f: getattr(self, f)[idx] for f in self.__dataclass_fields__})

    def features(self) -> np.ndarray:
        """Compact numeric description (used only for analysis plots, never by policies)."""
        return np.column_stack([
            self.mass_scale, self.motor_eff.min(1), self.drag_scale,
            np.linalg.norm(self.wind, axis=1), self.gust_std, self.latency_steps,
        ])

    @staticmethod
    def concat(batches) -> "TaskBatch":
        return TaskBatch(**{f: np.concatenate([getattr(b, f) for b in batches], 0)
                            for f in TaskBatch.__dataclass_fields__})


def nominal_tasks(n: int) -> TaskBatch:
    return TaskBatch(
        mass_scale=np.ones(n), motor_eff=np.ones((n, 4)), drag_scale=np.ones(n),
        wind=np.zeros((n, 3)), gust_std=np.zeros(n), latency_steps=np.zeros(n, dtype=int),
    )


def sample_tasks(n: int, rng: np.random.Generator, split: str = "train") -> TaskBatch:
    """split: 'train' / 'test' (same ranges, disjoint seeds) or 'ood'."""
    def u(name):
        lo, hi = RANGES[name][1 if split == "ood" else 0]
        return rng.uniform(lo, hi, n)

    mass = u("mass_scale")
    eff = rng.uniform(0.95, 1.0, (n, 4))  # small spread on healthy motors
    weak = rng.integers(0, 4, n)
    eff[np.arange(n), weak] = u("motor_eff_min")
    heading = rng.uniform(0, 2 * np.pi, n)
    speed = u("wind_speed")
    wind = np.column_stack([speed * np.cos(heading), speed * np.sin(heading), np.zeros(n)])
    lo, hi = RANGES["latency_steps"][1 if split == "ood" else 0]
    lat = rng.integers(lo, hi + 1, n)
    return TaskBatch(mass_scale=mass, motor_eff=eff, drag_scale=u("drag_scale"),
                     wind=wind, gust_std=u("gust_std"), latency_steps=lat)


def fixed_eval_tasks(n: int, split: str) -> TaskBatch:
    """Deterministic held-out task sets used by every method's evaluation."""
    seed = {"train": 0, "test": 10_001, "ood": 20_002}[split]
    return sample_tasks(n, np.random.default_rng(seed), split)
