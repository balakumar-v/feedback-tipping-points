import numpy as np, time
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
from p3ope.sharp import balanced_bounds
op.NL = 0.0; op.U_BOUNDED = True
rng = np.random.default_rng(606); T0 = time.time()
ALPHA, TAU_OLD, TN, n, R = 0.8, 1.0, 0.5, 6000, 12
pn_fn = lambda X: pi_new(X, TN)
print("moderate hidden confounder (bounded U). ZSB vs balanced bounds on V(new). Lambda = empirical sup odds ratio (so MSM holds).")
for beta, gamma in [(0.15, 0.5), (0.15, 1.5), (0.25, 1.5)]:
    V = truth(pn_fn, rng, gamma=gamma)
    res = []
    for r in range(R):
        L = sample_logs(n, rng, alpha=ALPHA, tau=TAU_OLD, beta=beta, gamma=gamma)
        pn = pn_fn(L["X"]); Q = fit_q(L["X"], L["a"], L["y"]); t = terms(L, pn, Q)
        lam = L["lam_true"]; snips = t["ipw"].sum()/t["w"].sum()
        # ZSB uses the stabilised estimator; balanced uses unstabilised. Compare each at the same Lambda.
        zl, zu = msm_bounds(t["pa"], L["y"], L["e"], lam)
        bl, bu = balanced_bounds(t["pa"], L["y"], L["e"], L["a"], Q, lam, K)
        res.append((lam, snips - V, zl, zu, bl, bu))
    a = np.array(res)
    print(f"beta={beta} gamma={gamma}: truth {V:.4f} | mean Lambda_true {a[:,0].mean():.2f} | nominal SNIPS bias {a[:,1].mean():+.4f}"
          f" | ZSB width {np.mean(a[:,3]-a[:,2]):.3f} cover {np.mean((a[:,2]<=V)&(V<=a[:,3])):.2f}"
          f" | balanced width {np.mean(a[:,5]-a[:,4]):.3f} cover {np.mean((a[:,4]<=V)&(V<=a[:,5])):.2f}")
print("elapsed", round(time.time()-T0,1))
