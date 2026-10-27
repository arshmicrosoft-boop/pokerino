"""Pure pot-odds decision policy."""

from math_core.probability import pot_odds_threshold


def policy(state, idx):
    p = state.players[idx]
    if p.folded or p.allin:
        return ("fold", None)
    max_bet = max(x.bet_this_round for x in state.players)
    to_call = max_bet - p.bet_this_round
    pot = state.pot
    if to_call == 0:
        return ("check", None)
    threshold = pot_odds_threshold(pot, to_call)
    # assume ~30% equity as default (placeholder; real impl uses equity calc)
    equity = 0.30
    if equity > threshold:
        return ("call", None)
    return ("fold", None)