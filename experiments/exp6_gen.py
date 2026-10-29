"""Generate OPE tasks across four failure families with ground truth, record label-free diagnostics and failure labels."""
import numpy as np, time, csv, sys
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
from p3ope.khat import pareto_khat
op.U_BOUNDED = True
rng = np.random.default_rng(2027)
NT = int(sys.argv[1]); OUT = sys.argv[2]
truth_cache = {}
def V_true(nl, gamma, tn):
    key = (nl, gamma, tn)
    if key not in truth_cache:
        op.NL = nl
        truth_cache[key] = truth(lambda X: pi_new(X, tn), np.random.default_rng(99), gamma=gamma, m=1_000_000)
    return truth_cache[key]

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

def breakdown(c, y, e, ybar, cap=6.0):
    lo_l, hi_l = 1.0, cap
    if msm_bounds(c, y, e, cap)[0] - ybar > 0: return cap
    for _ in range(10):
        mid = 0.5 * (lo_l + hi_l)
        if msm_bounds(c, y, e, mid)[0] - ybar > 0: lo_l = mid
        else: hi_l = mid
    return 0.5 * (lo_l + hi_l)

fams = ["A_clean", "B_misspec", "C_conf", "D_loop"]
cols = None; f = open(OUT, "w", newline=""); wr = None; T0 = time.time()
for t in range(NT):
    fam = fams[t % 4]
    n = int(rng.choice([2000, 5000, 10000])); tn = float(rng.choice([0.25, 0.5, 1.0]))
    alpha = float(rng.uniform(0.5, 1.2)); tau = float(np.exp(rng.uniform(np.log(0.08), np.log(2.0))))
    nl = 0.8 if fam == "B_misspec" else 0.0
    beta, gamma = 0.0, 0.0
    if fam == "C_conf":
        beta, gamma = [(0.15, 1.0), (0.25, 1.5), (0.1, 0.5)][int(rng.integers(3))]
    op.NL = nl
    if fam == "D_loop":
        L1 = sample_logs(n, rng, alpha=alpha, tau=1.0)
        ms = fit_models(L1["X"], L1["a"], L1["y"]); tp = float(rng.choice([0.1, 0.2, 0.4]))
        X = rng.normal(size=(n, D))
        Qh = np.clip(predict(ms, X), 1e-4, 1 - 1e-4); P = softmax(np.log(Qh / (1 - Qh)) / tp, axis=1)
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        y = (rng.random(n) < expit(logits_r(X))[np.arange(n), a]).astype(float)
        L = dict(X=X, a=a, y=y, e=P[np.arange(n), a])
    else:
        L = sample_logs(n, rng, alpha=alpha, tau=tau, beta=beta, gamma=gamma)
    pn = pi_new(L["X"], tn); Q = fit_q(L["X"], L["a"], L["y"]); tt = terms(L, pn, Q); est = estimates(tt)
    V = V_true(nl, gamma, tn)
    B = 100
    lo_s, hi_s = boot_ci(tt["ipw"], rng, B, kind="ratio", w=tt["w"]); lo_d, hi_d = boot_ci(tt["dr"], rng, B)
    w = tt["w"]; ybar = L["y"].mean()
    row = dict(fam=fam, n=n, tau_old=tau, tau_new=tn, nl=nl, beta=beta, gamma=gamma, V=V,
               ipw=est["ipw"], snips=est["snips"], dm=est["dm"], dr=est["dr"],
               ci_lo_dr=lo_d, ci_hi_dr=hi_d, ci_lo_sn=lo_s, ci_hi_sn=hi_s,
               ess=ess(w) / n, maxw=w.max() / w.sum(), khat=pareto_khat(w), mean_w=w.mean(), cv_w=w.std() / w.mean(),
               gap_dr_sn=abs(est["dr"] - est["snips"]), gap_dr_dm=abs(est["dr"] - est["dm"]),
               ci_w=hi_d - lo_d, lam_star=breakdown(tt["pa"], L["y"], L["e"], ybar), lift_dr=est["dr"] - ybar)
    if wr is None: wr = csv.DictWriter(f, fieldnames=list(row.keys())); wr.writeheader()
    wr.writerow(row); f.flush()
    if t % 50 == 0: print(t, round(time.time() - T0), "s", flush=True)
print("done", round(time.time() - T0), flush=True)
