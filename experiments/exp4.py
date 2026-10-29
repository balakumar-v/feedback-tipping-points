import numpy as np, time
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
op.NL = 0.0
rng = np.random.default_rng(31); T0 = time.time()
n, ROUNDS, R, TAU_P = 5000, 7, 12, 0.15
cand = lambda X: pi_new(X, 0.5)
V = truth(cand, rng)
def fit_models(X, a, y):
    ms = []
    for k in range(K):
        m = a == k
        if m.sum() < 30 or y[m].min() == y[m].max(): ms.append(("c", y[m].mean() if m.sum() else y.mean())); continue
        ms.append(("lr", LogisticRegression(C=1.0, max_iter=200).fit(X[m], y[m])))
    return ms
def predict(ms, X):
    out = np.zeros((len(X), K))
    for k, (t, m) in enumerate(ms): out[:, k] = m if t == "c" else m.predict_proba(X)[:, 1]
    return out
res = np.zeros((ROUNDS, R, 4))
for r in range(R):
    # round 0: the original softmax logger
    Xc, ac, yc = [], [], []
    ms = None
    for t in range(ROUNDS):
        X = rng.normal(size=(n, D))
        if ms is None: P = pi_old_full(X, None, 0.8, 1.0)
        else:
            Qh = np.clip(predict(ms, X), 1e-4, 1-1e-4); P = softmax(np.log(Qh/(1-Qh))/TAU_P, axis=1)
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        y = (rng.random(n) < expit(logits_r(X))[np.arange(n), a]).astype(float)
        e = P[np.arange(n), a]
        L = dict(X=X, a=a, y=y, e=e)
        pn = cand(X); Q = fit_q(X, a, y); tt = terms(L, pn, Q); est = estimates(tt)
        res[t, r] = [ess(tt["w"])/n, est["snips"]-V, est["dr"]-V, np.sort(P, 1)[:, -1].mean()]
        Xc.append(X); ac.append(a); yc.append(y)
        ms = fit_models(np.vstack(Xc), np.concatenate(ac), np.concatenate(yc))
print("round | mean top-action prob of logger | ESS/n for fixed candidate | SNIPS rmse | DR rmse")
for t in range(ROUNDS):
    print(f"{t:5d} | {res[t,:,3].mean():.3f} | {res[t,:,0].mean():.3f} | {np.sqrt((res[t,:,1]**2).mean()):.4f} | {np.sqrt((res[t,:,2]**2).mean()):.4f}")
print("elapsed", round(time.time()-T0,1))
