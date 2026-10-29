import numpy as np, time
from p3ope.ope_pilot import *
rng = np.random.default_rng(77); T0=time.time()
n, R, B, ALPHA = 5000, 100, 200, 0.8
pn_fn = lambda X: pi_new(X, 0.5)
print("tau_old | ESS/n | max-w share | method: bias  RMSE  cov95(bootstrap)  [cov95 normal-approx]")
for tau_old in [2.0, 1.0, 0.5, 0.25, 0.1]:
    V = truth(pn_fn, rng)
    rows = {m: [] for m in ["ipw","snips","dm","dr"]}
    cov_b = {m: [] for m in ["ipw","snips","dr"]}; cov_n = {m: [] for m in ["ipw","snips","dr"]}
    es, mx = [], []
    for r in range(R):
        L = sample_logs(n, rng, alpha=ALPHA, tau=tau_old)
        pn = pn_fn(L["X"]); Q = fit_q(L["X"], L["a"], L["y"]); t = terms(L, pn, Q)
        est = estimates(t)
        for m in rows: rows[m].append(est[m])
        es.append(ess(t["w"])/n); mx.append(t["w"].max()/t["w"].sum())
        lo, hi = boot_ci(t["ipw"], rng, B); cov_b["ipw"].append(lo <= V <= hi)
        lo, hi = boot_ci(t["ipw"], rng, B, kind="ratio", w=t["w"]); cov_b["snips"].append(lo <= V <= hi)
        lo, hi = boot_ci(t["dr"], rng, B); cov_b["dr"].append(lo <= V <= hi)
        for m in ["ipw","dr"]:
            v = t[m]; se = v.std(ddof=1)/np.sqrt(n); cov_n[m].append(abs(v.mean()-V) <= 1.96*se)
        # delta-method SE for SNIPS
        w, yv = t["w"], L["y"]; s = est["snips"]; se = np.sqrt(np.sum((w*(yv-s))**2))/w.sum(); cov_n["snips"].append(abs(s-V) <= 1.96*se)
    out = f"{tau_old:5.2f} | {np.mean(es):.3f} | {np.mean(mx):.4f} | "
    for m in ["ipw","snips","dm","dr"]:
        a = np.array(rows[m]); b = a.mean()-V; rm = np.sqrt(((a-V)**2).mean())
        c = f" cov {np.mean(cov_b[m]):.2f} [{np.mean(cov_n[m]):.2f}]" if m in cov_b else ""
        out += f"{m}: {b:+.4f} {rm:.4f}{c} | "
    print(out)
print("truth V(new) example:", round(V,4), "elapsed", round(time.time()-T0,1))
