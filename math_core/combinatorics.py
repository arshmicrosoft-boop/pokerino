"""Combinatorics: combos, blockers, range counting."""

from math_core.cards import card_rank, card_suit, full_deck, remove_cards
from itertools import combinations


def combos_for_hand_type(hand_type: str) -> int:
    """Return number of combos for a hand type string.
    e.g. 'AA' -> 6, 'AKs' -> 4, 'AKo' -> 12, 'AK' -> 16
    """
    if len(hand_type) == 2 and hand_type[0] == hand_type[1]:
        return 6  # pocket pair
    if len(hand_type) == 3:
        if hand_type[2].lower() == 's':
            return 4  # suited
        if hand_type[2].lower() == 'o':
            return 12  # offsuit
    if len(hand_type) == 2:
        return 16  # both suited + offsuit
    return 0


def count_combos(cards_known, dead_cards=()):
    """Count remaining combos for a set of known cards given dead cards."""
    deck = remove_cards(full_deck(), list(dead_cards) + list(cards_known))
    # number of ways to choose remaining from deck
    from math import comb
    n = len(deck)
    k = 5 - len(cards_known) if len(cards_known) <= 5 else 0
    if k < 0:
        return 0
    return comb(n, k)


def remove_blockers(range_cards, known_cards):
    """Remove combos from a range that conflict with known cards."""
    known_set = set(known_cards)
    result = []
    for combo in range_cards:
        if not (set(combo) & known_set):
            result.append(combo)
    return result


def hand_combos_from_string(hand_str: str, dead_cards=()):
    """Generate actual card-combo list for a hand string like 'AA', 'AKs', 'AKo', 'AK'.
    Returns list of (card1, card2) tuples.
    """
    dead = set(dead_cards)
    result = []
    ranks = "23456789TJQKA"
    ri = {r: i for i, r in enumerate(ranks)}

    if len(hand_str) == 2 and hand_str[0] == hand_str[1]:
        # pocket pair
        r = ri[hand_str[0].upper()]
        cards_of_rank = [r * 4 + s for s in range(4) if r * 4 + s not in dead]
        for c1, c2 in combinations(cards_of_rank, 2):
            result.append((c1, c2))
    elif len(hand_str) == 3:
        r1 = ri[hand_str[0].upper()]
        r2 = ri[hand_str[1].upper()]
        suited = hand_str[2].lower() == 's'
        for s1 in range(4):
            for s2 in range(4):
                c1 = r1 * 4 + s1
                c2 = r2 * 4 + s2
                if c1 in dead or c2 in dead or c1 == c2:
                    continue
                if suited and s1 != s2:
                    continue
                if not suited and s1 == s2:
                    continue
                if (c1, c2) not in result and (c2, c1) not in result:
                    result.append((c1, c2))
    elif len(hand_str) == 2:
        # both suited and offsuit
        r1 = ri[hand_str[0].upper()]
        r2 = ri[hand_str[1].upper()]
        for s1 in range(4):
            for s2 in range(4):
                c1 = r1 * 4 + s1
                c2 = r2 * 4 + s2
                if c1 in dead or c2 in dead or c1 == c2:
                    continue
                if (c1, c2) not in result and (c2, c1) not in result:
                    result.append((c1, c2))
    return result


def parse_range(range_str: str, dead_cards=()):
    """Parse a range string like 'AA, AKs, 77+, A5s-A2s, KQo' into a list of card combos.
    Supports: exact hands (AA), suited/offsuit (AKs, AKo), plus notation (77+), range notation (A5s-A2s).
    """
    dead = list(dead_cards)
    combos = []
    tokens = [t.strip() for t in range_str.replace(";", ",").split(",") if t.strip()]
    ranks = "23456789TJQKA"
    ri = {r: i for i, r in enumerate(ranks)}

    for tok in tokens:
        tok = tok.strip()
        # range notation like A5s-A2s
        if "-" in tok and len(tok) >= 5:
            parts = tok.split("-")
            left, right = parts[0].strip(), parts[1].strip()
            # suited/offsuit suffix
            suffix = ""
            if left and left[-1].lower() in ("s", "o"):
                suffix = left[-1]
                left = left[:-1]
                right = right[:-1] if right[-1].lower() in ("s", "o") else right
            r1 = left[0].upper()
            r2_left = ri[left[1].upper()]
            r2_right = ri[right[1].upper()]
            lo, hi = min(r2_left, r2_right), max(r2_left, r2_right)
            for r2i in range(lo, hi + 1):
                r2c = ranks[r2i]
                hs = r1 + r2c + suffix if suffix else r1 + r2c
                combos.extend(hand_combos_from_string(hs, dead))
            continue
        # plus notation like 77+ or A5s+
        if tok.endswith("+"):
            base = tok[:-1]
            if len(base) == 2 and base[0] == base[1]:
                # pocket pair plus
                start = ri[base[0].upper()]
                for r in range(start, 13):
                    combos.extend(hand_combos_from_string(ranks[r] + ranks[r], dead))
            elif len(base) >= 2:
                suffix = ""
                if base[-1].lower() in ("s", "o"):
                    suffix = base[-1]
                    base = base[:-1]
                r1 = base[0].upper()
                r2i = ri[base[1].upper()]
                # plus means lower second card down to 2
                for r2 in range(0, r2i + 1):
                    r2c = ranks[r2]
                    hs = r1 + r2c + suffix if suffix else r1 + r2c
                    combos.extend(hand_combos_from_string(hs, dead))
            continue
        # exact hand
        combos.extend(hand_combos_from_string(tok, dead))

    # dedupe
    seen = set()
    out = []
    for c in combos:
        key = tuple(sorted(c))
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out