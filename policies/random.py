"""Random policy."""

import random


def policy(state, idx):
    legal = _legal(state, idx)
    if not legal:
        return ("fold", None)
    return random.choice(legal)


def _legal(state, idx):
    from simulation.engine import Engine
    # replicate legal actions logic
    p = state.players[idx]
    if p.folded or p.allin:
        return []
    max_bet = max(x.bet_this_round for x in state.players)
    to_call = max_bet - p.bet_this_round
    acts = [("fold", None)]
    if to_call == 0:
        acts.append(("check", None))
    else:
        if p.stack >= to_call:
            acts.append(("call", None))
    if p.stack > to_call:
        acts.append(("raise", 1.0))
        acts.append(("allin", None))
    return acts