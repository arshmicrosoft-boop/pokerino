"""Headless No-Limit Texas Hold'em game engine. Seeded RNG, reproducible."""

import random
from math_core.cards import full_deck, remove_cards, parse_cards
from math_core.hand_eval import evaluate_7
from simulation.state import GameState, PlayerState
from simulation.actions import FOLD, CHECK, CALL, RAISE, ALLIN
from simulation.rake import rake_amount


class Engine:
    def __init__(self, num_players=2, starting_stack=100.0, sb=0.5, bb=1.0,
                 rake_pct=0.05, rake_cap=None, seed=None):
        self.num_players = num_players
        self.starting_stack = starting_stack
        self.sb = sb
        self.bb = bb
        self.rake_pct = rake_pct
        self.rake_cap = rake_cap
        self.rng = random.Random(seed)
        self.seed = seed

    def new_hand(self, dealer=0):
        stacks = [self.starting_stack] * self.num_players
        state = GameState(
            num_players=self.num_players,
            stacks=stacks,
            dealer=dealer,
            small_blind=self.sb,
            big_blind=self.bb,
            rng_seed=self.seed,
        )
        # deal hole cards
        deck = full_deck()
        self.rng.shuffle(deck)
        for p in state.players:
            p.hole = [deck.pop(), deck.pop()]
        state._deck = deck
        # blinds
        sb_idx = (dealer + 1) % self.num_players
        bb_idx = (dealer + 2) % self.num_players
        self._post_blind(state, sb_idx, self.sb)
        self._post_blind(state, bb_idx, self.bb)
        state.current_actor = (bb_idx + 1) % self.num_players
        # if heads-up, dealer posts sb and acts first preflop
        if self.num_players == 2:
            state.current_actor = dealer  # dealer = sb in HU, acts first preflop
        state.street = "preflop"
        state.reset_round_bets()
        # set initial bets for blinds
        for p in state.players:
            pass
        # track blind bets in bet_this_round
        state.players[sb_idx].bet_this_round = self.sb
        state.players[bb_idx].bet_this_round = self.bb
        state.players[sb_idx].total_bet += self.sb
        state.players[bb_idx].total_bet += self.bb
        state.pot = self.sb + self.bb
        state.min_raise = self.bb
        state.last_raise_size = self.bb - self.sb if self.num_players > 2 else self.bb
        return state

    def _post_blind(self, state, idx, amount):
        p = state.players[idx]
        amt = min(amount, p.stack)
        p.stack -= amt
        p.total_bet += amt
        if p.stack <= 0:
            p.allin = True

    def legal_actions(self, state):
        p = state.players[state.current_actor]
        if p.folded or p.allin:
            return []
        # to call
        max_bet = max(x.bet_this_round for x in state.players)
        to_call = max_bet - p.bet_this_round
        actions = [FOLD]
        if to_call == 0:
            actions.append(CHECK)
        else:
            if p.stack >= to_call:
                actions.append(CALL)
        # raise
        if p.stack > to_call:
            actions.append(RAISE)
            actions.append(ALLIN)
        return actions

    def apply_action(self, state, action, raise_amount=None):
        p = state.players[state.current_actor]
        max_bet = max(x.bet_this_round for x in state.players)
        to_call = max_bet - p.bet_this_round

        if action == FOLD:
            p.folded = True
        elif action == CHECK:
            pass
        elif action == CALL:
            amt = min(to_call, p.stack)
            p.stack -= amt
            p.bet_this_round += amt
            p.total_bet += amt
            state.pot += amt
            if p.stack <= 1e-9:
                p.allin = True
        elif action == RAISE:
            if raise_amount is None:
                raise_amount = state.min_raise
            raise_amount = max(raise_amount, state.min_raise)
            total_needed = to_call + raise_amount
            total_needed = min(total_needed, p.stack)
            amt = total_needed
            p.stack -= amt
            p.bet_this_round += amt
            p.total_bet += amt
            state.pot += amt
            state.last_raise_size = raise_amount
            state.min_raise = raise_amount
            if p.stack <= 1e-9:
                p.allin = True
        elif action == ALLIN:
            amt = p.stack
            p.stack -= amt
            p.bet_this_round += amt
            p.total_bet += amt
            state.pot += amt
            if amt > to_call:
                state.last_raise_size = amt - to_call
                state.min_raise = state.last_raise_size
            if p.stack <= 1e-9:
                p.allin = True

        state.acted.add(state.current_actor)

        # advance actor
        self._advance(state)
        # check if betting round complete
        if self._round_complete(state):
            self._next_street(state)
        return state

    def _advance(self, state):
        n = self.num_players
        i = state.current_actor
        for _ in range(n):
            i = (i + 1) % n
            p = state.players[i]
            if not p.folded and not p.allin:
                state.current_actor = i
                return
        # all folded or allin
        state.current_actor = -1

    def _round_complete(self, state):
        active = [p for p in state.players if not p.folded and not p.allin]
        if not active:
            return True
        # all active have acted and bets equalized
        max_bet = max(p.bet_this_round for p in state.players if not p.folded)
        for p in active:
            if p.bet_this_round != max_bet:
                return False
            if p.idx not in state.acted:
                return False
        # also need at least one action? handled by acted set
        return True

    def _next_street(self, state):
        # reset round bets
        state.reset_round_bets()
        # deal board cards
        deck = state._deck
        if state.street == "preflop":
            # flop: 3 cards
            state.board.extend([deck.pop() for _ in range(3)])
            state.street = "flop"
        elif state.street == "flop":
            state.board.append(deck.pop())
            state.street = "turn"
        elif state.street == "turn":
            state.board.append(deck.pop())
            state.street = "river"
        elif state.street == "river":
            state.street = "showdown"
            return
        # set first actor for postflop: first active after dealer
        if self.num_players == 2:
            # heads-up: dealer (sb) acts first postflop
            first = state.dealer
        else:
            first = (state.dealer + 1) % self.num_players
        # find first non-folded non-allin
        i = first
        for _ in range(self.num_players):
            p = state.players[i]
            if not p.folded and not p.allin:
                state.current_actor = i
                return
            i = (i + 1) % self.num_players
        state.current_actor = -1

    def is_hand_over(self, state):
        active = [p for p in state.players if not p.folded]
        if len(active) <= 1:
            return True
        if state.street == "showdown":
            return True
        # all remaining are allin
        if all(p.allin or p.folded for p in state.players):
            return True
        return False

    def showdown(self, state):
        """Determine winners and payouts. Returns list of (player_idx, amount_won)."""
        active = [p for p in state.players if not p.folded]
        if len(active) == 1:
            w = active[0]
            # rake
            r = rake_amount(state.pot, self.rake_pct, self.rake_cap)
            w.stack += state.pot - r
            return [(w.idx, state.pot - r)]
        # evaluate hands
        best_score = None
        winners = []
        for p in active:
            score = evaluate_7(p.hole + state.board)
            if best_score is None or score > best_score:
                best_score = score
                winners = [p]
            elif score == best_score:
                winners.append(p)
        # split pot
        r = rake_amount(state.pot, self.rake_pct, self.rake_cap)
        net_pot = state.pot - r
        share = net_pot / len(winners)
        for w in winners:
            w.stack += share
        return [(w.idx, share) for w in winners]

    def run_hand(self, policy_fn, opponent_policy_fn=None):
        """Run a full hand. policy_fn(state, player_idx) -> (action, raise_amount).
        opponent_policy_fn same signature; if None, uses policy_fn for all."""
        import random as _r
        _r.seed(self.seed if self.seed is not None else 0)
        state = self.new_hand(dealer=0)
        if opponent_policy_fn is None:
            opponent_policy_fn = policy_fn
        safety = 0
        while not self.is_hand_over(state) and safety < 1000:
            safety += 1
            if state.current_actor == -1:
                # deal remaining streets
                while state.street not in ("showdown",) and not self.is_hand_over(state):
                    self._next_street(state)
                break
            idx = state.current_actor
            p = state.players[idx]
            if p.folded or p.allin:
                self._advance(state)
                if self._round_complete(state):
                    self._next_street(state)
                continue
            # choose policy
            if idx == 0:
                action, amt = policy_fn(state, idx)
            else:
                action, amt = opponent_policy_fn(state, idx)
            self.apply_action(state, action, amt)
        if not self.is_hand_over(state):
            # force showdown
            state.street = "showdown"
        result = self.showdown(state)
        return state, result