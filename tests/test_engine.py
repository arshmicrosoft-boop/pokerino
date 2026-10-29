from simulation.engine import Engine
from policies.tag import policy as tag_policy
from policies.calling_station import policy as cs_policy


def test_engine_runs_hand():
    eng = Engine(num_players=2, starting_stack=100.0, seed=42)
    state, result = eng.run_hand(tag_policy, cs_policy)
    assert state is not None
    assert len(result) >= 1


def test_engine_reproducible():
    eng1 = Engine(num_players=2, starting_stack=100.0, seed=7)
    s1, r1 = eng1.run_hand(tag_policy, cs_policy)
    eng2 = Engine(num_players=2, starting_stack=100.0, seed=7)
    s2, r2 = eng2.run_hand(tag_policy, cs_policy)
    # stacks should match
    assert s1.players[0].stack == s2.players[0].stack
    assert s1.players[1].stack == s2.players[1].stack


def test_engine_multiway():
    eng = Engine(num_players=3, starting_stack=100.0, seed=1)
    state, result = eng.run_hand(tag_policy, cs_policy)
    assert state is not None