"""E3/E4 library: multi-mechanism feedback simulator, fast weighted logistic fit, user bootstrap, forecast, tipping point, verdict.
World = exp12 world (ope_pilot K=10, D=5). Reward logit = base(x0,a) + gamma*U*C_a + mechanism adjustment.
Mechanisms: lin (-kappa*count), sat, decay (recency-weighted memory), window (last 2 rounds), convex (exploratory), drift (taste moves toward shown items), none.
"""
import numpy as np
from scipy.special import expit, softmax
from p3ope import ope_pilot as op
from p3ope.ope_pilot import K, D, W, B0, logits_r, pi_old_full, pi_old_nominal, pi_new
op.NL = 0.0
import os
ALPHA, TAU_OLD, TN = float(os.environ.get('P3_ALPHA', 0.8)), float(os.environ.get('P3_TAUOLD', 1.0)), float(os.environ.get('P3_TN', 0.5))
T_OBS, T_EVAL = 6, 10
RIDGE = 0.1          # = 1/C with C=10 (as exp12 sklearn fit)
NP = K * D + K + 1   # params: per-action slopes, per-action intercepts, count coefficient (= -kappa)


# ---------------- mechanisms ----------------
class State:
    def __init__(self, n):
        self.n = n; self.cnt = np.zeros((n, K)); self.mem = np.zeros((n, K)); self.l1 = np.full(n, -1); self.l2 = np.full(n, -1); self.S = np.zeros((n, D))


def adj(kind, kappa, eta, st, a):
    ii = np.arange(st.n)
    if kind == "none": return np.zeros(st.n)
    if kind == "lin": return -kappa * st.cnt[ii, a]
    if kind == "sat": c = st.cnt[ii, a]; return -kappa * 1.5 * c / (1 + 0.5 * c)
    if kind == "convex": c = st.cnt[ii, a]; return -kappa * c * (1 + 0.25 * np.maximum(c - 1, 0))
    if kind == "decay": return -kappa * st.mem[ii, a]
    if kind == "window": return -kappa * ((st.l1 == a).astype(float) + (st.l2 == a))
    if kind == "drift": return -kappa * st.cnt[ii, a] + np.einsum("nd,nd->n", st.S, W[a])
    raise ValueError(kind)


def update(kind, eta, st, a):
    ii = np.arange(st.n)
    st.cnt[ii, a] += 1; st.mem *= 0.5; st.mem[ii, a] += 1; st.l2 = st.l1; st.l1 = a.copy()
    if kind == "drift": st.S += eta * W[a]


def rollout(Pc, base, kind, kappa, eta, ua, ur, T):
    """Per-round mean reward. Pc: cumulative action probs (n,K); base: (n,K) logits; ua, ur: (T,n) uniforms."""
    n = Pc.shape[0]; st = State(n); ii = np.arange(n); out = np.empty(T)
    for t in range(T):
        a = (Pc > ua[t][:, None]).argmax(1)
        z = base[ii, a] + adj(kind, kappa, eta, st, a)
        out[t] = (ur[t] < expit(z)).mean(); update(kind, eta, st, a)
    return out


def draws(n, T, seed):
    r = np.random.default_rng(seed); return r.random((T, n)), r.random((T, n))


# ---------------- truth ----------------
def true_paths(kind, kappa, eta, beta, gamma, n=60000, seed=7, Pold_fn=None):
    r = np.random.default_rng(seed); X0 = r.normal(size=(n, D)); U = r.normal(size=n)
    base = logits_r(X0, U, gamma)
    Pn = pi_new(X0, TN).cumsum(1)
    Po = (pi_old_full(X0, U, ALPHA, TAU_OLD, beta) if Pold_fn is None else Pold_fn(X0)).cumsum(1)
    ua, ur = draws(n, T_EVAL, seed + 1)
    return rollout(Pn, base, kind, kappa, eta, ua, ur, T_EVAL), rollout(Po, base, kind, kappa, eta, ua, ur, T_EVAL)


def true_lift(kind, kappa, eta, beta, gamma, **kw):
    pn, po = true_paths(kind, kappa, eta, beta, gamma, **kw); return float((pn - po).mean()), float(pn[0] - po[0])


