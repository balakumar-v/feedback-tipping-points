"""R2 library: shapes (lin/log/mem7 fit; sat/convex/decay/window truths), generic round trend, last-only slice, slice kappa estimators (pooled, random-intercept, within-pair FE).
Same world as exp13_lib (K=10, D=5, T_OBS=6, T_EVAL=10)."""
import numpy as np
from scipy.special import expit
from p3ope import exp13_lib as L
from p3ope.exp13_lib import K, D, W, B0, logits_r, pi_old_full, pi_old_nominal, pi_new, T_OBS, T_EVAL, TN, ALPHA, TAU_OLD, RIDGE, newton
from scipy import sparse

RHO = 0.7


class St:
    def __init__(s, n):
        s.n = n; s.ii = np.arange(n); s.cnt = np.zeros((n, K)); s.m5 = np.zeros((n, K)); s.m7 = np.zeros((n, K)); s.l1 = np.full(n, -1); s.l2 = np.full(n, -1)

    def feat(s, kind, a):
        ii = s.ii
        if kind == "lin": return s.cnt[ii, a]
        if kind == "log": return np.log1p(s.cnt[ii, a])
        if kind == "mem7": return s.m7[ii, a]
        if kind == "sat": c = s.cnt[ii, a]; return 1.5 * c / (1 + 0.5 * c)
        if kind == "convex": c = s.cnt[ii, a]; return c * (1 + 0.25 * np.maximum(c - 1, 0))
        if kind == "quad": c = s.cnt[ii, a]; return c * c
        if kind == "kink": c = s.cnt[ii, a]; return np.maximum(c - 2, 0)
        if kind == "tail2": c = s.cnt[ii, a]; return c + np.maximum(c - 2, 0)
        if kind == "decay": return s.m5[ii, a]
        if kind == "window": return (s.l1 == a).astype(float) + (s.l2 == a)
        raise ValueError(kind)

    def step(s, a):
        ii = s.ii; s.cnt[ii, a] += 1; s.m5 *= 0.5; s.m5[ii, a] += 1; s.m7 *= RHO; s.m7[ii, a] += 1; s.l2 = s.l1; s.l1 = a.copy()


def rollout(Pc, base, kind, kappa, tr, ua, ur, T):
    n = Pc.shape[0]; st = St(n); ii = np.arange(n); out = np.empty(T)
    for t in range(T):
        a = (Pc > ua[t][:, None]).argmax(1)
        z = base[ii, a] - kappa * st.feat(kind, a) + tr[t]
        out[t] = (ur[t] < expit(z)).mean(); st.step(a)
    return out


def true_paths(kind, kappa, delta, beta, gamma, n=60000, seed=7):
    r = np.random.default_rng(seed); X0 = r.normal(size=(n, D)); U = r.normal(size=n)
    base = logits_r(X0, U, gamma); Pn = pi_new(X0, TN).cumsum(1); Po = pi_old_full(X0, U, ALPHA, TAU_OLD, beta).cumsum(1)
    ua, ur = L.draws(n, T_EVAL, seed + 1); tr = -delta * np.arange(T_EVAL)
    return rollout(Pn, base, kind, kappa, tr, ua, ur, T_EVAL), rollout(Po, base, kind, kappa, tr, ua, ur, T_EVAL)


def true_lift(kind, kappa, delta, beta, gamma, H=T_EVAL, **kw):
    pn, po = true_paths(kind, kappa, delta, beta, gamma, **kw); return float((pn - po)[:H].mean())


def simulate(n, rng, kind, kappa, delta, beta, gamma, mode="old", T=T_OBS):
    """mode: old | slice (uniform every impression) | lastslice (old policy rounds 0..T-2, uniform at T-1). Returns dict with X0, A, Y, G{lin,log,mem7}, e (round-0 nominal propensity)."""
    X0 = rng.normal(size=(n, D)); U = rng.normal(size=n); base = logits_r(X0, U, gamma)
    Pold = pi_old_full(X0, U, ALPHA, TAU_OLD, beta); Punif = np.full((n, K), 1.0 / K)
    st = St(n); ii = np.arange(n); A = np.zeros((T, n), int); Y = np.zeros((T, n)); G = {s: np.zeros((T, n)) for s in ("lin", "log", "mem7", "tail2")}
    for t in range(T):
        P = Punif if (mode == "slice" or (mode == "lastslice" and t == T - 1)) else Pold
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        z = base[ii, a] - kappa * st.feat(kind, a) - delta * t
        y = (rng.random(n) < expit(z)).astype(float)
        A[t], Y[t] = a, y
        for s in G: G[s][t] = st.feat(s, a)
        st.step(a)
    e = np.full(n, 1.0 / K) if mode == "slice" else pi_old_nominal(X0, ALPHA, TAU_OLD, beta)[ii, A[0]]
    return dict(X0=X0, A=A, Y=Y, G=G, e=e, n=n, T=T)


def design(X0, A, g, trend=False):
    T, n = A.shape; R = T * n; P = K * D + K + 1 + (1 if trend else 0)
    Xd = np.zeros((R, P)); rows = np.arange(R); af = A.reshape(-1); Xf = np.tile(X0, (T, 1))
    for j in range(D): Xd[rows, af * D + j] = Xf[:, j]
    Xd[rows, K * D + af] = 1.0; Xd[:, K * D + K] = g.reshape(-1)
    if trend: Xd[:, K * D + K + 1] = np.repeat(np.arange(T, dtype=float), n)
    return Xd


