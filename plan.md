# NLHE Mathematical Simulator & Benchmark Engine — Master Plan

> Simulation-only. Math-corrected. No RL. No Kelly in initial scope.
> All formulas below are the **corrected** versions from the mathematical audit.

---

## 0. Evolution of This Plan (Audit Trail)

1. **v1** — Original: math core + strategy + bankroll + simulation + RL/NN self-learning.
2. **User decision** — Dropped RL/NN. Kept math strategy + bankroll + simulation.
3. **Deep research added** — Sklansky, Chen/Ankenman, Harrington, Galfond, Polk, Miller, Thorp, Kelly, Nash, CFR, variance/Sharpe/RoR, implied odds, blockers, Morton's theorem, position, leaks.
4. **External mathematical audit applied** — corrected pot odds, semi-bluff EV, sample size, Kelly/RoR assumptions, GTO "floor" claim; restructured into 3 separated layers; removed misleading verification criteria; deferred Kelly/stop-loss.
5. **Brutal audit applied** — 8 fixes: hybrid exact/MC approach, opponent profile injection, adaptive MC sampling, multi-street implied odds, Dirichlet priors + smoothing, parallel multiway MC, rake in EV formula, seed-locked benchmarking with CI.
6. **Final additions** — rake, table selection, cold-start opponent handling, multiway EV, implied/reverse implied odds, simulation engine architecture, benchmarking methodology, implementation details, limitations, future extensions, deliverables, glossary.

---

## 1. Purpose & Scope

**Build a purely mathematical, reproducible, simulation-only engine** for no-limit Texas Hold'em that demonstrates — with evidence and confidence intervals — why one mathematical policy performs differently from another.

**In scope:** hand evaluation, combinatorics, probability, equity (exact + Monte Carlo), game-state simulation, opponent-behaviour experiments, statistical benchmarking.

**Out of scope (initial):** real-money play, site automation, Kelly bankroll sizing, stop-loss, self-learning/NN, tournament ICM (deferred to P7).

**Ethical stance:** Simulation and decision-support only. Automation execution deferred to a later, separate phase.

---

## 2. Three Quantities That Must Never Be Confused

| Quantity | Definition | Notes |
|---|---|---|
| **Equity** | Probability-weighted share of the pot | Property of a hand vs a range on a board |
| **EV** | Expected payoff of a decision | Property of an *action* in a state |
| **Realized profit** | What actually happened | Noisy; can be negative for a +EV strategy |

A +EV strategy can lose for a long time. A winning short sample proves nothing. These three are not interchangeable.

---

## 3. Corrected Mathematical Core

### 3.1 Pot Odds

Given pot $P$ before villain's bet $B$, your call costs $C = B$:

$$\text{threshold} = \frac{C}{P + B + C} = \frac{B}{P + 2B}$$

Call iff $\text{equity} > \text{threshold}$.

Sanity check: pot $40, bet $10 → threshold = 10/(40+20) = 16.67% (standard 5:1 → 1/6). ✓

### 3.2 Bluff Breakeven (zero equity when called)

$$F = \frac{R}{P + R}$$

$R$ = your risk (bet), $P$ = pot. Half-pot → 33.3%; pot → 50%; 2x pot → 66.7%.

### 3.3 Semi-Bluff EV

Model **all** outcomes and contributions explicitly: fold, call-and-hit, call-and-miss, raise. No simplified two-outcome form. (Earlier simplified formula was incorrect.)

### 3.4 Rule of 2 and 4

Approximation only ($\text{outs} \times 2\%$ per street). Use exact enumeration or Monte Carlo for actual evaluation.

### 3.5 SPR (Stack-to-Pot Ratio)

$$SPR = \frac{\text{effective stack}}{\text{pot}}$$

Cannot alone determine commitment. Combine with equity, range, board texture, position, and stack depth.

### 3.6 Combinatorics

- Pocket pair (AA): 6 combos
- Suited (AKs): 4 combos
- Offsuit (AKo): 12 combos
- Always recompute after removing known cards/blockers.

