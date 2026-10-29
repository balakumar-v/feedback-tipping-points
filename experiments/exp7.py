import numpy as np, time, warnings
warnings.filterwarnings("ignore")
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
from sklearn.linear_model import LogisticRegression
op.U_BOUNDED = True; op.NL = 0.0
rng = np.random.default_rng(808); T0 = time.time()
ALPHA, TAU_OLD, TN = 0.8, 1.0, 0.5
pn_fn = lambda X: pi_new(X, TN)

def propensity_odds_shift(X, a, j):
    full = LogisticRegression(max_iter=300).fit(X, a); red = LogisticRegression(max_iter=300).fit(np.delete(X, j, 1), a)
    pf = full.predict_proba(X)[np.arange(len(a)), a]; pr = red.predict_proba(np.delete(X, j, 1))[np.arange(len(a)), a]
    pf, pr = np.clip(pf, 1e-6, 1-1e-6), np.clip(pr, 1e-6, 1-1e-6)
    r = (pf/(1-pf)) / (pr/(1-pr)); return np.maximum(r, 1/r)

print("PART 1: do omitted-covariate benchmarked Lambdas give sensitivity intervals that contain the truth? (n=10000, 30 logs per row)")
print("hidden strength m x (beta=0.4, gamma=0.5) ~ 'as strong as a typical observed covariate' at m=1")
for m in [0.0, 0.5, 1.0, 2.0]:
    beta, gamma = 0.4*m, 0.5*m
    V = truth(pn_fn, rng, gamma=gamma)
    rows = []
    for r in range(30):
        L = sample_logs(10000, rng, alpha=ALPHA, tau=TAU_OLD, beta=beta, gamma=gamma)
        t = terms(L, pn_fn(L["X"]), None); snips = t["ipw"].sum()/t["w"].sum()
        lam_j = np.array([propensity_odds_shift(L["X"], L["a"], j) for j in range(D)])   # D x n
        rec = [snips - V]
        for q in (0.5, 0.9, 0.99):
            lam_b = max(1.0, np.quantile(lam_j, q, axis=1).max())
            lo, hi = msm_bounds(t["pa"], L["y"], L["e"], lam_b)
            rec += [lam_b, lo <= V <= hi, hi - lo]
        rows.append(rec)
    a = np.array(rows, float)
    s = f"m={m}: nominal SNIPS bias {a[:,0].mean():+.4f} (|bias| {np.abs(a[:,0]).mean():.4f}) |"
    for i, q in enumerate((0.5, 0.9, 0.99)):
        s += f" q={q}: Lambda_b {a[:,1+3*i].mean():.2f} cover {a[:,2+3*i].mean():.2f} width {a[:,3+3*i].mean():.3f} |"
    print(s, flush=True)

print("\nPART 2: closed-loop logs (logger retrained on its own data, sharp). Simple fixes vs plain DR. 200 tasks, n=5000.")
def fit_models(X, a, y):
    ms = []
    for k in range(K):
        mk = a == k
        if mk.sum() < 30 or y[mk].min() == y[mk].max(): ms.append(("c", y[mk].mean() if mk.sum() else y.mean())); continue
        ms.append(("lr", LogisticRegression(C=1.0, max_iter=200).fit(X[mk], y[mk])))
    return ms
def predict(ms, X):
    out = np.zeros((len(X), K))
    for k, (tt, mm) in enumerate(ms): out[:, k] = mm if tt == "c" else mm.predict_proba(X)[:, 1]
    return out
V = truth(pn_fn, rng)
names = ["snips","dm","dr","dr_clip10","dr_clip50","dr_os1","dr_os10","dr_os100","switch(ESS<.1->DM else DR)"]
err = {k: [] for k in names}; essl = []
for r in range(200):
    n = 5000
    L1 = sample_logs(n, rng, alpha=ALPHA, tau=1.0); ms = fit_models(L1["X"], L1["a"], L1["y"]); tp = float(rng.choice([0.1, 0.2, 0.4]))
    X = rng.normal(size=(n, D)); Qh = np.clip(predict(ms, X), 1e-4, 1-1e-4); P = softmax(np.log(Qh/(1-Qh))/tp, axis=1)
    a = (P.cumsum(1) > rng.random((n, 1))).argmax(1); y = (rng.random(n) < expit(logits_r(X))[np.arange(n), a]).astype(float)
    L = dict(X=X, a=a, y=y, e=P[np.arange(n), a])
    pn = pn_fn(X); Q = fit_q(X, a, y); t = terms(L, pn, Q); w = t["w"]; dm = t["dm"]; qa = Q[np.arange(n), a]
    est = dict(snips=t["ipw"].sum()/w.sum(), dm=dm.mean(), dr=t["dr"].mean(),
               dr_clip10=(dm + np.minimum(w, 10)*(y-qa)).mean(), dr_clip50=(dm + np.minimum(w, 50)*(y-qa)).mean())
    for lam in (1, 10, 100): est[f"dr_os{lam}"] = (dm + (lam*w/(w**2+lam))*(y-qa)).mean()
    ess_n = ess(w)/n; est["switch(ESS<.1->DM else DR)"] = est["dm"] if ess_n < 0.1 else est["dr"]
    for k in names: err[k].append(est[k]-V)
    essl.append(ess_n)
print(f"mean ESS/n {np.mean(essl):.3f}; truth {V:.4f}")
for k in names:
    e = np.array(err[k]); print(f"{k:28s} bias {e.mean():+.4f} rmse {np.sqrt((e**2).mean()):.4f}")
print("elapsed", round(time.time()-T0,1))
