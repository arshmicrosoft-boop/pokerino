"""Rake calculation."""

def rake_amount(pot, rake_pct=0.05, rake_cap=None):
    r = pot * rake_pct
    if rake_cap is not None:
        r = min(r, rake_cap)
    return r


def net_pot(pot, rake_pct=0.05, rake_cap=None):
    return pot - rake_amount(pot, rake_pct, rake_cap)