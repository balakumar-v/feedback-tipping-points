"""R8: third held-out generator W3, designed AFTER the tail guard (tail2) was frozen, using none of the shapes the guard was tuned on.
Truth shapes (never fitted; the audit still fits lin/log/mem7/tail2):
  step  : 2 * 1[c >= 3]                 (no fatigue until the third repeat)
  expo  : (exp(0.35 c) - 1) / 0.35      (exponentially accelerating)
  late  : 1.5 * max(c - 3, 0)           (fatigue only after three repeats)
Heterogeneity the fitted model cannot see (both mean-preserving):
  per-user  kappa_i = kappa * exp(CPL*U - CPL^2/2), U = the hidden taste that also drives the logger  (taste x fatigue coupling)
  per-item  multiplier m_k = exp(ISIG*e_k - ISIG^2/2), e_k fixed draws
Same world otherwise (K, D, T_OBS, T_EVAL, old/new policies, features) as r2_lib / exp13_lib.
"""
import numpy as np
from scipy.special import expit
from p3ope import r2_lib as R
from p3ope import exp13_lib as L
from p3ope.exp13_lib import K, D, logits_r, pi_old_full, pi_old_nominal, pi_new, T_OBS, T_EVAL, TN, ALPHA, TAU_OLD

CPL, ISIG = 0.5, 0.4
M_ITEM = np.exp(ISIG * np.random.default_rng(2026).normal(size=K) - ISIG ** 2 / 2)
NEW_SHAPES = ("step", "expo", "late", "cliff4", "late4", "quadlate", "bump", "late5", "cubic", "pow15", "q2", "expl3")


def feat3(st, kind, a):
    if kind in NEW_SHAPES:
        c = st.cnt[st.ii, a]
        if kind == "step": return 2.0 * (c >= 3)
        if kind == "cliff4": return 3.0 * (c >= 4)
        if kind == "bump": return 2.5 * ((c >= 3) & (c <= 5))
        if kind == "late5": return 2.0 * np.maximum(c - 5, 0)
        if kind == "cubic": return 0.08 * c ** 3
        if kind == "pow15": return 0.5 * c ** 1.5
        if kind == "q2": return 0.3 * np.maximum(c - 2, 0) ** 2
        if kind == "expl3": return np.exp(0.5 * np.maximum(c - 3, 0)) - 1.0
        if kind == "late4": return 2.0 * np.maximum(c - 4, 0)
        if kind == "quadlate": return 0.6 * np.maximum(c - 3, 0) ** 2
        if kind == "expo": return (np.exp(0.35 * c) - 1.0) / 0.35
        return 1.5 * np.maximum(c - 3, 0)
    return st.feat(kind, a)


def kap_user(U, kappa, cpl=None):
    c = CPL if cpl is None else cpl
    return kappa * np.exp(c * U - c * c / 2)


def sim_w3(n, rng, kind, kappa, beta, gamma, mode="old", T=T_OBS, cpl=None):
    """same output dict as R.simulate; mode old | slice."""
    X0 = rng.normal(size=(n, D)); U = rng.normal(size=n); base = logits_r(X0, U, gamma); ku = kap_user(U, kappa, cpl)
    Pold = pi_old_full(X0, U, ALPHA, TAU_OLD, beta); Punif = np.full((n, K), 1.0 / K)
    st = R.St(n); ii = np.arange(n); A = np.zeros((T, n), int); Y = np.zeros((T, n)); G = {s: np.zeros((T, n)) for s in ("lin", "log", "mem7", "tail2")}; prev = None
    for t in range(T):
        P = Punif if mode in ("slice", "tail") else Pold
        if mode == "tail" and t > 0: P = (1 - 0.5) * Punif; P[ii, prev] += 0.5   # r5_lib design, q=0.5, propensity known
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        z = base[ii, a] - ku * M_ITEM[a] * feat3(st, kind, a)
        y = (rng.random(n) < expit(z)).astype(float); A[t], Y[t] = a, y
        for s in G: G[s][t] = st.feat(s, a)
        st.step(a); prev = a
    e = np.full(n, 1.0 / K) if mode in ("slice", "tail") else pi_old_nominal(X0, ALPHA, TAU_OLD, beta)[ii, A[0]]
    return dict(X0=X0, A=A, Y=Y, G=G, e=e, n=n, T=T)


def _roll(Pc, base, kind, ku, ua, ur, T):
    n = Pc.shape[0]; st = R.St(n); ii = np.arange(n); out = np.empty(T)
    for t in range(T):
        a = (Pc > ua[t][:, None]).argmax(1); z = base[ii, a] - ku * M_ITEM[a] * feat3(st, kind, a)
        out[t] = (ur[t] < expit(z)).mean(); st.step(a)
    return out


def true_lift_w3(kind, kappa, beta, gamma, H=T_EVAL, n=60000, seed=7, cpl=None):
    r = np.random.default_rng(seed); X0 = r.normal(size=(n, D)); U = r.normal(size=n); base = logits_r(X0, U, gamma); ku = kap_user(U, kappa, cpl)
    Pn = pi_new(X0, TN).cumsum(1); Po = pi_old_full(X0, U, ALPHA, TAU_OLD, beta).cumsum(1); ua, ur = L.draws(n, T_EVAL, seed + 1)
    pn = _roll(Pn, base, kind, ku, ua, ur, T_EVAL); po = _roll(Po, base, kind, ku, ua, ur, T_EVAL)
    return float((pn - po)[:H].mean())
