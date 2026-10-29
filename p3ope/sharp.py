"""Data-compatible (balancing-constrained) MSM bounds for multi-action policy value.
Variables v_i = 1/e*_i for each logged row, box [lo_i, hi_i].
ZSB: maximise / minimise  sum c_i y_i v_i / sum c_i v_i  (no further constraints)  -> msm_bounds in ope_pilot
Balanced (this file): add, for every action a and each g in {1, q_hat_a(x)}:
      sum_{i: a_i = a} g(x_i) v_i  =  sum_{i: a_i = a} g(x_i) / e_i      (the nominal weights satisfy it, so v=1/e is feasible)
and use the UNSTABILISED objective  (1/n) sum c_i y_i v_i  (denominator is pinned by the g=1 constraints).
Same idea as Dorn & Guo (2022) balancing constraints; valid (outer) bounds, not exactly sharp for K>2 actions or binary rewards.
"""
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


def balanced_bounds(c, y, e, a, Qhat, lam, K):
    n = len(y)
    lo = 1 + (1 / e - 1) / lam
    hi = 1 + lam * (1 / e - 1)
    rows, cols, vals, rhs = [], [], [], []
    r = 0
    for k in range(K):
        idx = np.where(a == k)[0]
        if len(idx) == 0:
            continue
        for g in (np.ones(len(idx)), Qhat[idx, k]):
            rows += [r] * len(idx); cols += list(idx); vals += list(g); rhs.append(float((g / e[idx]).sum())); r += 1
    A = csr_matrix((vals, (rows, cols)), shape=(r, n))
    obj = c * y / n
    out = []
    for sgn in (+1, -1):   # +1: maximise
        res = linprog(-sgn * obj, A_eq=A, b_eq=rhs, bounds=np.column_stack([lo, hi]), method="highs")
        out.append(sgn * -res.fun if res.status == 0 else np.nan)
    return out[1], out[0]   # (lower, upper)
