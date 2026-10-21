"""Card representation and deck management.

Cards are integers 0..51. Rank = card // 4 (0=2 .. 12=Ace). Suit = card % 4.
Bitmask helpers for fast flush/straight detection.
"""

RANKS = "23456789TJQKA"  # index 0..12
SUITS = "cdhs"            # clubs, diamonds, hearts, spades (index 0..3)

# Rank values: 2=0 ... Ace=12
RANK_VALUE = {r: i for i, r in enumerate(RANKS)}
SUIT_VALUE = {s: i for i, s in enumerate(SUITS)}


def make_card(rank_char: str, suit_char: str) -> int:
    """Create a card integer from rank and suit characters."""
    return RANK_VALUE[rank_char] * 4 + SUIT_VALUE[suit_char]


def card_rank(card: int) -> int:
    return card // 4


def card_suit(card: int) -> int:
    return card % 4


def card_str(card: int) -> str:
    return RANKS[card // 4] + SUITS[card % 4]


def parse_card(s: str) -> int:
    """Parse a 2-char string like 'Ah' or 'Td'."""
    return make_card(s[0].upper(), s[1].lower())


def parse_cards(s: str):
    """Parse a space/comma separated string of cards."""
    s = s.replace(",", " ")
    return [parse_card(tok) for tok in s.split() if tok.strip()]


def full_deck():
    return list(range(52))


def remove_cards(deck, cards):
    card_set = set(cards)
    return [c for c in deck if c not in card_set]


# Bitmask helpers for fast flush detection
def suit_bitmask(cards):
    """Return 4-element list of rank bitmasks per suit."""
    masks = [0, 0, 0, 0]
    for c in cards:
        masks[c % 4] |= 1 << (c // 4)
    return masks


def rank_bitmask(cards):
    """Return a single 13-bit mask of all ranks present."""
    m = 0
    for c in cards:
        m |= 1 << (c // 4)
    return m


# Precomputed straight masks (5 consecutive ranks, A-low included)
STRAIGHT_MASKS = []
for i in range(9):  # 0..8 -> 2-6 through T-A (ranks 0..4 up to 8..12)
    STRAIGHT_MASKS.append((0b11111 << i))
# Ace-low: A-2-3-4-5 -> ranks 12,0,1,2,3
STRAIGHT_MASKS.append((1 << 12) | 0b01111)
# Ace-high already covered by 8..12 (i=8)


def is_straight(rank_mask: int) -> int:
    """Return the high rank of the straight (0..12) or -1 if none."""
    for mask in reversed(STRAIGHT_MASKS):
        if (rank_mask & mask) == mask:
            # high card = highest set bit in mask
            # for ace-low mask, high is 3 (the 5)
            if mask == ((1 << 12) | 0b01111):
                return 3
            return (mask.bit_length() - 1)
    return -1


def combinations(iterable, r):
    """itertools.combinations wrapper (avoid import in hot paths optionally)."""
    from itertools import combinations as _c
    return list(_c(iterable, r))