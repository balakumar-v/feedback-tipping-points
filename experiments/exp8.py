import numpy as np, time, warnings
warnings.filterwarnings("ignore")
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
op.U_BOUNDED = True; op.NL = 0.0
rng = np.random.default_rng(909); T0 = time.time()
ALPHA, TAU_OLD, TN, NB, R = 0.8, 1.0, 0.5, 10000, 150
pn_fn = lambda X: pi_new(X, TN)

def slice_logs(n, rng, gamma):
    """randomised exploration slice: uniform actions, propensity 1/K, hidden U still affects reward"""
    X = rng.normal(size=(n, D)); U = draw_u(rng, n); a = rng.integers(0, K, n)
    y = (rng.random(n) < expit(logits_r(X, U, gamma))[np.arange(n), a]).astype(float)
    return dict(X=X, a=a, y=y, e=np.full(n, 1.0 / K))

print("hidden confounding in the bulk logs; small randomised exploration slice used to ground the estimate. 150 reps each.")
print("config | estimator: bias  rmse  cover95")
for m in [1.0, 2.0]:
    beta, gamma = 0.4 * m, 0.5 * m
    V = truth(pn_fn, rng, gamma=gamma)
    for ns in [300, 1000, 3000]:
        res = {k: [] for k in ["bulk_DR", "slice_IPW", "shrink", "test_then_pool"]}; cov = {k: [] for k in res}; om = []
        for r in range(R):
            B = sample_logs(NB, rng, alpha=ALPHA, tau=TAU_OLD, beta=beta, gamma=gamma)
            tb = terms(B, pn_fn(B["X"]), fit_q(B["X"], B["a"], B["y"])); xb = tb["dr"]; th_o = xb.mean(); s2o = xb.var(ddof=1) / NB
            S = slice_logs(ns, rng, gamma); ts = terms(S, pn_fn(S["X"]), None); xs = ts["ipw"]; th_e = xs.mean(); s2e = xs.var(ddof=1) / ns
            b2 = max(0.0, (th_e - th_o) ** 2 - s2e - s2o); w = (s2o + b2) / (s2e + s2o + b2); th_sh = th_o + w * (th_e - th_o)
            z = abs(th_e - th_o) / np.sqrt(s2e + s2o); th_pool = (th_e * (1 / s2e) + th_o * (1 / s2o)) / (1 / s2e + 1 / s2o) if z < 1.96 else th_e
            se_sh = np.sqrt(w ** 2 * s2e + (1 - w) ** 2 * s2o + (1 - w) ** 2 * b2)   # includes estimated bias
            se_pool = np.sqrt(1 / (1 / s2e + 1 / s2o)) if z < 1.96 else np.sqrt(s2e)
            for k, (est, se) in {"bulk_DR": (th_o, np.sqrt(s2o)), "slice_IPW": (th_e, np.sqrt(s2e)), "shrink": (th_sh, se_sh), "test_then_pool": (th_pool, se_pool)}.items():
                res[k].append(est - V); cov[k].append(abs(est - V) <= 1.96 * se)
            om.append(w)
        s = f"m={m} slice n={ns:4d} (mean w on slice {np.mean(om):.2f}) |"
        for k in res:
            e = np.array(res[k]); s += f" {k}: {e.mean():+.4f} {np.sqrt((e**2).mean()):.4f} {np.mean(cov[k]):.2f} |"
        print(s, flush=True)
print("elapsed", round(time.time() - T0, 1))
