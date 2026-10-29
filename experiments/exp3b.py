import numpy as np
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
op.NL = 0.0; op.U_BOUNDED = True
rng = np.random.default_rng(505)
ALPHA, TAU_OLD, TN, n, R = 0.8, 1.0, 0.5, 20000, 40
pn_fn = lambda X: pi_new(X, TN)
print("bounded hidden confounder: does the MSM interval at the true Lambda contain the truth, and is it informative?")
for beta, gamma in [(0.3, 0.5), (0.5, 1.0), (0.8, 1.5)]:
    V_new = truth(pn_fn, rng, gamma=gamma)
    V_old = truth(None, rng, gamma=gamma, beta=beta, alpha=ALPHA, tau=TAU_OLD, old=True)
    cov, wid, bias, lams, bds = [], [], [], [], []
    for r in range(R):
        L = sample_logs(n, rng, alpha=ALPHA, tau=TAU_OLD, beta=beta, gamma=gamma)
        t = terms(L, pn_fn(L["X"]), None); s_ = t["ipw"].sum()/t["w"].sum(); ybar = L["y"].mean()
        lam = L["lam_true"]; lo, hi = msm_bounds(t["pa"], L["y"], L["e"], lam)
        cov.append(lo <= V_new <= hi); wid.append(hi-lo); bias.append(s_-V_new); lams.append(lam)
        bd = np.inf
        for l in np.round(np.arange(1.0, 3.01, 0.02), 2):
            if msm_bounds(t["pa"], L["y"], L["e"], l)[0] - ybar <= 0: bd = l; break
        bds.append(bd)
    print(f"beta={beta} gamma={gamma}: true lift {V_new-V_old:+.4f} | nominal SNIPS bias {np.mean(bias):+.4f} | mean sup-Lambda {np.mean(lams):.2f} | bound@Lambda_true covers truth {np.mean(cov):.2f}, mean width {np.mean(wid):.3f} | median breakdown L* {np.median(bds):.2f}")
