from math_core.combinatorics import combos_for_hand_type, parse_range, hand_combos_from_string


def test_combos():
    assert combos_for_hand_type("AA") == 6
    assert combos_for_hand_type("AKs") == 4
    assert combos_for_hand_type("AKo") == 12
    assert combos_for_hand_type("AK") == 16


def test_parse_range_aa():
    combos = parse_range("AA")
    assert len(combos) == 6


def test_parse_range_ak():
    combos = parse_range("AKs")
    assert len(combos) == 4


def test_hand_combos_from_string():
    combos = hand_combos_from_string("AA")
    assert len(combos) == 6