# ---------------- data simulation ----------------
def design(X0, a, c):
    """X0 (n,D); a, c (T,n) -> design rows ordered round-major, (T*n, NP)."""
    T, n = a.shape; R = T * n
    Xd = np.zeros((R, NP)); rows = np.arange(R); af = a.reshape(-1); Xf = np.tile(X0, (T, 1))
    for j in range(D): Xd[rows, af * D + j] = Xf[:, j]
    Xd[rows, K * D + af] = 1.0; Xd[:, -1] = c.reshape(-1)
    return Xd


def fit_models(X, a, y):
    from sklearn.linear_model import LogisticRegression
    ms = []
    for k in range(K):
        m = a == k
        if m.sum() < 30 or y[m].min() == y[m].max(): ms.append(("c", y[m].mean() if m.sum() else y.mean())); continue
        ms.append(("lr", LogisticRegression(C=1.0, max_iter=200).fit(X[m], y[m])))
    return ms


def predict_models(ms, X):
    out = np.zeros((len(X), K))
    for k, (t, m) in enumerate(ms): out[:, k] = m if t == "c" else m.predict_proba(X)[:, 1]
    return out


TAU_RETRAIN = 0.3


def simulate_obs(n, rng, kind, kappa, eta, beta, gamma, mode="old", T=T_OBS):
    """mode: old (logger softmax, sees U if beta), slice (uniform random exposure), retrain (logger refit on its own logs at rounds 2 and 4).
    Returns dict: X0, a (T,n), c (T,n) prior same-item count, y (T,n), e (n,) nominal propensity of round-0 action, pnew0, final_logger (callable or None)."""
    X0 = rng.normal(size=(n, D)); U = rng.normal(size=n); base = logits_r(X0, U, gamma)
    if mode == "old": P = pi_old_full(X0, U, ALPHA, TAU_OLD, beta)
    elif mode == "slice": P = np.full((n, K), 1.0 / K)
    elif mode == "retrain": P = pi_old_full(X0, None, ALPHA, TAU_OLD, 0.0)
    P0 = P.copy(); st = State(n); ii = np.arange(n)
    A = np.zeros((T, n), int); C = np.zeros((T, n)); Y = np.zeros((T, n)); final = None
    for t in range(T):
        if mode == "retrain" and t in (2, 4):
            ms = fit_models(np.tile(X0, (t, 1)), A[:t].reshape(-1), Y[:t].reshape(-1))
            Qh = np.clip(predict_models(ms, X0), 1e-4, 1 - 1e-4); P = softmax(np.log(Qh / (1 - Qh)) / TAU_RETRAIN, axis=1); final = ms
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        c = st.cnt[ii, a].copy(); z = base[ii, a] + adj(kind, kappa, eta, st, a)
        y = (rng.random(n) < expit(z)).astype(float)
        A[t], C[t], Y[t] = a, c, y; update(kind, eta, st, a)
    if mode == "old": e = pi_old_nominal(X0, ALPHA, TAU_OLD, beta)[ii, A[0]]
    elif mode == "slice": e = np.full(n, 1.0 / K)
    else: e = P0[ii, A[0]]
    return dict(X0=X0, a=A, c=C, y=Y, e=e, n=n, final=final)


def retrain_logger_fn(ms):
    def f(X):
        Qh = np.clip(predict_models(ms, X), 1e-4, 1 - 1e-4); return softmax(np.log(Qh / (1 - Qh)) / TAU_RETRAIN, axis=1)
    return f


# ---------------- fitting ----------------
def newton(X, y, w, b0=None, iters=8):
    b = np.zeros(X.shape[1]) if b0 is None else b0.copy(); I = RIDGE * np.eye(X.shape[1])
    for _ in range(iters):
        p = expit(X @ b); g = X.T @ (w * (p - y)) + RIDGE * b
        H = (X * (w * p * (1 - p))[:, None]).T @ X + I
        b = b - np.linalg.solve(H, g)
    return b


def fit_full(d):
    Xd = design(d["X0"], d["a"], d["c"]); y = d["y"].reshape(-1); w = np.ones(len(y))
    return newton(Xd, y, w, None, 10), Xd, y


def unpack(b): return b[:K * D].reshape(K, D), b[K * D:K * D + K], -b[-1]


