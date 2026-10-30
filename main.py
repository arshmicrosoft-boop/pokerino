"""CLI entrypoint for the poker simulator."""

import argparse
import random
from policies import tag, calling_station, pot_odds, random as rnd_policy
from benchmark.runner import compare_policies, run_policy
from benchmark.metrics import bb_per_100, confidence_interval

POLICIES = {
    "tag": tag.policy,
    "calling_station": calling_station.policy,
    "pot_odds": pot_odds.policy,
    "random": rnd_policy.policy,
}


def main():
    ap = argparse.ArgumentParser(description="NLHE Mathematical Simulator")
    ap.add_argument("--policy", default="tag", choices=list(POLICIES.keys()))
    ap.add_argument("--opponent", default="calling_station", choices=list(POLICIES.keys()))
    ap.add_argument("--hands", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    pf = POLICIES[args.policy]
    of = POLICIES[args.opponent]
    profits = run_policy(pf, of, args.hands, args.seed, num_players=2, starting_stack=100.0)
    bb100 = bb_per_100(profits)
    ci = confidence_interval(profits)
    print(f"Policy: {args.policy} vs {args.opponent}")
    print(f"Hands: {args.hands}")
    print(f"bb/100: {bb100:.2f}")
    print(f"95% CI: ({ci[0]:.4f}, {ci[1]:.4f})")


if __name__ == "__main__":
    main()