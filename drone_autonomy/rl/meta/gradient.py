"""Gradient-based meta-learning: MAML, FOMAML, ANIL, Meta-SGD, Reptile,
plus the non-meta baselines that share the same machinery:
domain-randomised PPO (DR) and DR + fine-tuning.

All inner loops for a meta-batch of T tasks run at once: shared parameters
are expanded to per-task views (T, ...) and one backward pass of the summed
per-task losses yields every task's gradient.
"""
import numpy as np
import torch

from ..nets import expand_params
from ..rollout import clip_loss, pg_loss


def _seed(rng):
    return int(rng.integers(0, 2**31 - 1))


def summarize(stats, prefix, problem):
    keys = ("return",) + tuple(problem.log_keys)
    return {f"{prefix}_{k}": float(np.nanmean(stats[k])) for k in keys}


class Method:
    """Common interface used by the trainer and the benchmark."""
    name = "method"
    adapts = True

    def __init__(self, problem, seed=0):
        self.problem = problem
        self.policy = problem.policy
        self.rng = np.random.default_rng(seed)
        torch.manual_seed(seed)
        self.iteration = 0

    def shared_params(self):
        return list(self.policy.params)

    # --- adaptation used both in meta-training (some methods) and evaluation
    def adapt(self, params_rep, batch):
        raise NotImplementedError

    @torch.no_grad()
    def _detach(self, ps):
        return [p.detach().clone() for p in ps]

    def adaptation_curve(self, tasks, stages, E=10, E_eval=4, seed=0, eval_problem=None):
        """Evaluate (deterministically) before and after each adaptation stage.

        One stage = E exploratory episodes per task + one adaptation update.
        Exploration always uses self.problem; evaluation uses eval_problem if
        given (e.g. the full online-mapping stack).
        """
        rng = np.random.default_rng(seed)
        T = len(tasks)
        ev = eval_problem or self.problem
        params = self._detach(expand_params(self.shared_params(), T))
        out = []
        for s in range(stages + 1):
            _, st = ev.collect(params, tasks, E_eval, _seed(rng), deterministic=True)
            st["episodes_used"] = s * E
            out.append(st)
            if s < stages and self.adapts:
                batch, _ = self.problem.collect(params, tasks, E, _seed(rng))
                params = self._detach(self.adapt([p.detach().requires_grad_(True) for p in params], batch))
        return out

    def state_dict(self):
        return {"policy": self.policy.state_dict(), "iteration": self.iteration}

    def load_state_dict(self, sd):
        self.policy.load_state_dict(sd["policy"])
        self.iteration = sd.get("iteration", 0)


class GradMeta(Method):
    """MAML family with a policy-gradient inner step.

    variant: 'maml' (second order), 'fomaml' (first order), 'anil' (adapt only
    the output head, second order), 'metasgd' (learned per-parameter inner
    learning rates, second order).
    """

    def __init__(self, problem, variant="maml", meta_batch=16, E=10, inner_lr=0.1,
                 outer_lr=1e-3, outer_epochs=3, seed=0):
        super().__init__(problem, seed)
        self.name = variant
        self.variant, self.T, self.E = variant, meta_batch, E
        self.outer_epochs = outer_epochs
        n = len(self.policy.params)
        self.adapt_idx = list(self.policy.head_idx) if variant == "anil" else list(range(n))
        self.second_order = variant != "fomaml"
        if variant == "metasgd":
            self.alpha = torch.nn.ParameterList(
                [torch.nn.Parameter(torch.full_like(self.policy.params[i], inner_lr)) for i in self.adapt_idx])
        else:
            self.alpha = [torch.tensor(inner_lr)] * len(self.adapt_idx)
        extra = list(self.alpha) if variant == "metasgd" else []
        self.opt = torch.optim.Adam(list(self.policy.params) + extra, lr=outer_lr)

    def adapt(self, params_rep, batch, create_graph=False):
        loss = pg_loss(self.policy.log_prob(params_rep, batch), batch).sum()
        targets = [params_rep[i] for i in self.adapt_idx]
        grads = torch.autograd.grad(loss, targets, create_graph=create_graph, allow_unused=True)
        new = list(params_rep)
        for j, (i, g) in enumerate(zip(self.adapt_idx, grads)):
            if g is None:
                continue
            g = g.clamp(-10, 10)  # guards rare huge PG gradients
            new[i] = params_rep[i] - self.alpha[j] * g
        return new

    def train_step(self):
        T, E = self.T, self.E
        tasks = self.problem.sample_tasks(T, self.rng)
        theta = self.shared_params()
        pre, pre_st = self.problem.collect(self._detach(expand_params(theta, T)), tasks, E, _seed(self.rng))
        post, post_st = None, None
        for ep in range(self.outer_epochs):
            rep = expand_params(theta, T)
            adapted = self.adapt(rep, pre, create_graph=self.second_order)
            if post is None:
                post, post_st = self.problem.collect(self._detach(adapted), tasks, E, _seed(self.rng))
            loss = clip_loss(self.policy.log_prob(adapted, post), post).mean()
            self.opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
            self.opt.step()
        self.iteration += 1
        return {**summarize(pre_st, "pre", self.problem), **summarize(post_st, "post", self.problem),
                "loss": float(loss)}

    def state_dict(self):
        sd = super().state_dict()
        if self.variant == "metasgd":
            sd["alpha"] = [a.detach().clone() for a in self.alpha]
        return sd

    def load_state_dict(self, sd):
        super().load_state_dict(sd)
        if self.variant == "metasgd":
            with torch.no_grad():
                for a, v in zip(self.alpha, sd["alpha"]):
                    a.copy_(v)