### 3.7 Equity (exact)

$$\text{Equity} = \frac{\sum_{h \in H}\sum_{v \in V} \text{win}(h,v,\text{board})}{|H|\cdot|V|}$$

Exact enumeration feasible heads-up (1326×1326). Multi-way → Monte Carlo.

**Hybrid approach (from audit):** Exact for preflop and simple endgame. Representative board sampling for flop (bucket by texture class). Monte Carlo for turn/river.

### 3.8 Monte Carlo Equity (adaptive sampling)

- Minimum $N = 10{,}000$ (floor), maximum $N = 200{,}000$ (cap).
- Adaptive $N$ based on: pot size relative to stack depth, number of opponents, street, current estimate variance.
- Convergence must be verified empirically, not assumed.
- For variance/RoR estimates, use $N \geq 100{,}000$.

### 3.9 Bayesian Range Updating

$$P(\text{hand} \mid \text{action}) \propto P(\text{action} \mid \text{hand}) \cdot P(\text{hand})$$

Engine of hand reading; narrows 1326 combos to ~50 by the river.

**Noise fix (from audit):** Use Dirichlet priors + Laplace smoothing. Never let one weird action wipe out a hand's probability. Sample size threshold ≥ 20 actions before updating. Confidence weighting: $\text{final} = w \cdot \text{posterior} + (1-w) \cdot \text{prior}$, where $w = \min(1, n/50)$.

### 3.10 Blockers

Your hole cards remove opponent outs. Basis of blocker-based bluffing.

### 3.11 Bluff-to-Value Ratio (polarized)

For sizing $s$ (fraction of pot): $\text{bluff}:\text{value} = s:1$. Half-pot → 1:2 (33% bluffs).

### 3.12 Polarized vs Merged Ranges

- Polarized: nuts + bluffs; checks medium. Maximizes fold equity + value.
- Merged (linear): continuous strength. Used vs. overcalling opponents.

### 3.13 Nash / GTO

- Nash equilibrium: no unilateral improvement possible.
- Minimax (von Neumann 1928): $\max_\sigma \min_\tau EV = \min_\tau \max_\sigma EV$.
- CFR (Zinkevich 2007): regret matching → Nash as $T \to \infty$.
- GTO strategies are range-based, not hand-specific. They account for indifference points where the opponent's calling/folding frequency makes bluffing vs. value betting equally profitable.

**Correction:** GTO is an *approximation baseline*, not a guarantee of unexploitability. An approximate GTO strategy is not necessarily unexploitable. Exploitative deviations are *testable hypotheses*, not guaranteed improvements — they can reduce performance if the opponent model is wrong.

### 3.14 Implied Odds & Reverse Implied Odds

**Implied Odds:**

$$\text{Implied Odds} = \frac{\text{Current Pot} + \text{Expected Future Bets}}{\text{Cost to Call}}$$

Crucial when pot odds alone say "fold," but you have strong implied odds (e.g., deep stacks with a drawing hand).

**Reverse Implied Odds (RIO):** The cost of losing more money when you do hit your hand but are still behind a better hand (e.g., hitting second-nuts on a paired board). Adjusts effective equity downward.

### 3.15 Variance, Sharpe Ratio, and Risk of Ruin (RoR)

- **Variance:** Measure of spread in outcomes. NLHE has high variance; short-term results deviate significantly from EV.
- **Sharpe Ratio:** $(\text{Mean Return} - \text{Risk-Free Rate}) / \text{Standard Deviation}$. Used to compare strategy efficiency across different stakes or formats.
- **Risk of Ruin (RoR):** Probability of losing the entire bankroll before reaching a target. Depends heavily on Buy-in size (in BBs) and Standard Deviation (BB/100 hands).

Note: Kelly Criterion is often cited for bet sizing, but Full Kelly is too volatile for human psychology. Fractional Kelly (e.g., 1/4 or 1/5) is standard for bankroll preservation.

### 3.16 Table Selection & Game Selection

