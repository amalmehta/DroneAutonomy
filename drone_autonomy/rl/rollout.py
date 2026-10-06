"""Batched rollouts, advantages and policy-gradient losses shared by all learners.

Layout convention: T tasks x E episodes per task, task-major, so env row
t*E + e is episode e of task t. Batches handed to losses are tensors whose
first dim is the task: obs (T, N, d), act (T, N, a), adv (T, N), mask (T, N).
"""
import numpy as np
import torch

GAMMA, LAM = 0.99, 0.95


def _per_task(x, T, E):
    """[H, T*E, ...] numpy -> [H, T, E, ...] torch float32."""
    x = torch.as_tensor(np.asarray(x), dtype=torch.float32)
    return x.reshape(x.shape[0], T, E, *x.shape[2:])


def _flatten(x):
    """[H, T, E, ...] -> [T, H*E, ...]"""
    H, T, E = x.shape[:3]
    return x.permute(1, 0, 2, *range(3, x.dim())).reshape(T, H * E, *x.shape[3:])


def linear_baseline_advantages(obs, rew, mask, gamma=GAMMA, lam=LAM, reg=1e-3):
    """Per-task linear feature baseline (as in MAML-RL) + GAE, normalised per task.

    obs [H,T,E,d], rew/mask [H,T,E] -> adv, returns [H,T,E]
    """
    H = rew.shape[0]
    ret = torch.zeros_like(rew)
    run = torch.zeros_like(rew[0])
    for t in reversed(range(H)):
        run = rew[t] + gamma * run * (mask[t + 1] if t + 1 < H else 0.0)
        ret[t] = run * mask[t]
    o = obs.clamp(-10, 10)
    tt = (torch.arange(H, dtype=torch.float32) / 100.0).view(H, 1, 1, 1).expand(*rew.shape, 1)
    feats = torch.cat([o, o ** 2, tt, tt ** 2, tt ** 3, torch.ones_like(tt)], -1) * mask.unsqueeze(-1)
    F = _flatten(feats)                     # (T, N, f)
    G = _flatten(ret).unsqueeze(-1)         # (T, N, 1)
    A = F.transpose(1, 2) @ F + reg * torch.eye(F.shape[-1])
    w = torch.linalg.solve(A, F.transpose(1, 2) @ G)
    V = (F @ w).squeeze(-1)                 # (T, N)
    H_, T, E = rew.shape
    V = V.reshape(T, H_, E).permute(1, 0, 2) * mask
    adv = torch.zeros_like(rew)
    gae = torch.zeros_like(rew[0])
    for t in reversed(range(H)):
        m_next = mask[t + 1] if t + 1 < H else torch.zeros_like(mask[t])
        v_next = V[t + 1] if t + 1 < H else torch.zeros_like(V[t])
        delta = rew[t] + gamma * v_next * m_next - V[t]
        gae = delta + gamma * lam * m_next * gae
        adv[t] = gae * mask[t]
    return normalize_per_task(adv, mask), ret


def normalize_per_task(adv, mask):
    """adv/mask [H,T,E] (or [T,E] with H absent handled by caller)."""
    dims = (0, 2)
    n = mask.sum(dims, keepdim=True).clamp_min(1)
    mu = (adv * mask).sum(dims, keepdim=True) / n
    var = (((adv - mu) * mask) ** 2).sum(dims, keepdim=True) / n
    return (adv - mu) / (var.sqrt() + 1e-6) * mask


def is_per_task(params, policy):
    return params[-1].dim() == policy.params[-1].dim() + 1


@torch.no_grad()
def collect_steps(env, policy, params, tasks, E, seed=None, deterministic=False, gains=None):
    """Run E episodes per task with a step policy. Returns (batch, stats)."""
    T = len(tasks)
    assert env.n == T * E
    obs = env.reset(tasks.repeat(E), gains=gains, seed=seed)
    per_task = is_per_task(params, policy)
    O, A, R, M = [], [], [], []
    alive = np.ones(env.n, bool)
    for _ in range(env.horizon):
        o = torch.as_tensor(obs)
        a = policy.act(params, o.view(T, E, -1) if per_task else o, deterministic)
        a = a.reshape(env.n, -1).numpy()
        O.append(obs); A.append(a); M.append(alive.copy())
        obs, r, done, info = env.step(a)
        R.append(r)
        alive = ~info["crashed"]
    obs_t, act_t = _per_task(O, T, E), _per_task(A, T, E)
    rew_t, mask_t = _per_task(R, T, E), _per_task(np.array(M, dtype=np.float32), T, E)
    adv, ret = linear_baseline_advantages(obs_t, rew_t, mask_t)
    batch = {"obs": _flatten(obs_t), "act": _flatten(act_t), "adv": _flatten(adv),
             "mask": _flatten(mask_t), "rew": rew_t}
    m = env.metrics()
    ep_ret = rew_t.sum(0)  # (T, E)
    stats = {"return": ep_ret.numpy(), **{k: v.reshape(T, E) for k, v in m.items()}}
    batch["logp_old"] = policy.log_prob(params, batch).detach()
    return batch, stats


@torch.no_grad()
def collect_gains(env, gpolicy, params, tasks, E, seed=None, deterministic=False):
    """Episodic rollouts where each episode flies with sampled controller gains."""
    T = len(tasks)
    eps = gpolicy.sample(params, T, E, deterministic)          # (T, E, 7)
    gains = gpolicy.to_gains(eps.reshape(T * E, -1))
    env.reset(tasks.repeat(E), gains=gains, seed=seed)
    R = np.zeros(env.n)
    for _ in range(env.horizon):
        _, r, _, _ = env.step(None)
        R += r
    ret = torch.as_tensor(R, dtype=torch.float32).view(T, E)
    adv = (ret - ret.mean(1, keepdim=True)) / (ret.std(1, keepdim=True) + 1e-6)
    m = env.metrics()
    batch = {"act": eps, "adv": adv, "mask": torch.ones(T, E)}
    batch["logp_old"] = gpolicy.log_prob(params, batch).detach()
    stats = {"return": ret.numpy(), **{k: v.reshape(T, E) for k, v in m.items()}}
    return batch, stats


def pg_loss(logp, batch):
    """Vanilla policy-gradient surrogate, one value per task (T,)."""
    m = batch["mask"]
    return -(logp * batch["adv"] * m).sum(-1) / m.sum(-1).clamp_min(1)


def clip_loss(logp, batch, clip=0.2):
    """PPO clipped surrogate, one value per task (T,)."""
    m = batch["mask"]
    ratio = torch.exp(logp - batch["logp_old"])
    adv = batch["adv"]
    s = torch.min(ratio * adv, ratio.clamp(1 - clip, 1 + clip) * adv)
    return -(s * m).sum(-1) / m.sum(-1).clamp_min(1)
