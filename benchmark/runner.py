"""Seed-locked A/B benchmark runner."""

import random
import numpy as np
from simulation.engine import Engine


def run_policy(policy_fn, opponent_policy_fn, n_hands, seed, **engine_kwargs):
    """Run n_hands of a policy vs an opponent policy. Returns list of per-hand profits (for player 0)."""
    rng = random.Random(seed)
    profits = []
    for h in range(n_hands):
        hand_seed = rng.randint(0, 10**9)
        eng = Engine(seed=hand_seed, **engine_kwargs)
        state, result = eng.run_hand(policy_fn, opponent_policy_fn)
        # player 0 profit = final stack - starting stack
        p0 = state.players[0]
        profit = p0.stack - eng.starting_stack
        profits.append(profit)
    return profits


def ab_test(policy_a, policy_b, opponent_policy, n_hands, seed, **engine_kwargs):
    """Run policy_a and policy_b against the same opponent with seed-locked boards.
    Returns (profits_a, profits_b)."""
    profits_a = run_policy(policy_a, opponent_policy, n_hands, seed, **engine_kwargs)
    profits_b = run_policy(policy_b, opponent_policy, n_hands, seed + 1, **engine_kwargs)
    return profits_a, profits_b


def compare_policies(policy_a, policy_b, opponent_policy, n_hands=1000, seed=42,
                     **engine_kwargs):
    from benchmark.metrics import bb_per_100, confidence_interval, std_dev
    pa = run_policy(policy_a, opponent_policy, n_hands, seed, **engine_kwargs)
    pb = run_policy(policy_b, opponent_policy, n_hands, seed + 999, **engine_kwargs)
    return {
        "policy_a": {
            "bb_per_100": bb_per_100(pa),
            "std": std_dev(pa),
            "ci": confidence_interval(pa),
            "n": len(pa),
        },
        "policy_b": {
            "bb_per_100": bb_per_100(pb),
            "std": std_dev(pb),
            "ci": confidence_interval(pb),
            "n": len(pb),
        },
    }