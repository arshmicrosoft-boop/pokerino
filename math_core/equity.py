"""Equity calculation: exact (preflop), representative sampling (flop), adaptive MC."""

import random
import numpy as np
from math_core.cards import full_deck, remove_cards, card_rank, card_suit
from math_core.hand_eval import evaluate_7, evaluate_5
from math_core.combinatorics import remove_blockers


def _deal_remaining(deck, n):
    return random.sample(deck, n)


def exact_equity_heads_up(hero_cards, villain_cards, board=()):
    """Exact equity for heads-up given known hole cards and partial board.
    Enumerates all possible completions of the board."""
    known = list(hero_cards) + list(villain_cards) + list(board)
    deck = remove_cards(full_deck(), known)
    remaining = 5 - len(board)
    if remaining == 0:
        # showdown
        h = evaluate_7(list(hero_cards) + list(board))
        v = evaluate_7(list(villain_cards) + list(board))
        if h > v:
            return 1.0
        if h < v:
            return 0.0
        return 0.5
    # enumerate combinations of remaining cards
    from itertools import combinations
    wins = 0.0
    total = 0
    for combo in combinations(deck, remaining):
        full_board = list(board) + list(combo)
        h = evaluate_7(list(hero_cards) + full_board)
        v = evaluate_7(list(villain_cards) + full_board)
        total += 1
        if h > v:
            wins += 1.0
        elif h == v:
            wins += 0.5
    return wins / total if total > 0 else 0.5


def monte_carlo_equity(hero_cards, villain_cards, board=(), n_samples=10000, seed=None):
    """Monte Carlo equity for heads-up. Adaptive n via caller."""
    rng = random.Random(seed)
    known = set(list(hero_cards) + list(villain_cards) + list(board))
    deck = [c for c in full_deck() if c not in known]
    remaining = 5 - len(board)
    if remaining < 0:
        remaining = 0
    wins = 0.0
    total = 0
    for _ in range(n_samples):
        runout = rng.sample(deck, remaining)
        full_board = list(board) + runout
        h = evaluate_7(list(hero_cards) + full_board)
        v = evaluate_7(list(villain_cards) + full_board)
        total += 1
        if h > v:
            wins += 1.0
        elif h == v:
            wins += 0.5
    return wins / total if total > 0 else 0.5


def adaptive_n(pot_bb, stack_bb, n_opponents, street):
    """Determine adaptive sample count for MC."""
    base = 10000
    # deeper stacks -> more samples
    if stack_bb > 100:
        base = int(base * 1.5)
    if stack_bb > 200:
        base = int(base * 2.0)
    # multiway -> more samples
    if n_opponents >= 2:
        base = int(base * (1 + 0.5 * (n_opponents - 1)))
    # early streets -> more samples
    if street in ("preflop", "flop"):
        base = int(base * 1.5)
    # cap
    base = min(base, 200000)
    base = max(base, 10000)
    return base


def range_vs_range_equity(hero_range, villain_range, board=(), n_samples=5000, seed=None):
    """Monte Carlo equity of a range vs a range (heads-up)."""
    rng = random.Random(seed)
    # flatten combos
    hero_combos = list(hero_range)
    vill_combos = list(villain_range)
    if not hero_combos or not vill_combos:
        return 0.5
    wins = 0.0
    total = 0
    for _ in range(n_samples):
        hc = rng.choice(hero_combos)
        vc = rng.choice(vill_combos)
        if set(hc) & set(vc):
            continue
        known = set(list(hc) + list(vc) + list(board))
        deck = [c for c in full_deck() if c not in known]
        remaining = 5 - len(board)
        runout = rng.sample(deck, remaining)
        full_board = list(board) + runout
        h = evaluate_7(list(hc) + full_board)
        v = evaluate_7(list(vc) + full_board)
        total += 1
        if h > v:
            wins += 1.0
        elif h == v:
            wins += 0.5
    return wins / total if total > 0 else 0.5