- **Softness Metric:** Average Hand Played vs. Showdown ratio, Average Pot Size, Aggression Frequency (AF).
- **Leak Identification:** Identify opponents who fold too much to continuation bets (C-bet), call too wide (calling stations), or bluff too frequently (bluff-happy).
- **Adjustment:** Shift from GTO baseline to exploitative strategies against specific leak types.

### 3.17 Cold-Start Opponent Handling

- **Prior Distribution:** Start with a default population model (e.g., "tight-aggressive" default).
- **Bayesian Updating:** As each action is observed, update the opponent's range posterior probability (see D.9).
- **Sample Size Thresholds:** Do not trust small samples (< 20 actions) for major strategic shifts. Use confidence intervals to weigh new data against the prior.

### 3.18 Multiway Pot Dynamics

- **Equity Realization:** In multiway pots (3+ players), realized equity drops because there are more hands that can beat yours.
- **Pot Odds Improvement:** More callers mean better pot odds, encouraging speculative hands (small pairs, suited connectors) that have high implied odds but low direct equity.
- **Bluff Efficiency:** Bluffs become less effective as the number of opponents increases (probability that someone has a piece of the board rises).

### 3.19 Fundamental Theorem of Poker (Sklansky)

Every time you play your hand the way you would if you could see your opponents' cards, you gain; every time your opponents play differently from how they would if they could see your cards, you gain. The "error" of opponents is your profit — this is why exploitative play beats GTO against non-optimal humans.

### 3.20 Exploitation Level

$$\lambda^* = \frac{\delta F}{2C}$$

$\delta$ = leak magnitude, $F$ = frequency, $C$ = cost of being exploited back. Balances gain vs. risk.

### 3.21 Rake

Real cash games charge rake (typically 2.5–5%, capped). All EV calculations and benchmarks must subtract rake. A strategy's "edge" is only meaningful after rake. Table selection affects effective rake and opponent pool.

### 3.22 M and Q (tournaments)

- $M = \frac{\text{stack}}{\text{blinds + antes per orbit}}$ — orbits of survival. Primarily a tournament metric; in cash games M is effectively infinite.
- $Q = \frac{\text{stack}}{\text{average stack}}$ — relative position.

---

## 4. Architecture (3 Layers Separated)

```
poker_bot/
├── math_core/                  # Mathematical truth only — pure functions, no state, no RNG
│   ├── cards.py                # 52-card deck, hand representation (bitmask)
│   ├── hand_eval.py            # 7-card → rank 0..7461 (treys-backed)
│   ├── combinatorics.py        # Combos, blockers, range counting
│   ├── probability.py          # Pot/implied odds, fold equity, EV formulas (with rake)
│   └── equity.py               # Exact (preflop) + representative sampling (flop) + MC (turn/river)
├── simulation/                 # Game states, actions, payouts, seeded RNG
│   ├── engine.py               # Headless game engine (reproducible seeds, backward induction)
│   ├── state.py                # Game state representation
│   ├── actions.py              # Action definitions
│   └── rake.py                 # Rake calculation (configurable % + cap)
├── benchmark/                  # Compare fixed policies under identical conditions
│   ├── runner.py               # Seed-locked A/B runner across opponent populations
│   ├── metrics.py              # EV, bb/100, variance, CI, Sharpe, power analysis
│   └── reports.py              # Reproducible evidence output
├── policies/                   # Fixed mathematical policies (benchmark baselines)
│   ├── random.py
│   ├── calling_station.py
│   ├── tag.py                  # Tight-aggressive heuristic
│   └── pot_odds.py             # Pure pot-odds decision policy
├── opponent/                   # Opponent behaviour models (P6)
│   ├── model.py                # VPIP, PFR, AF, 3-bet, fold-to-cbet, WTSD
│   ├── profile.py              # Injectable profiles: GTO, calling_station, nit, bluff_happy, etc.
│   └── bayesian.py             # Dirichlet priors, smoothing, cold-start handling
├── tests/
└── main.py                     # CLI entrypoint
```

