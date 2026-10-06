"""Physical platform parameters and simulation timing.

The default platform approximates the drone recommended for real-world tests
(see docs/DRONE-SELECTION.md). Values marked "est." are estimates, not
manufacturer data; the task distribution randomizes around them anyway.
"""
from dataclasses import dataclass, field

import numpy as np

GRAVITY = 9.81


@dataclass(frozen=True)
class Platform:
    # Holybro X500 V2 + Jetson Orin Nano Super + RealSense D435i build.
    # Mass, arm, inertia and yaw coefficient follow PX4's x500 Gazebo model;
    # thrust-to-weight, motor lag and drag are estimates (bench-test them).
    name: str = "Holybro X500 V2 + Jetson Orin Nano + RealSense D435i"
    mass: float = 2.0              # kg, takeoff mass (est. for full build)
    arm_length: float = 0.25       # m, motor to centre (500 mm wheelbase)
    inertia: tuple = (0.0217, 0.0217, 0.040)  # kg m^2, PX4 sim model
    thrust_to_weight: float = 2.1  # est. from Holybro payload spec
    yaw_moment_coeff: float = 0.016  # m, torque/thrust ratio, PX4 sim model
    motor_tau: float = 0.04        # s, first-order motor lag, est.
    drag_coeff: float = 0.3        # N/(m/s), linear body drag, est.
    max_rate: float = 4.0          # rad/s, body-rate command limit
    max_tilt_deg: float = 35.0
    rate_gain: tuple = (25.0, 25.0, 10.0)  # 1/s, onboard body-rate PI loop, P term
    rate_int_gain: float = 15.0    # 1/s^2, body-rate PI loop, I term

    @property
    def max_motor_thrust(self) -> float:
        return self.thrust_to_weight * self.mass * GRAVITY / 4.0

    @property
    def hover_thrust(self) -> float:
        return self.mass * GRAVITY


@dataclass(frozen=True)
class Timing:
    physics_dt: float = 0.002   # 500 Hz rigid-body integration
    control_dt: float = 0.01    # 100 Hz classical position controller
    tracking_policy_dt: float = 0.02  # 50 Hz residual policy
    nav_policy_dt: float = 0.1  # 10 Hz local planner policy

    @property
    def substeps(self) -> int:
        return int(round(self.control_dt / self.physics_dt))


@dataclass(frozen=True)
class Gains:
    """Cascaded geometric controller gains (position -> thrust + body rates)."""
    kp_xy: float = 6.0
    kp_z: float = 8.0
    kd_xy: float = 4.0
    kd_z: float = 5.0
    ki_xy: float = 0.5
    ki_z: float = 1.0
    k_att: float = 8.0

    NAMES = ("kp_xy", "kp_z", "kd_xy", "kd_z", "ki_xy", "ki_z", "k_att")

    def as_array(self) -> np.ndarray:
        return np.array([getattr(self, n) for n in self.NAMES], dtype=np.float64)


DEFAULT_PLATFORM = Platform()
DEFAULT_TIMING = Timing()
DEFAULT_GAINS = Gains()
