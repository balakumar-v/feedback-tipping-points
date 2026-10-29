import numpy as np
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
op.NL = 0.0
rng = np.random.default_rng(404)
ALPHA, TAU_OLD, TN = 0.8, 1.0, 0.5
pn_fn = lambda X: pi_new(X, TN)
n = 20000
def breakdown(c, y, e, ybar, lam_grid):
    for lam in lam_grid:
        lo, hi = msm_bounds(c, y, e, lam)
        if lo - ybar <= 0: return lam
    return np.inf
grid = np.round(np.arange(1.0, 6.01, 0.05), 2)
for beta, gamma in [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.0, -1.0), (2.0, 1.5)]:
    V_new = truth(pn_fn, rng, gamma=gamma)
    V_old = truth(None, rng, gamma=gamma, beta=beta, alpha=ALPHA, tau=TAU_OLD, old=True)
    L = sample_logs(n, rng, alpha=ALPHA, tau=TAU_OLD, beta=beta, gamma=gamma)
    pn = pn_fn(L["X"]); t = terms(L, pn); est = estimates(t)
    ybar = L["y"].mean(); c = t["pa"]
    lam_t = L["lam_true"] if L["lam_true"] else 1.0
    lo1, hi1 = msm_bounds(c, L["y"], L["e"], 1.0)
    lo_t, hi_t = msm_bounds(c, L["y"], L["e"], lam_t)
    bd = breakdown(c, L["y"], L["e"], ybar, grid)
    print(f"beta={beta} gamma={gamma:+} | true V_new={V_new:.4f} true lift={V_new-V_old:+.4f} | SNIPS V={est['snips']:.4f} lift={est['snips']-ybar:+.4f} (bias {est['snips']-V_new:+.4f})"
          f" | check bounds@L=1 == SNIPS: {abs(lo1-est['snips'])<1e-9 and abs(hi1-est['snips'])<1e-9}"
          f" | empirical L_true={lam_t:.2f}: V_new bounds [{lo_t:.4f},{hi_t:.4f}] covers truth: {lo_t<=V_new<=hi_t} | breakdown L* for 'new beats old': {bd}")
