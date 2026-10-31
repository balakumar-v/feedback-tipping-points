import numpy as np
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
op.NL = 0.8
rng = np.random.default_rng(78)
n, R, B, ALPHA = 5000, 100, 200, 0.8
pn_fn = lambda X: pi_new(X, 0.5)
print("MISSPECIFIED reward model (nonlinear truth, logistic-linear fit)")
for tau_old in [1.0, 0.25, 0.1]:
    V = truth(pn_fn, rng); rows = {m: [] for m in ["ipw","snips","dm","dr"]}; cov = {m: [] for m in ["ipw","snips","dr"]}
    for r in range(R):
        L = sample_logs(n, rng, alpha=ALPHA, tau=tau_old); pn = pn_fn(L["X"]); Q = fit_q(L["X"], L["a"], L["y"]); t = terms(L, pn, Q); est = estimates(t)
        for m in rows: rows[m].append(est[m])
        lo, hi = boot_ci(t["ipw"], rng, B); cov["ipw"].append(lo <= V <= hi)
        lo, hi = boot_ci(t["ipw"], rng, B, kind="ratio", w=t["w"]); cov["snips"].append(lo <= V <= hi)
        lo, hi = boot_ci(t["dr"], rng, B); cov["dr"].append(lo <= V <= hi)
    out = f"tau_old {tau_old:4.2f} | V={V:.4f} | "
    for m in rows:
        a = np.array(rows[m]); out += f"{m}: bias {a.mean()-V:+.4f} rmse {np.sqrt(((a-V)**2).mean()):.4f}" + (f" cov {np.mean(cov[m]):.2f}" if m in cov else "") + " | "
    print(out)