**Key principles:**
- `math_core` contains no strategy and no state. Pure functions only.
- `simulation` contains no math. Only game mechanics.
- `benchmark` compares policies. No strategy claims without CI.
- RNG is always seeded and passed in; reproducibility is mandatory.

---

## 5. Development Priorities

| Priority | Deliverable | Audit Fix |
|---|---|---|
| P0 | Card representation & hand evaluator | — |
| P1 | Exact equity calculator (preflop only) + MC engine (adaptive N) | Fix 1, Fix 3 |
| P2 | Range representation & combinatorics (with blockers) + Dirichlet priors | Fix 5 |
| P3 | Game-state simulator (seeded, reproducible, backward induction) | Fix 4 |
| P4 | Rake module + opponent profiles + multiway parallel MC | Fix 6, Fix 7 |
| P5 | Statistical benchmark framework (seed-locked, CI, multi-population) | Fix 2, Fix 8 |
| P6 | Opponent-behaviour experiments (cold-start handling) | Fix 5 |
| P7 | Tournament comparisons (ICM, push/fold, M/Q) | — |

---

## 6. Verification Criteria (corrected — no misleading win claims)

- Hand evaluator matches known hand-ranking examples (treys reference on 1,000 random 7-card samples).
- Exact equity matches exhaustive enumeration.
- Monte Carlo converges to exact within tolerance as $N \to \infty$ (empirically verified, not assumed).
- Confidence intervals computed and reported for all performance claims.
- Performance evaluated across **multiple opponent populations**, not a single baseline.
- Reproducibility across random seeds (same seed → identical results).
- **No claim of "winning 100,000 hands" as success.** Instead: demonstrate with reproducible evidence why one mathematical policy performs differently from another.
- Rake subtracted in all EV calculations.
- Power analysis provided for any sample-size claim.

---

## 7. Strategy Layer (deferred — built only after math core verified)

When built (post-P5), follows corrected math:
- GTO baseline as an **approximation**, not a guarantee. (Source from established solvers — PioSolver/GTO Wizard — as reference tables; custom CFR deferred unless needed.)
- Exploitative deviations as **testable hypotheses**, validated via benchmark before adoption.
- All claims backed by confidence intervals across opponent populations.
- Decision engine computes EV over narrowed opponent ranges and picks argmax; optional GTO-prior blending.

---

## 8. Tech Stack

- Python 3.11+
- `treys` (hand eval reference)
- `pokerkit` (later, for full game engine + ICM in P7)
- `numpy` (Monte Carlo vectorization)
- `pytest` (tests)
- `scipy` (confidence intervals, power analysis)

---

## 9. Game Format Roadmap

- **Cash games first** (infinite M, SPR-focused, rake-aware).
- SNG/MTT later (P7): add M/Q metrics, ICM, push/fold thresholds.

---

## 10. Simulation Engine Architecture

### 10.1 Core Components

- **Deck & Card Representation:** Bitmask or integer-based representation for speed.
- **Hand Evaluator:** Exact evaluation engine (e.g., Cactus Kev or similar optimized algorithm) returning rank/value.
- **Range Manager:** Stores distribution of hands for Player and Villain(s). Supports updating via Bayesian inference.
- **Board Generator:** Handles flop, turn, river generation with correct combinatorics (no replacement).
- **Action Tree Builder:** Constructs game tree based on current state (street, pot size, stack sizes).
- **EV Calculator:** Computes expected value for each legal action (Fold, Call, Raise, All-In) considering all possible future streets and opponent responses.
- **Monte Carlo Engine:** For multiway or complex range intersections, simulates $N$ random board runouts to estimate equity. Supports parallel processing.

### 10.2 Data Structures

- **State Object:** Contains current_pot, player_stacks, board_cards, player_range, opponent_range, last_action.
- **Action Node:** Represents a decision point with children nodes for each possible response.

### 10.3 Algorithm Flow

