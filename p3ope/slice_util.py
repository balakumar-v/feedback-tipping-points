import numpy as np
from scipy.special import expit
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
def slice_logs(n, rng, gamma):
    """randomised exploration slice: uniform actions, propensity 1/K, hidden U still affects reward"""
    X = rng.normal(size=(n, D)); U = draw_u(rng, n); a = rng.integers(0, K, n)
    y = (rng.random(n) < expit(logits_r(X, U, gamma))[np.arange(n), a]).astype(float)
    return dict(X=X, a=a, y=y, e=np.full(n, 1.0 / K))

