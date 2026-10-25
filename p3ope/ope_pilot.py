"""
Pilot for Perceptron Hackathon Problem 3 (off-policy evaluation).
numpy/scipy/sklearn only. Python 3.12 OK.

World: K actions, d-dim context, Bernoulli reward with logistic link.
Old policy (logger): softmax over a weakened copy of the true logits, optionally
also reacting to a hidden variable U that is NOT in the logs.
New policy (candidate): sharper softmax over the true logits (no access to U).
Ground truth is computed exactly by Monte Carlo over contexts and U.
"""
import numpy as np
from scipy.special import expit, softmax
from sklearn.linear_model import LogisticRegression

K, D = 10, 5
W = np.random.default_rng(0).normal(size=(K, D)) * 0.5
B0 = np.random.default_rng(1).normal(size=K) * 0.3 - 2.5
C = np.where(np.arange(K) % 2 == 0, 1.0, -1.0)      # how each action loads on hidden U
DRIFT_DIR = -W.mean(0) / np.linalg.norm(W.mean(0))  # drift direction that lowers the average logit across actions

W_STALE = np.random.default_rng(5).normal(size=(K, D)) * 0.5   # a stale/misaligned scoring model
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(41)  # quadrature for U ~ N(0,1)
GH_W = GH_W / GH_W.sum()
U_BOUNDED = False                      # True: U ~ Uniform(-sqrt3, sqrt3) (unit variance, bounded odds ratios)
_LN, _LW = np.polynomial.legendre.leggauss(41)
LG_X, LG_W = _LN * np.sqrt(3), _LW / _LW.sum()


def draw_u(rng, n):
    return rng.uniform(-np.sqrt(3), np.sqrt(3), n) if U_BOUNDED else rng.normal(size=n)


NL = 0.0   # strength of a nonlinear reward term that the logistic-linear reward model cannot represent
CN = np.random.default_rng(2).choice([-1.0, 1.0], size=K)


def logits_r(X, U=None, gamma=0.0):
    z = X @ W.T + B0
    if NL:
        z = z + NL * (np.sin(2.0 * X[:, [0]]) + X[:, [1]] ** 2 - 1.0) * CN[None, :]
    if U is not None and gamma:
        z = z + gamma * U[:, None] * C[None, :]
    return z


def pi_old_full(X, U=None, alpha=0.5, tau=1.0, beta=0.0, mix=0.0):
    z = alpha * (X @ W.T + B0) + mix * (X @ W_STALE.T)
    if U is not None and beta:
        z = z + beta * U[:, None] * C[None, :]
    return softmax(z / tau, axis=1)


def pi_old_nominal(X, alpha=0.5, tau=1.0, beta=0.0, mix=0.0):
    """Propensity the practitioner can compute: U marginalised out."""
    if not beta:
        return pi_old_full(X, None, alpha, tau, 0.0, mix)
    out = np.zeros((len(X), K))
    nodes, wts = (LG_X, LG_W) if U_BOUNDED else (GH_X, GH_W)
    for u, w in zip(nodes, wts):
        out += w * pi_old_full(X, np.full(len(X), u), alpha, tau, beta, mix)
    return out


def pi_new(X, tau=0.25):
    return softmax(logits_r(X) / tau, axis=1)


def sample_logs(n, rng, alpha=0.5, tau=1.0, beta=0.0, gamma=0.0, drift=0.0, mix=0.0):
    X = rng.normal(size=(n, D)) + drift * DRIFT_DIR
    U = rng.normal(size=n)
    P = pi_old_full(X, U, alpha, tau, beta, mix)
    a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
    p_true = expit(logits_r(X, U, gamma))[np.arange(n), a]
    y = (rng.random(n) < p_true).astype(float)
    e_nom = pi_old_nominal(X, alpha, tau, beta, mix)[np.arange(n), a]   # logged propensity
    lam = None
    if beta:
        e_full = P[np.arange(n), a]
        odds = lambda p: p / (1 - p)
        r = odds(e_full) / odds(e_nom)
        lam = float(max(r.max(), 1 / r.min()))
    return dict(X=X, a=a, y=y, e=e_nom, lam_true=lam)


