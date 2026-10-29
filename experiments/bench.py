import numpy as np
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
rng = np.random.default_rng(9)
ALPHA, TAU_OLD = 0.8, 1.0
n = 20000
L = sample_logs(n, rng, alpha=ALPHA, tau=TAU_OLD)
X, a = L["X"], L["a"]
full = pi_old_full(X, None, ALPHA, TAU_OLD)[np.arange(n), a]
odds = lambda p: p/(1-p)
res = []
for j in range(D):
    red = np.zeros(n)
    for u, w in zip(GH_X, GH_W):
        Xj = X.copy(); Xj[:, j] = u
        red += w * pi_old_full(Xj, None, ALPHA, TAU_OLD)[np.arange(n), a]
    r = odds(full)/odds(red); lam_row = np.maximum(r, 1/r)
    res.append((j, lam_row.max(), np.quantile(lam_row, 0.99), np.quantile(lam_row, 0.5)))
    print(f"drop covariate {j}: implied Lambda  max {lam_row.max():.2f}  p99 {np.quantile(lam_row,.99):.2f}  median {np.quantile(lam_row,.5):.2f}")
# breakdown value for the same unconfounded logs, lift SNIPS vs mean(y), new policy tau 0.5
pn = pi_new(X, 0.5); t = terms(L, pn); ybar = L["y"].mean()
for lam in [1.05,1.1,1.15,1.2,1.3,1.4,1.5]:
    lo, hi = msm_bounds(t["pa"], L["y"], L["e"], lam); print(f"Lambda={lam}: V_new in [{lo:.4f},{hi:.4f}], lift lower bound {lo-ybar:+.4f}")
