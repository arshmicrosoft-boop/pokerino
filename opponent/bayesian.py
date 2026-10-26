"""Bayesian range narrowing with Dirichlet priors and smoothing."""

import random
from math_core.combinatorics import hand_combos_from_string, parse_range


class BayesianRange:
    def __init__(self, prior_range_str="AA, KK, QQ, AKs, AKo", dead_cards=(), alpha=0.01):
        self.alpha = alpha  # smoothing
        self.dead = list(dead_cards)
        self.combos = parse_range(prior_range_str, self.dead)
        # weights: start uniform
        self.weights = [1.0 for _ in self.combos]
        self.n_obs = 0

    def update(self, action, likelihood_fn=None):
        """Update weights given an observed action. likelihood_fn(combo)->prob of action."""
        if likelihood_fn is None:
            likelihood_fn = lambda c: 1.0
        new_w = []
        for c, w in zip(self.combos, self.weights):
            # Dirichlet smoothing: never zero
            lk = max(self.alpha, likelihood_fn(c))
            new_w.append(w * lk + self.alpha)
        self.weights = new_w
        self.n_obs += 1

    def normalized(self):
        s = sum(self.weights)
        if s <= 0:
            return [1.0 / len(self.weights)] * len(self.weights)
        return [w / s for w in self.weights]

    def sample_combo(self, rng=None):
        if rng is None:
            rng = random
        w = self.normalized()
        return rng.choices(self.combos, weights=w, k=1)[0]

    def confidence(self):
        return min(1.0, self.n_obs / 50.0)

    def blend_with_prior(self, prior_weights, n):
        """Blend posterior with prior based on sample size."""
        w = min(1.0, n / 50.0)
        blended = []
        for pw, prw in zip(self.weights, prior_weights):
            blended.append(w * pw + (1 - w) * prw)
        self.weights = blended