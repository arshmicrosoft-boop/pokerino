"""Injectable opponent profiles for benchmarking."""

import random

PROFILES = {}


def register(name, fn):
    PROFILES[name] = fn


def get_profile(name):
    return PROFILES.get(name, PROFILES.get("random"))


def _random_policy(state, idx):
    import random
    legal = []  # caller passes legal? We'll just return fold/call
    # simple: fold 30%, call 50%, raise 20%
    r = random.random()
    if r < 0.3:
        return ("fold", None)
    if r < 0.8:
        return ("call", None)
    return ("raise", 1.0)


def _calling_station(state, idx):
    # never folds, calls everything, rarely raises
    r = random.random()
    if r < 0.05:
        return ("raise", 1.0)
    return ("call", None)


def _nit(state, idx):
    # folds a lot, only raises with strong
    r = random.random()
    if r < 0.7:
        return ("fold", None)
    if r < 0.9:
        return ("call", None)
    return ("raise", 2.0)


def _bluff_happy(state, idx):
    r = random.random()
    if r < 0.25:
        return ("raise", 1.5)
    if r < 0.5:
        return ("call", None)
    return ("fold", None)


def _tag(state, idx):
    # tight-aggressive: fold weak, raise strong, call medium
    r = random.random()
    if r < 0.55:
        return ("fold", None)
    if r < 0.75:
        return ("call", None)
    return ("raise", 1.5)


register("random", _random_policy)
register("calling_station", _calling_station)
register("nit", _nit)
register("bluff_happy", _bluff_happy)
register("tag", _tag)
register("gto", _tag)  # placeholder: tag as GTO approximation