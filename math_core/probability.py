"""Probability, EV, pot odds, implied odds, fold equity, rake."""

def pot_odds_threshold(pot, bet):
    """Equity threshold for calling. pot=before villain bet, bet=villain bet."""
    # threshold = bet / (pot + 2*bet)
    denom = pot + 2 * bet
    if denom <= 0:
        return 1.0
    return bet / denom


def pot_odds_ratio(pot, bet):
    """Return pot:bet ratio (e.g. 4.0 means 4:1)."""
    if bet <= 0:
        return float("inf")
    return (pot + bet) / bet


def bluff_breakeven(pot, risk):
    """Minimum fold frequency for a bluff to be +EV. Assumes zero equity when called."""
    denom = pot + risk
    if denom <= 0:
        return 1.0
    return risk / denom


def fold_equity_ev(pot, risk, fold_prob, equity_if_called=0.0):
    """EV of a bluff/semi-bluff.
    pot: current pot before your bet
    risk: your bet size
    fold_prob: probability opponent folds
    equity_if_called: your equity when called
    """
    win_if_fold = pot
    # if called: you put in `risk`, pot becomes pot+risk (opponent calls risk) -> total pot+risk+risk? 
    # Net gain if win when called = pot + risk (opponent's call). Loss if lose = risk.
    ev_called = equity_if_called * (pot + risk) - (1 - equity_if_called) * risk
    return fold_prob * win_if_fold + (1 - fold_prob) * ev_called - (1 - fold_prob) * 0
    # subtract nothing extra; ev already net of risk


def semi_bluff_ev(pot, risk, fold_prob, equity_if_called):
    """Alias with explicit name; same formula."""
    return fold_equity_ev(pot, risk, fold_prob, equity_if_called)


def implied_odds(pot, cost, expected_future_win):
    """Implied odds ratio including expected future winnings."""
    denom = cost
    if denom <= 0:
        return float("inf")
    return (pot + expected_future_win) / denom


def implied_odds_threshold(pot, cost, expected_future_win):
    """Equity threshold when implied odds considered."""
    total = pot + expected_future_win + cost
    if total <= 0:
        return 1.0
    return cost / total


def rake_amount(pot, rake_pct=0.05, rake_cap=None):
    """Calculate rake taken from pot."""
    r = pot * rake_pct
    if rake_cap is not None:
        r = min(r, rake_cap)
    return r


def net_pot(pot, rake_pct=0.05, rake_cap=None):
    return pot - rake_amount(pot, rake_pct, rake_cap)


def ev_call(equity, pot, bet):
    """EV of calling a bet. equity = your equity, pot = pot before villain bet, bet = villain bet."""
    # If call: risk bet, win pot+bet if win
    return equity * (pot + bet) - (1 - equity) * bet


def ev_raise_value(equity, pot, bet, raise_size):
    """Simplified EV of a value raise (opponent calls)."""
    # you raise to raise_size; opponent calls raise_size
    # net gain if win = pot + bet + raise_size (opponent's call contribution)
    return equity * (pot + bet + raise_size) - (1 - equity) * raise_size