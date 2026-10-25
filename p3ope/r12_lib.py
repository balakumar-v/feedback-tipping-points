"""R12: free-form count-curve model (fifth shape). logit(click) = base(context, item) + f(c) + round term; f free on bins c=1..6, >=7."""
import numpy as np
from scipy.special import expit
from scipy import sparse
from p3ope import r2_lib as R
from p3ope import exp13_lib as L
from p3ope.exp13_lib import K, D, T_OBS, T_EVAL
J = 7

def design_ff(X0, A, C, trend=True):
    T, n = A.shape; base = R.design(X0, A, np.zeros_like(C), False)[:, :K * D + K]
    c = np.minimum(C.reshape(-1).astype(int), J); Dm = np.zeros((T * n, J)); idx = np.where(c >= 1)[0]; Dm[idx, c[idx] - 1] = 1.0
    cols = [base, Dm]
    if trend: cols.append(np.repeat(np.arange(T, dtype=float), n)[:, None])
    return np.hstack(cols)

def fit_ff(d, trend=True, w=None, b0=None, iters=10):
    Xd = design_ff(d["X0"], d["A"], d["G"]["lin"], trend); y = d["Y"].reshape(-1); ww = np.ones(len(y)) if w is None else w
    Xs = sparse.csr_matrix(Xd); return R.newton_fast(Xs, y, ww, b0, iters), Xs, y

def rollout_ff(Pc, base, cv, tr, ua, ur, T):
    n = Pc.shape[0]; st = R.St(n); ii = np.arange(n); out = np.empty(T)
    for t in range(T):
        a = (Pc > ua[t][:, None]).argmax(1); c = np.minimum(st.cnt[ii, a].astype(int), J)
        out[t] = (ur[t] < expit(base[ii, a] + cv[c] + tr[t])).mean(); st.step(a)
    return out

def forecast_ff(b, beta, obs_old, H=T_EVAL):
    f = R.pop(beta); Wf = b[:K * D].reshape(K, D); bf = b[K * D:K * D + K]; coef = b[K * D + K:K * D + K + J]; th = b[K * D + K + J]
    cv = np.concatenate([[0.0], coef]); t = np.arange(T_EVAL, dtype=float); tr = th * np.minimum(t, T_OBS - 1); base = f["X0"] @ Wf.T + bf
    pn = rollout_ff(f["Pn"], base, cv, tr, f["ua"], f["ur"], T_EVAL); po = rollout_ff(f["Po"], base, cv, tr, f["ua"], f["ur"], T_EVAL)
    delta = float((obs_old - po[:T_OBS]).mean()); return float((pn - po)[:H].mean() - delta)
