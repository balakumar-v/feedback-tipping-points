"""E1 MVP table: static OPE (IPW/SNIPS/DR/DM) vs naive before/after, with and without adverse covariate drift in the after period; 200 runs, n=20000."""
import numpy as np, time, json
from p3ope.ope_pilot import *
rng = np.random.default_rng(2026); T0 = time.time()
n, R, B, ALPHA, TN = 20000, 200, 200, 0.8, 1.0
pn_fn = lambda X: pi_new(X, TN)
V_old = truth(None, rng, alpha=ALPHA, old=True); V_new = truth(pn_fn, rng); lift = V_new - V_old
print(f"truth: V_old={V_old:.4f} V_new={V_new:.4f} true lift={lift:+.4f}")
res = {}
for drift in (0.0, 1.0):
    E = {k: [] for k in ["naive", "ipw", "snips", "dm", "dr"]}; cov = {k: [] for k in ["ipw", "snips", "dr"]}; ess_l = []; case = None
    for r in range(R):
        L = sample_logs(n, rng, alpha=ALPHA); X, y = L["X"], L["y"]; ybar = y.mean()
        Xa = rng.normal(size=(n, D)) + drift * DRIFT_DIR; aa = (pn_fn(Xa).cumsum(1) > rng.random((n, 1))).argmax(1)
        ya = (rng.random(n) < expit(logits_r(Xa))[np.arange(n), aa]).astype(float)
        Q = fit_q(X, L["a"], y); t = terms(L, pn_fn(X), Q); est = estimates(t)
        pt = dict(naive=ya.mean() - ybar, ipw=est["ipw"] - ybar, snips=est["snips"] - ybar, dm=est["dm"] - ybar, dr=est["dr"] - ybar)
        for k in E: E[k].append(pt[k])
        idx = rng.integers(0, n, size=(B, n)); yv = y[idx].mean(1)
        for k, s in (("ipw", t["ipw"][idx].mean(1)), ("snips", t["ipw"][idx].sum(1) / t["w"][idx].sum(1)), ("dr", t["dr"][idx].mean(1))):
            lo, hi = np.quantile(s - yv, [.025, .975]); cov[k].append(lo <= lift <= hi)
            if r == 0 and k in ("snips", "dr"): case = case or {}; case[k] = (pt[k], lo, hi)
        ess_l.append(ess(t["w"]) / n)
        if r == 0: case["naive"] = pt["naive"]
    print(f"\n== drift={drift}: ESS/n {np.mean(ess_l):.3f}; first-run case: naive {case['naive']:+.4f} | SNIPS {case['snips'][0]:+.4f} [{case['snips'][1]:+.4f},{case['snips'][2]:+.4f}] | DR {case['dr'][0]:+.4f} [{case['dr'][1]:+.4f},{case['dr'][2]:+.4f}]")
    print("method | mean lift | sd | rmse vs true lift | P(est<=0) | CI95 coverage of true lift")
    for k in E:
        a = np.array(E[k]); print(f"{k:6s} | {a.mean():+.4f} | {a.std():.4f} | {np.sqrt(((a-lift)**2).mean()):.4f} | {np.mean(a<=0):.3f} | " + (f"{np.mean(cov[k]):.2f}" if k in cov else "-"))
    res[drift] = {k: list(map(float, v)) for k, v in E.items()}
json.dump(dict(lift=lift, res=res), open("results/round-01/e1.json", "w"))
print("elapsed", round(time.time() - T0))
