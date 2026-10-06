"""RL^2 (Duan et al., 2016; Wang et al., 2016): a recurrent policy that adapts
through its hidden state.

A trial is K consecutive episodes on the same task; the GRU's hidden state
is carried across episode boundaries and sees the previous action, reward
and an episode-start flag, so it can infer the task from experience. Trained
with recurrent PPO on whole trials (full backprop through time).
"""
import math

import numpy as np
import torch
from torch import nn

from ..rollout import GAMMA, LAM

LOG2PI = math.log(2 * math.pi)


class RecurrentPolicy(nn.Module):
    def __init__(self, obs_dim, act_dim, hidden=128):
        super().__init__()
        self.inp = nn.Sequential(nn.Linear(obs_dim + act_dim + 2, hidden), nn.Tanh())
        self.gru = nn.GRU(hidden, hidden)
        self.mu = nn.Linear(hidden, act_dim)
        self.v = nn.Linear(hidden, 1)
        self.log_std = nn.Parameter(torch.full((act_dim,), -0.7))
        nn.init.orthogonal_(self.mu.weight, 0.01)
        nn.init.zeros_(self.mu.bias)

    def forward(self, x, h=None):
        """x (L, B, d) -> mean (L, B, a), value (L, B), h"""
        y, h = self.gru(self.inp(x), h)
        return self.mu(y), self.v(y).squeeze(-1), h

    def logp(self, mean, act):
        ls = self.log_std.clamp(-3, 0.5)
        return (-0.5 * ((act - mean) / ls.exp()) ** 2 - ls - 0.5 * LOG2PI).sum(-1)


class RL2:
    name = "rl2"
    adapts = True

    def __init__(self, problem, seed=0, n_trials=48, K=3, lr=3e-4, epochs=4, minibatches=4, clip=0.2):
        self.problem = problem
        self.rng = np.random.default_rng(seed)
        torch.manual_seed(seed)
        env = problem.env(1)
        self.od, self.ad = env.obs_dim, env.act_dim
        self.net = RecurrentPolicy(self.od, self.ad)
        self.opt = torch.optim.Adam(self.net.parameters(), lr=lr)
        self.n, self.K, self.epochs, self.mb, self.clip = n_trials, K, epochs, minibatches, clip
        self.iteration = 0

    @torch.no_grad()
    def run_trials(self, tasks, K, deterministic, seed, problem=None):
        """Each env row runs K consecutive episodes of its task with carried hidden state."""
        n = len(tasks)
        env = (problem or self.problem).env(n)
        rng = np.random.default_rng(seed)
        h = None
        prev_a = np.zeros((n, self.ad), np.float32)
        prev_r = np.zeros(n, np.float32)
        X, A, R, M, V, LP = [], [], [], [], [], []
        per_episode = []
        for k in range(K):
            obs = env.reset(tasks, seed=int(rng.integers(1 << 30)))
            first = np.ones(n, np.float32)
            alive = np.ones(n, bool)
            ret = np.zeros(n)
            for _ in range(env.horizon):
                x = np.concatenate([obs, prev_a, prev_r[:, None], first[:, None]], 1).astype(np.float32)
                mu, v, h = self.net(torch.as_tensor(x)[None], h)
                mu, v = mu[0], v[0]
                a = mu if deterministic else mu + self.net.log_std.clamp(-3, 0.5).exp() * torch.randn_like(mu)
                a_np = a.numpy()
                obs, r, done, info = env.step(a_np)
                X.append(x); A.append(a_np); R.append(r.astype(np.float32)); M.append(alive.astype(np.float32))
                V.append(v.numpy()); LP.append(self.net.logp(mu, a).numpy())
                ret += r
                prev_a = np.where(alive[:, None], np.clip(a_np, -1, 1), 0).astype(np.float32)
                prev_r = r.astype(np.float32)
                first = np.zeros(n, np.float32)
                alive = ~info["crashed"]
            per_episode.append({"return": ret.copy(), **env.metrics()})
        f = lambda L: torch.as_tensor(np.stack(L))
        return {"x": f(X), "act": f(A), "rew": f(R), "mask": f(M), "val": f(V), "logp": f(LP)}, per_episode

    def _gae(self, rew, val, mask):
        """GAE over each trial's live steps only. Steps after a crash are inert
        padding until the next episode starts; the trial (and the value
        bootstrap) continues across episode boundaries, as in RL^2."""
        rew, val, mask = rew.numpy(), val.numpy(), mask.numpy() > 0
        adv = np.zeros_like(rew)
        for j in range(rew.shape[1]):
            idx = np.nonzero(mask[:, j])[0]
            r, v = rew[idx, j], val[idx, j]
            g = 0.0
            for k in reversed(range(len(idx))):
                v_next = v[k + 1] if k + 1 < len(idx) else 0.0
                g = r[k] + GAMMA * v_next - v[k] + GAMMA * LAM * g
                adv[idx[k], j] = g
        adv, val = torch.as_tensor(adv), torch.as_tensor(val)
        return adv, adv + val

    def train_step(self):
        tasks = self.problem.sample_tasks(self.n, self.rng)
        data, eps = self.run_trials(tasks, self.K, False, int(self.rng.integers(1 << 30)))
        adv, ret = self._gae(data["rew"], data["val"], data["mask"])
        m = data["mask"]
        mu_a = (adv * m).sum() / m.sum()
        sd_a = (((adv - mu_a) * m) ** 2).sum() / m.sum()
        adv = (adv - mu_a) / (sd_a.sqrt() + 1e-8)
        idx = np.arange(self.n)
        for _ in range(self.epochs):
            self.rng.shuffle(idx)
            for chunk in np.array_split(idx, self.mb):
                c = torch.as_tensor(chunk)
                mu, v, _ = self.net(data["x"][:, c])
                lp = self.net.logp(mu, data["act"][:, c])
                ratio = torch.exp(lp - data["logp"][:, c])
                a, mm = adv[:, c], m[:, c]
                pg = -(torch.min(ratio * a, ratio.clamp(1 - self.clip, 1 + self.clip) * a) * mm).sum() / mm.sum()
                vl = (((v - ret[:, c]) ** 2) * mm).sum() / mm.sum()
                loss = pg + 0.5 * vl
                self.opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.net.parameters(), 0.5)
                self.opt.step()
        self.iteration += 1
        out = {"pre_return": float(eps[0]["return"].mean()), "post_return": float(eps[-1]["return"].mean())}
        for key in self.problem.log_keys:
            out[f"pre_{key}"] = float(np.nanmean(eps[0][key]))
            out[f"post_{key}"] = float(np.nanmean(eps[-1][key]))
        return out

    def adaptation_curve(self, tasks, stages, E=10, E_eval=4, seed=0, eval_problem=None):
        """Stage s = performance in episode s+1 of a trial (deterministic actions).
        RL^2 adapts inside its hidden state, so the whole trial runs on eval_problem."""
        T = len(tasks)
        _, eps = self.run_trials(tasks.repeat(E_eval), stages + 1, True, seed, eval_problem)
        out = []
        for s, st in enumerate(eps):
            d = {k: np.asarray(v).reshape(T, E_eval) for k, v in st.items()}
            d["episodes_used"] = s
            out.append(d)
        return out

    def state_dict(self):
        return {"net": self.net.state_dict(), "iteration": self.iteration}

    def load_state_dict(self, sd):
        self.net.load_state_dict(sd["net"])
        self.iteration = sd.get("iteration", 0)
