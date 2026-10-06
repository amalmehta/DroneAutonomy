"""Registry: which methods exist for which problem, and how to build them."""
from .rl.meta.gradient import DomainRandomized, Fixed, GradMeta, Reptile
from .rl.problems import make_problem

# Methods that need training, per problem. Untrained baselines are listed separately.
TRAINED = {
    "tracking_residual": ["dr", "maml", "fomaml", "anil", "metasgd", "reptile", "pearl", "rl2"],
    "tracking_gains": ["dr", "maml", "fomaml", "metasgd", "reptile"],
    "navigation": ["dr", "e2e_dr", "maml", "fomaml", "anil", "metasgd", "reptile", "pearl", "rl2"],
}
UNTRAINED = {
    "tracking_residual": ["classical", "l1"],
    "tracking_gains": ["classical"],
    "navigation": ["classical", "classical_l1"],
}
# evaluated by loading another method's checkpoint
DERIVED = {"dr_finetune": "dr", "e2e_dr_finetune": "e2e_dr"}

LABELS = {
    "classical": "Classical (nominal)", "l1": "Classical + L1 adaptive", "classical_l1": "Classical + L1 adaptive",
    "dr": "Domain-randomised PPO", "dr_finetune": "DR PPO + fine-tune", "e2e_dr": "End-to-end DR PPO",
    "e2e_dr_finetune": "End-to-end DR PPO + fine-tune",
    "maml": "MAML", "fomaml": "FOMAML", "anil": "ANIL", "metasgd": "Meta-SGD", "reptile": "Reptile",
    "pearl": "PEARL", "rl2": "RL²",
}

ITERS = {  # meta-training iterations per (problem, method); tuned to the CPU budget
    "tracking_residual": {"dr": 300, "maml": 150, "fomaml": 150, "anil": 150, "metasgd": 150, "reptile": 120,
                          "pearl": 400, "rl2": 250},
    "tracking_gains": {"dr": 150, "maml": 100, "fomaml": 100, "metasgd": 100, "reptile": 80},
    "navigation": {"dr": 250, "e2e_dr": 250, "maml": 120, "fomaml": 120, "anil": 120, "metasgd": 120,
                   "reptile": 100, "pearl": 300, "rl2": 200},
}


def problem_for(problem_name, method_name, split="train"):
    if problem_name == "tracking_residual":
        return make_problem(problem_name, adaptive_base=(method_name == "l1"))
    if problem_name == "navigation":
        planner = "none" if method_name.startswith("e2e") else "oracle"
        return make_problem(problem_name, planner=planner, split=split)
    return make_problem(problem_name)


def build(problem_name, method_name, seed=0, problem=None):
    P = problem or problem_for(problem_name, method_name)
    if method_name in ("classical", "l1", "classical_l1"):
        return Fixed(P, name=method_name, seed=seed)
    if method_name in ("dr", "e2e_dr"):
        m = DomainRandomized(P, seed=seed)
        m.name = method_name
        return m
    if method_name in ("dr_finetune", "e2e_dr_finetune"):
        m = DomainRandomized(P, finetune=True, seed=seed)
        m.name = method_name
        return m
    if method_name in ("maml", "fomaml", "anil", "metasgd"):
        return GradMeta(P, method_name, seed=seed)
    if method_name == "reptile":
        return Reptile(P, total_iters=ITERS[problem_name]["reptile"], seed=seed)
    if method_name == "pearl":
        from .rl.meta.pearl import PEARL
        return PEARL(P, seed=seed)
    if method_name == "rl2":
        from .rl.meta.rl2 import RL2
        return RL2(P, seed=seed)
    raise ValueError(method_name)
