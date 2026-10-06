"""PEARL (Rakelly et al., 2019): off-policy meta-RL with probabilistic context.

A permutation-invariant encoder turns recent transitions (s, a, r, s') of the
current task into a Gaussian posterior over a latent task variable z (product
of per-transition Gaussians). A SAC actor and twin critics are conditioned
on z. Adaptation at test time needs no gradient steps: fly one episode,
infer z, act. The encoder is trained through the critic loss plus a KL
penalty to the unit-Gaussian prior.
"""
import math

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

LATENT = 5


def mlp(i, o, h=(128, 128)):
    layers, d = [], i
    for w in h:
        layers += [nn.Linear(d, w), nn.ReLU()]
        d = w
    layers.append(nn.Linear(d, o))
    return nn.Sequential(*layers)


class TaskBuffer:
    """One ring buffer per training task."""

    def __init__(self, n_tasks, cap, obs_dim, act_dim):
        self.o = np.zeros((n_tasks, cap, obs_dim), np.float32)
        self.a = np.zeros((n_tasks, cap, act_dim), np.float32)
        self.r = np.zeros((n_tasks, cap), np.float32)
        self.o2 = np.zeros((n_tasks, cap, obs_dim), np.float32)
        self.d = np.zeros((n_tasks, cap), np.float32)
        self.ptr = np.zeros(n_tasks, int)
        self.size = np.zeros(n_tasks, int)
        self.cap = cap

    def add(self, t, o, a, r, o2, d):
        n = len(r)
        idx = (self.ptr[t] + np.arange(n)) % self.cap
        self.o[t, idx], self.a[t, idx], self.r[t, idx], self.o2[t, idx], self.d[t, idx] = o, a, r, o2, d
        self.ptr[t] = (self.ptr[t] + n) % self.cap
        self.size[t] = min(self.cap, self.size[t] + n)

    def sample(self, tasks, n, rng):
        idx = np.stack([rng.integers(0, self.size[t], n) for t in tasks])
        tt = np.asarray(tasks)[:, None]
        f = lambda x: torch.as_tensor(x[tt, idx])
        return f(self.o), f(self.a), f(self.r), f(self.o2), f(self.d)


