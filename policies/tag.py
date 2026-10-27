"""Tight-aggressive heuristic policy."""


def policy(state, idx):
    p = state.players[idx]
    if p.folded or p.allin:
        return ("fold", None)
    max_bet = max(x.bet_this_round for x in state.players)
    to_call = max_bet - p.bet_this_round
    # simple heuristic: fold ~55%, call ~25%, raise ~20%
    import random
    r = random.random()
    if to_call == 0:
        if r < 0.6:
            return ("check", None)
        return ("raise", 1.0)
    if r < 0.55:
        return ("fold", None)
    if r < 0.8:
        return ("call", None)
    return ("raise", 1.5)