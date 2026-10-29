import numpy as np, time
from p3ope.ope_pilot import *
rng = np.random.default_rng(2026); T0=time.time()
n, R, ALPHA, TN = 20000, 200, 0.8, 1.0
pn_fn = lambda X: pi_new(X, TN)
V_old = truth(None, rng, alpha=ALPHA, old=True); V_new = truth(pn_fn, rng); lift = V_new - V_old
print(f"truth P0: V_old={V_old:.4f} V_new={V_new:.4f} true lift={lift:+.4f}")
for drift in [0.0, 1.0]:
    V_new_P1 = truth(pn_fn, rng, drift=drift)
    naive, sn, dr = [], [], []
    for r in range(R):
        before = sample_logs(n, rng, alpha=ALPHA)
        Xa = rng.normal(size=(n, D)) + drift*DRIFT_DIR
        Pa = pn_fn(Xa); aa = (Pa.cumsum(1) > rng.random((n,1))).argmax(1)
        ya = (rng.random(n) < expit(logits_r(Xa))[np.arange(n), aa]).astype(float)
        naive.append(ya.mean() - before["y"].mean())
        Q = fit_q(before["X"], before["a"], before["y"])
        est = estimates(terms(before, pn_fn(before["X"]), Q))
        sn.append(est["snips"] - before["y"].mean()); dr.append(est["dr"] - before["y"].mean())
    f = lambda v: (np.mean(v), np.std(v), np.mean(np.array(v) <= 0))
    print(f"drift={drift}: E[naive Δ]={V_new_P1-V_old:+.4f} | naive mean %+.4f sd %.4f P(Δ<=0) %.2f | SNIPS %+.4f sd %.4f P(Δ<=0) %.2f | DR %+.4f sd %.4f P(Δ<=0) %.2f" % (*f(naive), *f(sn), *f(dr)))
print("elapsed", round(time.time()-T0,1))