1. Initialize Hands/Ranges.
2. Deal Hole Cards.
3. Loop through Streets (Pre-flop → River):
   - a. Generate Board Cards.
   - b. Calculate Pot Odds/SPR for current street.
   - c. Evaluate Current Strategy (GTO or Exploitative).
   - d. Simulate Opponent Response (using updated range).
   - e. Execute Action, Update Pot/Stacks.
   - f. If Hand Ends: Calculate Realized Profit/Loss.
   - g. If Hand Continues: Update Ranges based on action taken.
4. Aggregate Results over $M$ simulated hands.

---

## 11. Benchmarking & Statistical Validation

### 11.1 Metrics to Track

- **EV per 100 Hands:** Net profit normalized for sample size.
- **Realized Win Rate (RR):** Actual money won/lost per 100 hands.
- **Standard Deviation (SD):** Volatility of results.
- **Sharpe Ratio:** Risk-adjusted return.
- **Max Drawdown:** Largest peak-to-trough decline in bankroll during simulation.
- **Time to Break Even:** Number of hands required to overcome initial variance with 95% confidence.

### 11.2 Comparison Methodology

- **Control Group:** Baseline strategy (e.g., Tight-Aggressive).
- **Test Group:** Modified strategy (e.g., Bluff-heavy, Loose-Aggressive).
- **Statistical Significance:** Use t-tests or confidence intervals to determine if differences in EV are statistically significant ($p < 0.05$) or due to variance.
- **A/B Testing:** Run identical board seeds for both strategies to isolate strategy impact from board luck. (Seed locking mandatory.)
- **Confidence Intervals:** Report 95% CI for all EV metrics. If CIs overlap, strategies are statistically identical.

### 11.3 Visualization

- **Equity Curves:** Plot cumulative EV and Realized Profit over time.
- **Distribution Histograms:** Show distribution of outcomes per 100 hands.
- **Heatmaps:** Show profitability by position, hand type, and board texture.

---

## 12. Implementation Details

### 12.1 Language Choice

- **Python:** Ideal for rapid prototyping, statistical libraries (NumPy, SciPy, Pandas), and readability.
- **C++/Rust:** For production-grade speed if simulating millions of hands per second.

### 12.2 Key Libraries

- `numpy`: Array operations, random number generation.
- `scipy`: Statistical tests, distributions.
- `pandas`: Data analysis, result aggregation.
- `matplotlib`/`seaborn`: Visualization.

### 12.3 Precision

- Use double-precision floating-point numbers.
- Handle rounding errors in probability calculations carefully (use epsilon comparisons).

---

## 13. Limitations & Caveats

### 13.1 Model Assumptions

- **Perfect Information:** Simulator knows exact ranges, but real-world players have hidden information.
- **Static Opponents:** Unless adaptive AI is built, opponents may not adjust to your strategy.
- **No Physical Tells:** Purely mathematical model ignores behavioral tells.

### 13.2 Computational Complexity

- Exact enumeration is feasible for Heads-Up but becomes intractable for 6-max/9-max without Monte Carlo approximation.
- Range updates can be computationally expensive if done naively; use efficient data structures (sparse matrices, bitsets).

### 13.3 Variance Clustering

- Short simulations may show skewed results due to clustering of bad beats. Ensure sufficient sample size ($> 100{,}000$ hands) for reliable benchmarks.

---

## 14. Future Extensions (Post-P7)

- **I.1 Tournament ICM Integration:** Adjust EV calculations based on payout structure and chip equity rather than just dollar equity.
- **I.2 Adaptive Opponent Modeling:** Implement machine learning models to predict opponent tendencies dynamically from live data.
- **I.3 Multi-Agent Simulation:** Simulate full tables with multiple distinct AI agents interacting simultaneously.
- **I.4 Real-Time Decision Support:** Integrate simulator output into a HUD (Heads-Up Display) for live play assistance.

---

## 15. Deliverables Checklist

- [ ] Core Hand Evaluator Module
- [ ] Range Manager with Bayesian Updates
- [ ] Monte Carlo Equity Engine
- [ ] Strategy Engine (GTO/Exploitative)
- [ ] Simulation Runner (Batch Processing)
- [ ] Statistical Analysis Module
- [ ] Visualization Dashboard
- [ ] Documentation & API Reference

