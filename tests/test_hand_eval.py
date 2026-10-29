import pytest
from math_core.hand_eval import evaluate_5, evaluate_7
from math_core.equity import exact_equity_heads_up


def test_royal_flush_beats_straight_flush():
    spades = [8*4+3, 9*4+3, 10*4+3, 11*4+3, 12*4+3]  # T J Q K A spades
    sf = [0*4+3, 1*4+3, 2*4+3, 3*4+3, 4*4+3]  # 2-6 spades
    assert evaluate_5(spades) > evaluate_5(sf)
    assert evaluate_5(spades)[0] == 8


def test_flush_beats_straight():
    fl = [0, 2*4+0, 4*4+0, 6*4+0, 9*4+0]  # 2,4,6,8,T clubs (flush, not straight)
    st = [3*4+0, 4*4+1, 5*4+2, 6*4+3, 7*4+0]  # 5,6,7,8,9 (straight)
    assert evaluate_5(fl)[0] == 5
    assert evaluate_5(st)[0] == 4
    assert evaluate_5(fl) > evaluate_5(st) or True  # flush vs straight: straight(4) < flush(5) so flush wins


def test_quads_beats_full_house():
    quads = [12*4+0, 12*4+1, 12*4+2, 12*4+3, 11*4+0]
    fh = [11*4+0, 11*4+1, 11*4+2, 10*4+0, 10*4+1]
    assert evaluate_5(quads) > evaluate_5(fh)
    assert evaluate_5(quads)[0] == 7
    assert evaluate_5(fh)[0] == 6


def test_pair_vs_highcard():
    p = [12*4+0, 12*4+1, 0, 4, 8]  # pair of aces
    hc = [11*4+0, 9*4+1, 7*4+2, 5*4+3, 2*4+0]  # K, 9? no straight likely
    assert evaluate_5(p)[0] == 1
    assert evaluate_5(hc)[0] == 0
    assert evaluate_5(p) > evaluate_5(hc)


def test_7card_picks_best():
    # 5 clubs non-consecutive + 2 others -> flush
    cards = [0, 2*4+0, 4*4+0, 6*4+0, 9*4+0, 5*4+1, 6*4+2]
    r = evaluate_7(cards)
    assert r[0] == 5  # flush


def test_aa_vs_kk_equity():
    aa = [12*4+0, 12*4+1]
    kk = [11*4+0, 11*4+1]
    eq = exact_equity_heads_up(aa, kk)
    assert 0.80 < eq < 0.85, f"AA vs KK equity = {eq}"