def truth(policy, rng, gamma=0.0, beta=0.0, alpha=0.5, tau=1.0, drift=0.0, m=300_000, old=False):
    X = rng.normal(size=(m, D)) + drift * DRIFT_DIR
    U = draw_u(rng, m)
    P = pi_old_full(X, U, alpha, tau, beta) if old else policy(X)
    return float((P * expit(logits_r(X, U, gamma))).sum(1).mean())


# ---------- estimators ----------
def fit_q(X, a, y, folds=2, seed=0):
    """Cross-fitted per-action logistic reward model; returns q_hat(x, .) for each row."""
    n = len(y)
    idx = np.random.default_rng(seed).permutation(n) % folds
    Q = np.zeros((n, K))
    for f in range(folds):
        tr, te = idx != f, idx == f
        for k in range(K):
            m = tr & (a == k)
            if m.sum() < 20 or y[m].min() == y[m].max():
                Q[te, k] = y[m].mean() if m.sum() else y[tr].mean()
            else:
                clf = LogisticRegression(C=1.0, max_iter=200).fit(X[m], y[m])
                Q[te, k] = clf.predict_proba(X[te])[:, 1]
    return Q


def terms(logs, pol_probs, Q=None):
    X, a, y, e = logs["X"], logs["a"], logs["y"], logs["e"]
    n = len(y)
    pa = pol_probs[np.arange(n), a]
    w = pa / e
    out = {"ipw": w * y, "w": w, "pa": pa}
    if Q is not None:
        dm = (pol_probs * Q).sum(1)
        out["dm"] = dm
        out["dr"] = dm + w * (y - Q[np.arange(n), a])
    return out


def estimates(t):
    return dict(ipw=t["ipw"].mean(), snips=t["ipw"].sum() / t["w"].sum(),
                dm=t["dm"].mean() if "dm" in t else np.nan,
                dr=t["dr"].mean() if "dr" in t else np.nan)


def ess(w):
    return float(w.sum() ** 2 / (w ** 2).sum())


# ---------- marginal-sensitivity bounds for the self-normalised estimator ----------
def msm_bounds(w_nom_pa, y, e, lam):
    """Bounds on sum(c_i * v_i * y_i) / sum(c_i * v_i) where c_i = pi_new(a_i|x_i),
    v_i = 1/e*_i, and the odds of the true propensity are within a factor lam of the logged odds.
    1/e*_i in [1 + (1/e_i - 1)/lam, 1 + lam*(1/e_i - 1)]. Box-constrained fractional LP:
    optimum is a threshold rule on y (sorted), so a single scan finds it."""
    c = w_nom_pa
    keep = c > 0
    c, y, e = c[keep], y[keep], e[keep]
    lo = 1 + (1 / e - 1) / lam
    hi = 1 + lam * (1 / e - 1)
    res = []
    for sign in (+1, -1):
        order = np.argsort(-sign * y)            # sign=+1: descending y (maximise)
        ys = y[order]
        cl, ch = (c * lo)[order], (c * hi)[order]
        # first k points (in sorted order) get the hi weight, the rest get the lo weight
        num_hi = np.concatenate([[0], np.cumsum(ys * ch)])
        den_hi = np.concatenate([[0], np.cumsum(ch)])
        num_lo = np.concatenate([np.cumsum((ys * cl)[::-1])[::-1], [0]])
        den_lo = np.concatenate([np.cumsum(cl[::-1])[::-1], [0]])
        val = (num_hi + num_lo) / (den_hi + den_lo)
        res.append(val.max() if sign == 1 else val.min())
    return res[1], res[0]   # (lower, upper)


def boot_ci(vals, rng, B=300, alpha=0.05, kind="mean", w=None):
    n = len(vals)
    idx = rng.integers(0, n, size=(B, n))
    if kind == "mean":
        s = vals[idx].mean(1)
    else:  # ratio (SNIPS): vals = w*y, w
        s = vals[idx].sum(1) / w[idx].sum(1)
    return np.quantile(s, [alpha / 2, 1 - alpha / 2])