def ppo_adapt(policy, params_rep, batch, lr, epochs):
    """Per-task PPO fine-tuning (Adam) from given per-task params; no graph."""
    leaf = [p.detach().clone().requires_grad_(True) for p in params_rep]
    opt = torch.optim.Adam(leaf, lr=lr)
    for _ in range(epochs):
        loss = clip_loss(policy.log_prob(leaf, batch), batch).sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return [p.detach() for p in leaf]


class Reptile(Method):
    """Reptile: K inner PPO updates per task, then move theta toward the mean."""
    name = "reptile"

    def __init__(self, problem, meta_batch=16, E=10, inner_steps=3, inner_lr=3e-3, inner_epochs=4,
                 outer_lr=0.5, outer_lr_final=0.1, total_iters=200, seed=0):
        super().__init__(problem, seed)
        self.T, self.E, self.K = meta_batch, E, inner_steps
        self.inner_lr, self.inner_epochs = inner_lr, inner_epochs
        self.eps0, self.eps1, self.total = outer_lr, outer_lr_final, total_iters

    def adapt(self, params_rep, batch):
        return ppo_adapt(self.policy, params_rep, batch, self.inner_lr, self.inner_epochs)

    def train_step(self):
        T, E = self.T, self.E
        tasks = self.problem.sample_tasks(T, self.rng)
        theta = self.shared_params()
        params = self._detach(expand_params(theta, T))
        first = None
        for k in range(self.K):
            batch, st = self.problem.collect(params, tasks, E, _seed(self.rng))
            first = first or st
            params = self.adapt(params, batch)
        frac = min(1.0, self.iteration / max(1, self.total))
        eps = self.eps0 + frac * (self.eps1 - self.eps0)
        with torch.no_grad():
            for p, q in zip(theta, params):
                p += eps * (q.mean(0) - p)
        self.iteration += 1
        return {**summarize(first, "pre", self.problem), **summarize(st, "post", self.problem)}


class DomainRandomized(Method):
    """Non-meta baseline: one policy trained with PPO over the whole task
    distribution (domain randomisation). As 'dr' it never adapts; as
    'dr_finetune' it is evaluated with the same PPO fine-tuning as Reptile."""

    def __init__(self, problem, finetune=False, batch_tasks=16, E=10, lr=3e-4, epochs=8,
                 ft_lr=3e-3, ft_epochs=4, seed=0):
        super().__init__(problem, seed)
        self.name = "dr_finetune" if finetune else "dr"
        self.adapts = finetune
        self.T, self.E, self.epochs = batch_tasks, E, epochs
        self.ft_lr, self.ft_epochs = ft_lr, ft_epochs
        self.opt = torch.optim.Adam(self.policy.params, lr=lr)

    def adapt(self, params_rep, batch):
        return ppo_adapt(self.policy, params_rep, batch, self.ft_lr, self.ft_epochs)

    def train_step(self):
        tasks = self.problem.sample_tasks(self.T, self.rng)
        theta = self.shared_params()
        batch, st = self.problem.collect(self._detach(theta), tasks, self.E, _seed(self.rng))
        for _ in range(self.epochs):
            loss = clip_loss(self.policy.log_prob(theta, batch), batch).mean() \
                - 1e-3 * self.policy.entropy(theta)
            self.opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
            self.opt.step()
        self.iteration += 1
        return summarize(st, "post", self.problem)


class Fixed(Method):
    """No learning: the classical controller alone (zero residual / nominal gains)."""
    adapts = False

    def __init__(self, problem, name="classical", seed=0):
        super().__init__(problem, seed)
        self.name = name
        with torch.no_grad():
            for p in self.policy.params:
                p.zero_()
            self.policy.params[-1].fill_(-20.0)  # tiny std, mean zero

    def train_step(self):
        return {}

