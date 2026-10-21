"""Hand evaluator: 5-card and 7-card.

Returns a comparable rank tuple. Higher tuple = better hand.
Format: (category, *tiebreakers) where category:
  8 = straight flush
  7 = four of a kind
  6 = full house
  5 = flush
  4 = straight
  3 = three of a kind
  2 = two pair
  1 = one pair
  0 = high card

For comparison, tuples are compared lexicographically; ensure all tuples
of the same category have the same length.
"""

from math_core.cards import card_rank, card_suit, RANKS


def _rank_counts(cards):
    counts = [0] * 13
    for c in cards:
        counts[card_rank(c)] += 1
    return counts


def _suit_counts(cards):
    counts = [0] * 4
    for c in cards:
        counts[card_suit(c)] += 1
    return counts


def evaluate_5(cards):
    """Evaluate exactly 5 cards. Returns a comparable tuple (higher = better)."""
    assert len(cards) == 5
    ranks = _rank_counts(cards)
    suits = _suit_counts(cards)

    # Flush check
    flush_suit = None
    for s in range(4):
        if suits[s] == 5:
            flush_suit = s
            break

    # Straight check (on rank mask)
    rank_mask = 0
    for c in cards:
        rank_mask |= 1 << card_rank(c)
    # ace-low handling
    straight_high = -1
    for i in range(8, -1, -1):
        if (rank_mask & (0b11111 << i)) == (0b11111 << i):
            straight_high = i + 4
            break
    if straight_high == -1 and (rank_mask & 0b11111) == 0b11111 and (rank_mask >> 12) & 1:
        # ace-low: A-2-3-4-5
        straight_high = 3  # 5-high

    # Straight flush
    if flush_suit is not None:
        flush_mask = 0
        for c in cards:
            if card_suit(c) == flush_suit:
                flush_mask |= 1 << card_rank(c)
        sf_high = -1
        for i in range(8, -1, -1):
            if (flush_mask & (0b11111 << i)) == (0b11111 << i):
                sf_high = i + 4
                break
        if sf_high == -1 and (flush_mask & 0b11111) == 0b11111 and (flush_mask >> 12) & 1:
            sf_high = 3
        if sf_high != -1:
            return (8, sf_high)

    # Quads
    quads = [r for r in range(13) if ranks[r] == 4]
    if quads:
        q = quads[0]
        kicker = max(r for r in range(13) if ranks[r] > 0 and r != q)
        return (7, q, kicker)

    # Full house
    trips = [r for r in range(13) if ranks[r] == 3]
    pairs = [r for r in range(13) if ranks[r] == 2]
    if trips and (len(trips) >= 2 or pairs):
        t = max(trips)
        # second trips or best pair
        if len(trips) >= 2:
            p = max(r for r in trips if r != t)
        else:
            p = max(pairs)
        return (6, t, p)

    # Flush
    if flush_suit is not None:
        flush_ranks = sorted([card_rank(c) for c in cards if card_suit(c) == flush_suit], reverse=True)
        return (5, *flush_ranks[:5])

    # Straight
    if straight_high != -1:
        return (4, straight_high)

    # Three of a kind
    if trips:
        t = max(trips)
        kickers = sorted([r for r in range(13) if ranks[r] > 0 and r != t], reverse=True)[:2]
        return (3, t, *kickers)

    # Two pair
    if len(pairs) >= 2:
        p1, p2 = sorted(pairs, reverse=True)[:2]
        kicker = max(r for r in range(13) if ranks[r] > 0 and r not in (p1, p2))
        return (2, p1, p2, kicker)

    # One pair
    if len(pairs) == 1:
        p = pairs[0]
        kickers = sorted([r for r in range(13) if ranks[r] > 0 and r != p], reverse=True)[:3]
        return (1, p, *kickers)

    # High card
    hc = sorted([r for r in range(13) if ranks[r] > 0], reverse=True)[:5]
    return (0, *hc)


def evaluate_7(cards):
    """Evaluate 7 cards by trying all 21 five-card combinations."""
    assert len(cards) == 7
    from itertools import combinations
    best = None
    for combo in combinations(cards, 5):
        r = evaluate_5(list(combo))
        if best is None or r > best:
            best = r
    return best


def hand_rank_7(cards):
    """Return an integer rank 0..N where higher = better (for sorting)."""
    # Convert tuple to a comparable integer via lexicographic encoding.
    t = evaluate_7(cards)
    # Encode: category (0-8) * 13^5 + ... simplified: just return tuple, Python compares tuples.
    return t


# Convenience: numeric score for sorting (higher better)
def score_7(cards):
    return evaluate_7(cards)