"""R4: second held-out data-generating family (breaks the 'simulator = fitted model' match).
World W2 = probit click link p=Phi(z/1.702) (fitted model stays logit) + per-user fatigue kappa_i = kappa*exp(s*eps_i - s^2/2) (mean kappa, lognormal, s=SIG).
Everything else (K, D, T_OBS, T_EVAL, old/new policies, features) is r2_lib / exp13_lib unchanged."""
import numpy as np
from scipy.special import expit
from scipy.stats import norm
from p3ope import r2_lib as R
from p3ope import exp13_lib as L
from p3ope.exp13_lib import K, D, logits_r, pi_old_full, pi_old_nominal, pi_new, T_OBS, T_EVAL, TN, ALPHA, TAU_OLD
SIG = 0.75; PS = 1.702
def link(z, kind="probit"): return norm.cdf(z / PS) if kind == "probit" else expit(z)
def kap_i(n, kappa, rng, sig=None):
    s = SIG if sig is None else sig
    return kappa * np.exp(s * rng.normal(size=n) - s * s / 2) if s > 0 else np.full(n, float(kappa))
def sim_w2(n, rng, kind, kappa, delta, beta, gamma, mode="old", T=T_OBS, lk="probit", sig=None):
    """same output dict as R.simulate"""
    X0 = rng.normal(size=(n, D)); U = rng.normal(size=n); base = logits_r(X0, U, gamma); ki = kap_i(n, kappa, rng, sig)
    Pold = pi_old_full(X0, U, ALPHA, TAU_OLD, beta); Punif = np.full((n, K), 1.0 / K)
    st = R.St(n); ii = np.arange(n); A = np.zeros((T, n), int); Y = np.zeros((T, n)); G = {s: np.zeros((T, n)) for s in ("lin", "log", "mem7", "tail2")}
    for t in range(T):
        P = Punif if (mode == "slice" or (mode == "lastslice" and t == T - 1)) else Pold
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        z = base[ii, a] - ki * st.feat(kind, a) - delta * t
        y = (rng.random(n) < link(z, lk)).astype(float); A[t], Y[t] = a, y
        for s in G: G[s][t] = st.feat(s, a)
        st.step(a)
    e = np.full(n, 1.0 / K) if mode == "slice" else pi_old_nominal(X0, ALPHA, TAU_OLD, beta)[ii, A[0]]
    return dict(X0=X0, A=A, Y=Y, G=G, e=e, n=n, T=T)
def roll_w2(Pc, base, kind, ki, tr, ua, ur, T, lk):
    n = Pc.shape[0]; st = R.St(n); ii = np.arange(n); out = np.empty(T)
    for t in range(T):
        a = (Pc > ua[t][:, None]).argmax(1); z = base[ii, a] - ki * st.feat(kind, a) + tr[t]
        out[t] = (ur[t] < link(z, lk)).mean(); st.step(a)
    return out
def true_lift_w2(kind, kappa, delta=0, beta=0, gamma=0, H=T_EVAL, n=60000, seed=7, lk="probit", sig=None):
    r = np.random.default_rng(seed); X0 = r.normal(size=(n, D)); U = r.normal(size=n); base = logits_r(X0, U, gamma); ki = kap_i(n, kappa, r, sig)
    Pn = pi_new(X0, TN).cumsum(1); Po = pi_old_full(X0, U, ALPHA, TAU_OLD, beta).cumsum(1); ua, ur = L.draws(n, T_EVAL, seed + 1); tr = -delta * np.arange(T_EVAL)
    pn = roll_w2(Pn, base, kind, ki, tr, ua, ur, T_EVAL, lk); po = roll_w2(Po, base, kind, ki, tr, ua, ur, T_EVAL, lk)
    return float((pn - po)[:H].mean())