def newton_fast(Xs, y, w, b0=None, iters=8):
    """same as exp13_lib.newton but with a sparse CSR design (identical maths, ~10x faster)."""
    P = Xs.shape[1]; b = np.zeros(P) if b0 is None else b0.copy(); I = RIDGE * np.eye(P); XsT = Xs.T.tocsr()
    for _ in range(iters):
        p = expit(Xs @ b); g = XsT @ (w * (p - y)) + RIDGE * b
        H = (XsT.multiply((w * p * (1 - p))[None, :]) @ Xs).toarray() + I
        b = b - np.linalg.solve(H, g)
    return b


def fit(d, shape, trend=False, w=None, b0=None, iters=10):
    Xd = design(d["X0"], d["A"], d["G"][shape], trend); y = d["Y"].reshape(-1)
    ww = np.ones(len(y)) if w is None else w
    Xs = sparse.csr_matrix(Xd)
    return newton_fast(Xs, y, ww, b0, iters), Xs, y


def kappa_of(b): return -b[K * D + K]


# ---------------- forecast ----------------
NF = 5000
_FP = {}


def pop(beta):
    if beta not in _FP:
        r = np.random.default_rng(31337); X0 = r.normal(size=(NF, D)); ua, ur = L.draws(NF, T_EVAL, 4242)
        _FP[beta] = dict(X0=X0, Pn=pi_new(X0, TN).cumsum(1), Po=pi_old_nominal(X0, ALPHA, TAU_OLD, beta).cumsum(1), ua=ua, ur=ur)
    return _FP[beta]


def forecast(b, shape, trend, tmode, beta, obs_old, H=T_EVAL):
    """returns (forecast lift over first H rounds, calibration-adjusted). trend: model has round term; tmode flat|lin extrapolation of round term beyond the last observed round."""
    f = pop(beta); Wf = b[:K * D].reshape(K, D); bf = b[K * D:K * D + K]; kap = -b[K * D + K]
    th = b[K * D + K + 1] if trend else 0.0
    t = np.arange(T_EVAL, dtype=float); te = np.minimum(t, T_OBS - 1) if tmode == "flat" else t
    tr = th * te; base = f["X0"] @ Wf.T + bf
    pn = rollout(f["Pn"], base, shape, kap, tr, f["ua"], f["ur"], T_EVAL); po = rollout(f["Po"], base, shape, kap, tr, f["ua"], f["ur"], T_EVAL)
    delta = float((obs_old - po[:T_OBS]).mean())
    return float((pn - po)[:H].mean() - delta)


def snips0(d, WU=None):
    """round-0 SNIPS lift (new minus observed old mean) and bootstrap draws (user weights WU (B,n))."""
    n = d["n"]; a0 = d["A"][0]; y0 = d["Y"][0]; w = pi_new(d["X0"], TN)[np.arange(n), a0] / d["e"]
    pt = (w * y0).sum() / w.sum() - y0.mean()
    if WU is None: return pt, None
    return pt, (WU @ (w * y0)) / (WU @ w) - (WU @ y0) / WU.sum(1)


# ---------------- slice kappa estimators ----------------
def newton_ri(Xd, y, T, n, sigma2=1.0, iters=10):
    """pooled logit + user random intercept (penalised, variance sigma2) via Schur complement. Returns b."""
    P = Xd.shape[1]; b = np.zeros(P); u = np.zeros(n); X3 = Xd.reshape(T, n, P); y2 = y.reshape(T, n)
    for _ in range(iters):
        eta = (Xd @ b).reshape(T, n) + u[None, :]; p = expit(eta); w = p * (1 - p)
        gb = Xd.T @ (p - y2).reshape(-1) + RIDGE * b; gu = (p - y2).sum(0) + u / sigma2
        Hbb = (Xd * w.reshape(-1)[:, None]).T @ Xd + RIDGE * np.eye(P)
        Hbu = np.einsum("tn,tnp->np", w, X3); Huu = w.sum(0) + 1.0 / sigma2
        S = Hbb - np.einsum("np,nq,n->pq", Hbu, Hbu, 1.0 / Huu); rhs = gb - (Hbu * (gu / Huu)[:, None]).sum(0)
        db = np.linalg.solve(S, rhs); du = (gu - Hbu @ db) / Huu
        b -= db; u -= du
    return b


def fe_kappa(A, Y):
    """within-(user,item) first-vs-second exposure conditional contrast: kappa1 = log(n10/n01). Returns (kappa1, se, n_discordant)."""
    n10 = n01 = 0
    for k in range(K):
        M = A == k; cs = M.cumsum(0); f = M & (cs == 1); s = M & (cs == 2); has = s.any(0)
        yf = (Y * f).sum(0); ys = (Y * s).sum(0)
        n10 += int(np.sum(has & (yf == 1) & (ys == 0))); n01 += int(np.sum(has & (yf == 0) & (ys == 1)))
    return float(np.log((n10 + 0.5) / (n01 + 0.5))), float(np.sqrt(1.0 / (n10 + 0.5) + 1.0 / (n01 + 0.5))), n10 + n01
