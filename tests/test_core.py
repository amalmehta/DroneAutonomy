"""Fast checks of the physics, perception, mapping, planning and learners."""
import numpy as np
import torch

from drone_autonomy.config import DEFAULT_PLATFORM, GRAVITY
from drone_autonomy.control import GeometricController
from drone_autonomy.dynamics import QuadSim
from drone_autonomy.envs.tracking import TrackingEnv
from drone_autonomy.mapping import OccupancyMap
from drone_autonomy.perception import DepthCamera, render_depth
from drone_autonomy.planning import astar
from drone_autonomy.tasks import fixed_eval_tasks, nominal_tasks, sample_tasks
from drone_autonomy.world import ROOM, Worlds, collides


def one_pillar_world(x=5.0, y=4.0, r=0.4):
    cyl = np.zeros((1, 2, 3)); cyl[0, 0] = [x, y, r]
    box = np.zeros((1, 1, 6)); box[0, 0, 3] = -1
    return Worlds(cyl, box, np.array([[1.0, 4.0, 1.2]]), np.array([[13.0, 4.0, 1.2]]))


def test_hover_thrust_holds_altitude():
    sim = QuadSim(2)
    sim.reset(np.array([[0, 0, 1.0], [0, 0, 1.0]]))
    for _ in range(100):
        sim.step(np.full(2, DEFAULT_PLATFORM.hover_thrust), np.zeros((2, 3)))
    assert np.allclose(sim.p[:, 2], 1.0, atol=0.02)


def test_free_fall_without_thrust():
    sim = QuadSim(1)
    sim.reset(np.array([[0, 0, 10.0]]))
    sim.f_motor[:] = 0
    for _ in range(50):  # 0.5 s
        sim.step(np.zeros(1), np.zeros((1, 3)))
    drop = 10.0 - sim.p[0, 2]
    assert 0.9 < drop < 0.5 * GRAVITY * 0.25 + 0.05  # drag only slows it


def test_controller_tracks_step_nominal():
    sim, ctrl = QuadSim(1), GeometricController(1)
    target = np.array([[1.0, -0.5, 1.5]])
    sim.reset(np.array([[0, 0, 1.0]]))
    z = np.zeros((1, 3))
    for _ in range(1000):  # 10 s; the integrator settles slowly
        T, w = ctrl(sim.p, sim.v, sim.R, target, z, z)
        sim.step(T, w)
    assert np.linalg.norm(sim.p - target) < 0.05


def test_task_splits_are_disjoint_ranges():
    tr, ood = sample_tasks(500, np.random.default_rng(0)), sample_tasks(500, np.random.default_rng(0), "ood")
    assert tr.mass_scale.max() <= ood.mass_scale.min() + 1e-9
    assert np.array_equal(fixed_eval_tasks(5, "test").mass_scale, fixed_eval_tasks(5, "test").mass_scale)


def test_depth_ray_hits_pillar_at_right_range():
    w = one_pillar_world()
    cam = DepthCamera(cols=3, rows=1, hfov_deg=2, vfov_deg=0)
    d = render_depth(cam, np.array([[1.0, 4.0, 1.2]]), np.eye(3)[None], w)
    assert abs(d[0, 1] - (5.0 - 0.4 - 1.0)) < 1e-6


def test_collision_check():
    w = one_pillar_world()
    assert collides(np.array([[5.0, 4.5, 1.0]]), w)[0]
    assert not collides(np.array([[3.0, 4.0, 1.0]]), w)[0]


def test_mapping_marks_hit_and_free():
    m = OccupancyMap(0.2)
    m.integrate(np.array([1.0, 4.0, 1.2]), np.array([[1.0, 0.0, 0.0]]), np.array([3.0]), 5.0)
    assert m.occupied()[int(4.0 / 0.2), int(4.0 / 0.2), int(1.2 / 0.2)]
    assert m.logodds[int(2.0 / 0.2), int(4.0 / 0.2), int(1.2 / 0.2)] < 0


def test_astar_goes_around_wall():
    shape = tuple(np.ceil(ROOM / 0.2).astype(int))
    blocked = np.zeros(shape, bool)
    blocked[30:33, :30, :] = True  # wall with a gap at high y
    path = astar(blocked, np.array([1.0, 1.0, 1.2]), np.array([12.0, 1.0, 1.2]), 0.2)
    assert path is not None and path[:, 1].max() > 5.9


def test_tracking_env_reward_and_metrics():
    env = TrackingEnv(4, horizon=20)
    env.reset(nominal_tasks(4), seed=0)
    for _ in range(20):
        _, r, _, _ = env.step(np.zeros((4, 4)))
    m = env.metrics()
    # the reference accelerates from rest, so early errors of ~10 cm are expected
    assert (r > 0.3).all() and (m["rmse"] < 0.2).all() and not m["crashed"].any()


def test_maml_inner_step_changes_params_and_meta_sgd_learns_lr():
    from drone_autonomy.rl.meta.gradient import GradMeta
    from drone_autonomy.rl.nets import expand_params
    from drone_autonomy.rl.problems import make_problem
    torch.manual_seed(0)
    P = make_problem("tracking_gains")
    m = GradMeta(P, "metasgd", meta_batch=2, E=4)
    tasks = P.sample_tasks(2, np.random.default_rng(0))
    batch, _ = P.collect(m._detach(expand_params(m.shared_params(), 2)), tasks, 4, seed=0)
    rep = expand_params(m.shared_params(), 2)
    adapted = m.adapt(rep, batch, create_graph=True)
    assert not torch.allclose(adapted[0], rep[0])
    loss = sum(a.sum() for a in adapted)
    loss.backward()
    assert m.alpha[0].grad is not None  # second-order path reaches the learned inner rates
