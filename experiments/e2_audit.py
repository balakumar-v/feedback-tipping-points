"""E2 static audit across the overlap dial: separate findings per overlap level, false-approval/false-reject of CI rules vs naive before/after (favourable/adverse drift)."""
import sys, time, json, numpy as np, warnings
warnings.filterwarnings("ignore")
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
op.NL = 0.0
rng = np.random.default_rng(2718); T0 = time.time()
N, R, B, ALPHA = 5000, int(sys.argv[1]) if len(sys.argv) > 1 else 40, 150, 0.8
CANDS = [(s, tc) for s in (0.0, 0.3, 0.6, 0.85, 1.0) for tc in (0.5, 1.0)]
def cand_fn(s, tc): return lambda X: softmax((s * logits_r(X) + (1 - s) * (X @ W_STALE.T)) / tc, axis=1)
rows = []
for tau_old in (2.0, 1.0, 0.5, 0.25, 0.1):
    V_old = truth(None, rng, alpha=ALPHA, tau=tau_old, old=True)
    for (s, tc) in CANDS:
        fn = cand_fn(s, tc); V = truth(fn, rng); true_lift = V - V_old
        V_fav = truth(fn, rng, drift=-1.0); V_adv = truth(fn, rng, drift=+1.0)   # after-deployment value under context drift
        for r in range(R):
            L = sample_logs(N, rng, alpha=ALPHA, tau=tau_old); X, yb = L["X"], L["y"]; ybar = yb.mean()
            pn = fn(X); Q = fit_q(X, L["a"], yb); t = terms(L, pn, Q); est = estimates(t); w = t["w"]
            idx = rng.integers(0, N, size=(B, N)); ipwv, dr_v, wv, yv = t["ipw"][idx], t["dr"][idx], w[idx], yb[idx]
            lift_b = {"ipw": ipwv.mean(1) - yv.mean(1), "snips": ipwv.sum(1) / wv.sum(1) - yv.mean(1), "dr": dr_v.mean(1) - yv.mean(1)}
            lo = {k: np.quantile(v, .025) for k, v in lift_b.items()}; hi = {k: np.quantile(v, .975) for k, v in lift_b.items()}
            pt = {"ipw": est["ipw"] - ybar, "snips": est["snips"] - ybar, "dr": est["dr"] - ybar}
            rec = dict(tau_old=tau_old, s=s, tc=tc, true_lift=true_lift, ess=ess(w) / N, maxw=w.max() / w.sum(), gap=abs(est["dr"] - est["snips"]) / max(hi["dr"] - lo["dr"], 1e-9))
            for k in pt: rec[f"{k}_app"] = int(lo[k] > 0); rec[f"{k}_cov"] = int(lo[k] <= true_lift <= hi[k]); rec[f"{k}_err"] = pt[k] - true_lift
            for nm, Vd in (("fav", V_fav), ("adv", V_adv)):   # naive before/after: candidate deployed to drifted population
                Xa = rng.normal(size=(N, D)) + (-1.0 if nm == "fav" else 1.0) * DRIFT_DIR
                aa = (fn(Xa).cumsum(1) > rng.random((N, 1))).argmax(1); ya = (rng.random(N) < expit(logits_r(Xa))[np.arange(N), aa]).astype(float)
                d = ya.mean() - ybar; se = np.sqrt(ya.var(ddof=1) / N + yb.var(ddof=1) / N)
                rec[f"naive_{nm}_app"] = int(d - 1.96 * se > 0); rec[f"naive_{nm}_delta"] = d
            rows.append(rec)
    print("tau_old", tau_old, "done", round(time.time() - T0), flush=True)
json.dump(rows, open("results/round-01/e2_rows.json", "w"), default=float)