def boot_kappa(Xd, y, b0, n, T, B, rng, iters=3):
    """User-level Poisson bootstrap; returns kappa_b (B,) and user weights (B,n)."""
    kb = np.empty(B); WU = rng.poisson(1.0, size=(B, n)).astype(float)
    for i in range(B):
        w = np.tile(WU[i], T); b = newton(Xd, y, w, b0, iters); kb[i] = -b[-1]
    return kb, WU


def sandwich_se_kappa(Xd, y, b, n, T):
    p = expit(Xd @ b); r = (y - p)[:, None] * Xd
    s = r.reshape(T, n, -1).sum(0) - RIDGE * b[None, :] / n
    H = (Xd * (p * (1 - p))[:, None]).T @ Xd + RIDGE * np.eye(len(b)); Hi = np.linalg.inv(H)
    V = Hi @ (s.T @ s) @ Hi
    return float(np.sqrt(V[-1, -1]))


# ---------------- forecast ----------------
NF = 20000
_FC = {}


def forecast_pop(beta):
    if beta not in _FC:
        r = np.random.default_rng(31337); X0 = r.normal(size=(NF, D))
        ua, ur = draws(NF, T_EVAL, 4242)
        _FC[beta] = dict(X0=X0, Pn=pi_new(X0, TN).cumsum(1), Po=pi_old_nominal(X0, ALPHA, TAU_OLD, beta).cumsum(1), ua=ua, ur=ur)
    return _FC[beta]


def fc_paths(Wf, bf, kappa, beta, Pold_cum=None, kind="lin"):
    f = forecast_pop(beta); base = f["X0"] @ Wf.T + bf; Po = f["Po"] if Pold_cum is None else Pold_cum
    return (rollout(f["Pn"], base, kind, kappa, 0.0, f["ua"], f["ur"], T_EVAL), rollout(Po, base, kind, kappa, 0.0, f["ua"], f["ur"], T_EVAL))


def calib_delta(Wf, bf, kappa, beta, obs_old):
    """observed old-policy per-round reward minus model-predicted, averaged over observed rounds."""
    _, po = fc_paths(Wf, bf, kappa, beta); return float((obs_old - po[:T_OBS]).mean())


def forecast_lift(Wf, bf, kappa, beta, delta):
    pn, po = fc_paths(Wf, bf, kappa, beta); return float((pn - po).mean() - delta)


def tipping_kappa(Wf, bf, beta, delta, hi=3.0, iters=11):
    f0 = forecast_lift(Wf, bf, 0.0, beta, delta)
    if f0 <= 0: return 0.0
    if forecast_lift(Wf, bf, hi, beta, delta) > 0: return np.inf
    lo, h = 0.0, hi
    for _ in range(iters):
        m = 0.5 * (lo + h)
        if forecast_lift(Wf, bf, m, beta, delta) > 0: lo = m
        else: h = m
    return 0.5 * (lo + h)


def true_tipping(beta, gamma, hi=3.0, iters=11):
    f = lambda k: true_lift("lin", k, 0.0, beta, gamma, n=60000)[0]
    if f(0.0) <= 0: return 0.0
    if f(hi) > 0: return np.inf
    lo, h = 0.0, hi
    for _ in range(iters):
        m = 0.5 * (lo + h)
        if f(m) > 0: lo = m
        else: h = m
    return 0.5 * (lo + h)


# ---------------- verdicts ----------------
def verdict(s_lo, s_hi, k_lo, k_hi, kstar):
    if s_hi <= 0 or k_lo > kstar: return "REJECT"
    if s_lo > 0 and k_hi < kstar: return "APPROVE"
    return "NEED_DATA"


def one_step_verdict(s_lo): return "APPROVE" if s_lo > 0 else "REJECT"


def static_snips(d, beta, WU=None):
    """round-0 SNIPS lift (new minus observed old mean reward) and bootstrap draws."""
    X0 = d["X0"]; n = d["n"]; a0 = d["a"][0]; y0 = d["y"][0]; w = pi_new(X0, TN)[np.arange(n), a0] / d["e"]
    pt = (w * y0).sum() / w.sum() - y0.mean()
    if WU is None: return pt, None
    num = WU @ (w * y0); den = WU @ w; ybar = (WU @ y0) / WU.sum(1)
    return pt, num / den - ybar
