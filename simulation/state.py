"""Game state representation."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PlayerState:
    idx: int
    stack: float
    hole: list = field(default_factory=list)
    folded: bool = False
    allin: bool = False
    bet_this_round: float = 0.0
    total_bet: float = 0.0


@dataclass
class GameState:
    num_players: int
    stacks: List[float]
    players: List[PlayerState] = field(default_factory=list)
    board: List[int] = field(default_factory=list)
    pot: float = 0.0
    street: str = "preflop"  # preflop/flop/turn/river/showdown
    current_actor: int = 0
    dealer: int = 0
    small_blind: float = 0.5
    big_blind: float = 1.0
    min_raise: float = 0.0
    last_raise_size: float = 0.0
    acted: set = field(default_factory=set)
    rng_seed: Optional[int] = None

    def __post_init__(self):
        if not self.players:
            self.players = [PlayerState(i, self.stacks[i]) for i in range(self.num_players)]

    def active_players(self):
        return [p for p in self.players if not p.folded]

    def in_hand_players(self):
        return [p for p in self.players if not p.folded]

    def reset_round_bets(self):
        for p in self.players:
            p.bet_this_round = 0.0
        self.acted = set()
        self.min_raise = self.big_blind
        self.last_raise_size = 0.0