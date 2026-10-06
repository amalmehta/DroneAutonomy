"""Functional policies for meta-learning.

Parameters live in plain lists of tensors so that MAML-style algorithms can
build adapted copies (theta' = theta - alpha * grad) and differentiate through
them. Every tensor may carry an optional leading *task* dimension: a batch of
T per-task parameter sets is evaluated on obs shaped (T, N, d) in one pass,
which is how all tasks' inner loops run at once.
"""
import math

import numpy as np
import torch
from torch import nn

from ..config import DEFAULT_GAINS

LOG2PI = math.log(2 * math.pi)


def linear(x, W, b):
    if W.dim() == 3:          # per-task weights: x (T, N, i), W (T, i, o), b (T, o)
        return torch.baddbmm(b.unsqueeze(1), x, W)
    return x @ W + b


def gaussian_logp(x, mean, log_std):
    return (-0.5 * ((x - mean) / log_std.exp()) ** 2 - log_std - 0.5 * LOG2PI).sum(-1)


def expand_params(params, T):
    """Shared params -> per-task views (T, ...) that stay in the autograd graph."""
    return [p.unsqueeze(0).expand(T, *p.shape) for p in params]


class GaussianMLP(nn.Module):
    """Diagonal-Gaussian MLP policy; log_std is state independent."""

    def __init__(self, obs_dim, act_dim, hidden=(64, 64), init_log_std=-0.7):
        super().__init__()
        sizes = (obs_dim,) + tuple(hidden) + (act_dim,)
        ps = []
        for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
            W = torch.empty(a, b)
            nn.init.orthogonal_(W.T, gain=0.01 if i == len(sizes) - 2 else math.sqrt(2))
            ps += [nn.Parameter(W), nn.Parameter(torch.zeros(b))]
        ps.append(nn.Parameter(torch.full((act_dim,), init_log_std)))
        self.params = nn.ParameterList(ps)
        self.n_layers = len(sizes) - 1
        self.obs_dim, self.act_dim = obs_dim, act_dim

    @property
    def head_idx(self):
        """Indices of the output layer + log_std (the part ANIL adapts)."""
        L = len(self.params)
        return [L - 3, L - 2, L - 1]

    def mean(self, params, obs):
        h = obs
        for i in range(self.n_layers):
            h = linear(h, params[2 * i], params[2 * i + 1])
            if i < self.n_layers - 1:
                h = torch.tanh(h)
        return h

    def log_std(self, params, like):
        ls = params[-1].clamp(-3.0, 0.5)
        return ls.unsqueeze(-2) if ls.dim() == 2 else ls  # (T, 1, a) for per-task

    def log_prob(self, params, batch):
        mu = self.mean(params, batch["obs"])
        return gaussian_logp(batch["act"], mu, self.log_std(params, mu))

    def entropy(self, params):
        return (params[-1].clamp(-3.0, 0.5) + 0.5 * (1 + LOG2PI)).sum(-1).mean()

    @torch.no_grad()
    def act(self, params, obs, deterministic=False):
        mu = self.mean(params, obs)
        if deterministic:
            return mu
        return mu + self.log_std(params, mu).exp() * torch.randn_like(mu)


class GainPolicy(nn.Module):
    """Episodic Gaussian over log controller gains (parameter-exploring PG).

    gains = nominal * exp(mu + std * eps); the 'action' is eps-scaled mu.
    """

    def __init__(self, n_gains=7, init_log_std=-1.6):
        super().__init__()
        self.params = nn.ParameterList([nn.Parameter(torch.zeros(n_gains)),
                                        nn.Parameter(torch.full((n_gains,), init_log_std))])
        self.nominal = torch.tensor(DEFAULT_GAINS.as_array(), dtype=torch.float32)
        self.head_idx = [0, 1]

    def log_std(self, params):
        ls = params[1].clamp(-4.0, 0.0)
        return ls.unsqueeze(-2) if ls.dim() == 2 else ls

    def log_prob(self, params, batch):
        mu = params[0].unsqueeze(-2) if params[0].dim() == 2 else params[0]
        return gaussian_logp(batch["act"], mu, self.log_std(params))

    def entropy(self, params):
        return (params[1].clamp(-4.0, 0.0) + 0.5 * (1 + LOG2PI)).sum(-1).mean()

    @torch.no_grad()
    def sample(self, params, T, E, deterministic=False):
        mu = params[0].unsqueeze(-2) if params[0].dim() == 2 else params[0].expand(T, 1, -1)
        mu = mu.expand(T, E, -1)
        if deterministic:
            return mu.clone()
        return mu + self.log_std(params).exp() * torch.randn_like(mu)

    def to_gains(self, log_scale):
        return (self.nominal * torch.exp(torch.as_tensor(log_scale).clamp(-1.5, 1.5))).numpy().astype(np.float64)