class PEARL:
    name = "pearl"
    adapts = True

    def __init__(self, problem, seed=0, n_train_tasks=32, cap=8000, collect_tasks=8, grad_steps=100,
                 meta_batch=8, batch=128, context=64, lr=3e-4, gamma=0.99, tau=0.005, kl_weight=0.1,
                 reward_scale=5.0):
        self.problem = problem
        self.rng = np.random.default_rng(seed)
        torch.manual_seed(seed)
        env = problem.env(1)
        self.od, self.ad = env.obs_dim, env.act_dim
        od, ad = self.od, self.ad
        self.enc = mlp(od * 2 + ad + 1, 2 * LATENT)
        self.actor = mlp(od + LATENT, 2 * ad)
        self.q1, self.q2 = mlp(od + ad + LATENT, 1), mlp(od + ad + LATENT, 1)
        self.q1t, self.q2t = mlp(od + ad + LATENT, 1), mlp(od + ad + LATENT, 1)
        self.q1t.load_state_dict(self.q1.state_dict())
        self.q2t.load_state_dict(self.q2.state_dict())
        self.log_alpha = torch.zeros(1, requires_grad=True)
        self.opt_q = torch.optim.Adam(list(self.q1.parameters()) + list(self.q2.parameters())
                                      + list(self.enc.parameters()), lr=lr)
        self.opt_pi = torch.optim.Adam(self.actor.parameters(), lr=lr)
        self.opt_a = torch.optim.Adam([self.log_alpha], lr=lr)
        self.train_tasks = problem.sample_tasks(n_train_tasks, self.rng)
        self.buf = TaskBuffer(n_train_tasks, cap, od, ad)
        self.n_tasks, self.collect_tasks, self.grad_steps = n_train_tasks, collect_tasks, grad_steps
        self.meta_batch, self.batch, self.context = meta_batch, batch, context
        self.gamma, self.tau, self.kl_w, self.rs = gamma, tau, kl_weight, reward_scale
        self.iteration = 0

    # ----------------------------------------------------------- inference
    def posterior(self, ctx):
        """ctx (T, N, d) -> mean, var of product-of-Gaussians posterior (T, LATENT)."""
        out = self.enc(ctx)
        mu, var = out[..., :LATENT], F.softplus(out[..., LATENT:]).clamp_min(1e-6)
        prec = (1.0 / var).sum(1)
        v = 1.0 / prec
        return v * (mu / var).sum(1), v

    def policy(self, obs, z, deterministic=False):
        out = self.actor(torch.cat([obs, z], -1))
        mu, log_std = out[..., :self.ad], out[..., self.ad:].clamp(-5, 1)
        if deterministic:
            return torch.tanh(mu), None
        eps = torch.randn_like(mu)
        pre = mu + log_std.exp() * eps
        a = torch.tanh(pre)
        logp = (-0.5 * eps ** 2 - log_std - 0.5 * math.log(2 * math.pi)).sum(-1) \
            - (2 * (math.log(2) - pre - F.softplus(-2 * pre))).sum(-1)
        return a, logp

    # ------------------------------------------------------------ rollouts
    @torch.no_grad()
    def run_episodes(self, tasks, E, z_per_task, deterministic, seed, problem=None):
        """One synchronised batch: E episodes for each of T tasks with given z (T, LATENT)."""
        T = len(tasks)
        env = (problem or self.problem).env(T * E)
        obs = env.reset(tasks.repeat(E), seed=seed)
        z = z_per_task.repeat_interleave(E, 0)
        trans = []
        alive = np.ones(env.n, bool)
        R = np.zeros(env.n)
        for _ in range(env.horizon):
            a, _ = self.policy(torch.as_tensor(obs), z, deterministic)
            a = a.numpy()
            obs2, r, done, info = env.step(a)
            term = info["crashed"]
            trans.append((obs, a, r, obs2, term.astype(np.float32), alive.copy()))
            R += r
            alive = ~term
            obs = obs2
        stats = {"return": R.reshape(T, E), **{k: v.reshape(T, E) for k, v in env.metrics().items()}}
        return trans, stats

    @staticmethod
    def _per_task(trans, T, E):
        """Flatten transitions of alive steps per task -> list of arrays (o, a, r, o2, d)."""
        out = []
        for t in range(T):
            rows = slice(t * E, (t + 1) * E)
            sel = [(o[rows][m[rows]], a[rows][m[rows]], r[rows][m[rows]], o2[rows][m[rows]], d[rows][m[rows]])
                   for o, a, r, o2, d, m in trans]
            out.append(tuple(np.concatenate([s[k] for s in sel]) for k in range(5)))
        return out

    def _ctx_tensor(self, per_task, n=None):
        ctxs = []
        for o, a, r, o2, _ in per_task:
            idx = np.arange(len(r)) if n is None else self.rng.integers(0, max(1, len(r)), n)
            ctxs.append(np.concatenate([o[idx], a[idx], r[idx, None], o2[idx]], 1))
        m = min(len(c) for c in ctxs)
        return torch.as_tensor(np.stack([c[:m] for c in ctxs]), dtype=torch.float32)

    # ------------------------------------------------------------- training
    def train_step(self):
        if self.iteration == 0:  # warm-up: one prior episode on every training task
            T = self.n_tasks
            trans, _ = self.run_episodes(self.train_tasks, 1, torch.randn(T, LATENT), False,
                                         int(self.rng.integers(1 << 30)))
            for t, data in enumerate(self._per_task(trans, T, 1)):
                self.buf.add(t, *data)
        ids = self.rng.choice(self.n_tasks, self.collect_tasks, replace=False)
        tasks = self.train_tasks.index(ids)
        T = len(ids)
        prior = torch.randn(T, LATENT)
        trans, st_pre = self.run_episodes(tasks, 1, prior, False, int(self.rng.integers(1 << 30)))
        per = self._per_task(trans, T, 1)
        for k, t in enumerate(ids):
            self.buf.add(t, *per[k])
        with torch.no_grad():
            mu, var = self.posterior(self._ctx_tensor(per, self.context))
            z = mu + var.sqrt() * torch.randn_like(mu)
        trans, st_post = self.run_episodes(tasks, 1, z, False, int(self.rng.integers(1 << 30)))
        per = self._per_task(trans, T, 1)
        for k, t in enumerate(ids):
            self.buf.add(t, *per[k])
        losses = [self._update() for _ in range(self.grad_steps)]
        self.iteration += 1
        out = {"pre_return": float(st_pre["return"].mean()), "post_return": float(st_post["return"].mean()),
               "q_loss": float(np.mean([l[0] for l in losses])), "alpha": float(self.log_alpha.exp())}
        for key in self.problem.log_keys:
            out[f"pre_{key}"] = float(np.nanmean(st_pre[key]))
            out[f"post_{key}"] = float(np.nanmean(st_post[key]))
        return out

    def _update(self):
        ready = np.nonzero(self.buf.size > 0)[0]
        tasks = self.rng.choice(ready, min(self.meta_batch, len(ready)), replace=False)
        co, ca, cr, co2, _ = self.buf.sample(tasks, self.context, self.rng)
        ctx = torch.cat([co, ca, cr.unsqueeze(-1), co2], -1)
        mu, var = self.posterior(ctx)
        z = mu + var.sqrt() * torch.randn_like(mu)
        kl = 0.5 * (var + mu ** 2 - 1 - var.log()).sum(-1).mean()
        o, a, r, o2, d = self.buf.sample(tasks, self.batch, self.rng)
        zb = z.unsqueeze(1).expand(-1, self.batch, -1)
        alpha = self.log_alpha.exp().detach()
        with torch.no_grad():
            a2, logp2 = self.policy(o2, zb.detach())
            x2 = torch.cat([o2, a2, zb.detach()], -1)
            qt = torch.min(self.q1t(x2), self.q2t(x2)).squeeze(-1) - alpha * logp2
            y = self.rs * r + self.gamma * (1 - d) * qt
        x = torch.cat([o, a, zb], -1)
        q_loss = F.mse_loss(self.q1(x).squeeze(-1), y) + F.mse_loss(self.q2(x).squeeze(-1), y) + self.kl_w * kl
        self.opt_q.zero_grad()
        q_loss.backward()
        self.opt_q.step()
        zd = zb.detach()
        an, logp = self.policy(o, zd)
        xn = torch.cat([o, an, zd], -1)
        pi_loss = (alpha * logp - torch.min(self.q1(xn), self.q2(xn)).squeeze(-1)).mean()
        self.opt_pi.zero_grad()
        pi_loss.backward()
        self.opt_pi.step()
        a_loss = -(self.log_alpha * (logp.detach() - self.ad).mean())
        self.opt_a.zero_grad()
        a_loss.backward()
        self.opt_a.step()
        with torch.no_grad():
            for q, qt in ((self.q1, self.q1t), (self.q2, self.q2t)):
                for p, pt in zip(q.parameters(), qt.parameters()):
                    pt.mul_(1 - self.tau).add_(self.tau * p)
        return float(q_loss), float(pi_loss)

    # ----------------------------------------------------------- evaluation
    def adaptation_curve(self, tasks, stages, E=10, E_eval=4, seed=0, eval_problem=None):
        """Stage s: context = s exploration episodes collected with posterior sampling."""
        rng = np.random.default_rng(seed)
        T = len(tasks)
        context = None
        out = []
        for s in range(stages + 1):
            with torch.no_grad():
                if context is None:
                    z_mean, z_sample = torch.zeros(T, LATENT), torch.randn(T, LATENT)
                else:
                    mu, var = self.posterior(self._ctx_tensor(context))
                    z_mean, z_sample = mu, mu + var.sqrt() * torch.randn_like(mu)
            _, st = self.run_episodes(tasks, E_eval, z_mean, True, int(rng.integers(1 << 30)), eval_problem)
            st["episodes_used"] = s
            out.append(st)
            if s < stages:
                trans, _ = self.run_episodes(tasks, 1, z_sample, False, int(rng.integers(1 << 30)))
                per = self._per_task(trans, T, 1)
                context = per if context is None else [tuple(np.concatenate([c[k], p[k]]) for k in range(5))
                                                       for c, p in zip(context, per)]
        return out

    def state_dict(self):
        return {k: getattr(self, k).state_dict() for k in ("enc", "actor", "q1", "q2", "q1t", "q2t")} | \
            {"log_alpha": self.log_alpha.detach(), "iteration": self.iteration}

    def load_state_dict(self, sd):
        for k in ("enc", "actor", "q1", "q2", "q1t", "q2t"):
            getattr(self, k).load_state_dict(sd[k])
        with torch.no_grad():
            self.log_alpha.copy_(sd["log_alpha"])
        self.iteration = sd.get("iteration", 0)
