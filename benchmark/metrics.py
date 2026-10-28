"""Metrics: EV, bb/100, variance, CI, Sharpe, power analysis."""

import numpy as np
from scipy import stats


def bb_per_100(profits, bb=1.0):
    arr = np.array(profits, dtype=float)
    if len(arr) == 0:
        return 0.0
    return float(np.mean(arr) / bb * 100.0)


def std_dev(profits):
    arr = np.array(profits, dtype=float)
    if len(arr) < 2:
        return 0.0
    return float(np.std(arr, ddof=1))


def confidence_interval(profits, confidence=0.95):
    arr = np.array(profits, dtype=float)
    n = len(arr)
    if n < 2:
        return (0.0, 0.0)
    m = np.mean(arr)
    se = stats.sem(arr)
    h = se * stats.t.ppf((1 + confidence) / 2.0, n - 1)
    return (float(m - h), float(m + h))


def sharpe(profits, risk_free=0.0):
    arr = np.array(profits, dtype=float)
    if len(arr) < 2:
        return 0.0
    sd = np.std(arr, ddof=1)
    if sd == 0:
        return 0.0
    return float((np.mean(arr) - risk_free) / sd)


def max_drawdown(cumulative):
    arr = np.array(cumulative, dtype=float)
    if len(arr) == 0:
        return 0.0
    peak = arr[0]
    mdd = 0.0
    for v in arr:
        if v > peak:
            peak = v
        dd = peak - v
        if dd > mdd:
            mdd = dd
    return float(mdd)


def power_analysis(effect_size, alpha=0.05, power=0.8):
    """Approximate required sample size (per group) for two-sample t-test."""
    from scipy.stats import norm
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
    return int(np.ceil(n))