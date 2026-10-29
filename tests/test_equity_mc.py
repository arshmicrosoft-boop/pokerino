from math_core.equity import exact_equity_heads_up, monte_carlo_equity


def test_mc_converges_to_exact():
    aa = [12*4+0, 12*4+1]
    kk = [11*4+0, 11*4+1]
    exact = exact_equity_heads_up(aa, kk)
    mc = monte_carlo_equity(aa, kk, n_samples=50000, seed=1)
    assert abs(mc - exact) < 0.01, f"mc={mc} exact={exact}"