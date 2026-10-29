from math_core.probability import pot_odds_threshold, bluff_breakeven, ev_call


def test_pot_odds_threshold():
    # pot 40, bet 10 -> 10/(40+20)=0.1667
    assert abs(pot_odds_threshold(40, 10) - 10/60) < 1e-9


def test_bluff_breakeven():
    # pot 40, risk 20 -> 20/(40+20)=0.3333
    assert abs(bluff_breakeven(40, 20) - 20/60) < 1e-9
    # pot 40, risk 40 -> 40/80 = 0.5
    assert abs(bluff_breakeven(40, 40) - 0.5) < 1e-9


def test_ev_call():
    # equity 0.5, pot 40, bet 10 -> 0.5*50 - 0.5*10 = 25-5=20
    assert abs(ev_call(0.5, 40, 10) - 20.0) < 1e-9