---

## 16. Glossary

| Term | Definition |
|---|---|
| Aggression Factor (AF) | Ratio of bets/raises to calls |
| Blocker | A card in your hand that reduces the likelihood an opponent holds a specific strong hand |
| CFR | Counterfactual Regret Minimization |
| EV | Expected Value |
| GTO | Game Theory Optimal |
| ICM | Independent Chip Model (for tournaments) |
| NLHE | No-Limit Texas Hold'em |
| RoR | Risk of Ruin |
| SPR | Stack-to-Pot Ratio |
| Variance | Measure of spread in outcomes |

---

## 17. Pros / Cons / Solutions

| Aspect | Pros | Cons | Solution |
|---|---|---|---|
| Math-first approach | Grounded, testable, reproducible | Slower to show "results" | Accept; correctness > speed |
| Simulation-only | No legal/ethical risk; no ruin | No real-world edge validation | Calibrate opponent models against hand histories (P6) |
| Separated layers | Prevents conflating correctness with strategy claims | More files/modules | Worth it for clarity |
| Deferred Kelly/bankroll | Avoids premature optimization | No compounding demo initially | Add after math core verified |
| GTO as approximation | Honest, avoids overclaiming | Weaker "guarantee" | Frame as baseline + testable deviations |
| Monte Carlo equity | Fast, scalable | Sampling error | Convergence tests + CI |
| Exact enumeration | Ground truth | Expensive multiway | Use for heads-up; MC for multiway |
| Opponent models | Enable exploitation | Simplified vs real humans | Cold-start handling + hand-history calibration |

---

## 18. Remaining Caveats (honest limits)

- Simulated opponents are simplified; real human behavior is messier and context-dependent.
- GTO approximation quality depends on solver quality (use established solvers as reference).
- Implied/reverse-implied odds are estimates, not exact.
- No strategy is guaranteed to win in any finite sample (variance dominates short-term).
- Rake makes many "profitable" strategies actually losing in real games; table selection matters.
- Multiway pots require explicit EV, not heads-up shortcuts (Morton's theorem).

---

## 19. The Deliverable

Not a bot that "wins 100,000 hands." An engine that can demonstrate, with reproducible evidence, confidence intervals, and multi-population testing, **why** one mathematical policy performs differently from another — across hand evaluation, equity calculation, combinatorics, and simulated play. All math corrected, all claims hedged, all results reproducible.

---

## 20. Final Note on Execution Priority

- **Phase 1:** Build the Math Core (Evaluator, Combinatorics, Equity). Validate against known standards (e.g., PokerStove outputs).
- **Phase 2:** Build the Simulation Engine (Action Tree, Range Updates). Run basic Heads-Up scenarios.
- **Phase 3:** Implement Benchmarking & Statistics. Compare strategies rigorously.
- **Phase 4:** Refine with Advanced Concepts (Implied Odds, Blockers, Multiway).

---

## 21. Immediate Action Plan (Next 3 Steps)

### Step 1 — Build the "Truth" Engine First
- Write a brute-force evaluator that calculates exact equity for Heads-Up Preflop (AA vs AKs, etc.).
- Compare your Monte Carlo engine against this brute force result.
- Tune $N$ until error < 0.1%. This validates your core math.

### Step 2 — Implement One-Street Exploitation
- Create two opponents: `GTO_bot` and `calling_station`.
- Run your strategy against both.
- Verify that your strategy makes more money against the Calling Station than against GTO. If it doesn't, your exploitation logic is broken.

### Step 3 — Add Multi-Street Implied Odds
- Don't just simulate one street. Simulate the expected value of calling a draw by projecting future betting rounds.
- Use a simplified model first (e.g., assume you always hit your draw and win half the pot next street).

---

## 22. Next Step

Switch to **Build mode** and say **"Implement Phase 1"** (P0: card representation + hand evaluator) to begin. All work stays simulation-only until the math core is verified. All formulas above are the corrected versions — implement these, not any earlier drafts.

---

*Reference: https://notrack.ai/*