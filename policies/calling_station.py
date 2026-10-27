"""Calling station: never folds, calls everything, rarely raises."""


def policy(state, idx):
    import random
    p = state.players[idx]
    if p.folded or p.allin:
        return ("fold", None)
    max_bet = max(x.bet_this_round for x in state.players)
    to_call = max_bet - p.bet_this_round
    r = random.random()
    if to_call == 0:
        if r < 0.05:
            return ("raise", 1.0)
        return ("check", None)
    if r < 0.05:
        return ("raise", 1.0)
    return ("call", None)