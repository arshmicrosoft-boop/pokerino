"""Opponent model: VPIP, PFR, AF, 3-bet, fold-to-cbet, WTSD tracking."""

from dataclasses import dataclass, field


@dataclass
class OpponentModel:
    hands_seen: int = 0
    vpip_count: int = 0          # voluntarily put $ in pot
    pfr_count: int = 0           # preflop raise
    three_bet_count: int = 0
    three_bet_opps: int = 0
    fold_to_cbet_count: int = 0
    cbet_faced: int = 0
    wtsd_count: int = 0           # went to showdown
    showdowns: int = 0
    aggression_bets: int = 0
    aggression_calls: int = 0

    def observe_hand(self, vpip=False, pfr=False, three_bet=False, three_bet_opp=False,
                     fold_to_cbet=False, cbet_faced=False, wtsd=False, showdown=False,
                     bets=0, calls=0):
        self.hands_seen += 1
        if vpip:
            self.vpip_count += 1
        if pfr:
            self.pfr_count += 1
        if three_bet:
            self.three_bet_count += 1
        if three_bet_opp:
            self.three_bet_opps += 1
        if fold_to_cbet:
            self.fold_to_cbet_count += 1
        if cbet_faced:
            self.cbet_faced += 1
        if wtsd:
            self.wtsd_count += 1
        if showdown:
            self.showdowns += 1
        self.aggression_bets += bets
        self.aggression_calls += calls

    @property
    def vpip(self):
        return self.vpip_count / max(1, self.hands_seen)

    @property
    def pfr(self):
        return self.pfr_count / max(1, self.hands_seen)

    @property
    def three_bet_pct(self):
        return self.three_bet_count / max(1, self.three_bet_opps)

    @property
    def fold_to_cbet(self):
        return self.fold_to_cbet_count / max(1, self.cbet_faced)

    @property
    def wtsd(self):
        return self.wtsd_count / max(1, self.showdowns)

    @property
    def aggression_factor(self):
        if self.aggression_calls == 0:
            return float("inf") if self.aggression_bets > 0 else 0.0
        return self.aggression_bets / self.aggression_calls

    def confidence(self):
        """Sample-size confidence 0..1."""
        return min(1.0, self.hands_seen / 50.0)