"""R5: tail-targeted slice design (known propensities depending only on past actions) + slice audit with tipping margin."""
import numpy as np
from scipy.special import expit
from p3ope import r2_lib as R
from p3ope.exp13_lib import K, D, logits_r, pi_old_full, ALPHA, TAU_OLD, T_OBS
Q = 0.5
def simulate_tail(n, rng, kappa, beta, gamma, q=Q, T=T_OBS):
    """round 0 uniform; later rounds: with prob q repeat previous item else uniform. Propensity (1-q)/K + q*1[k==prev]. Same output dict as R.simulate (e = 1/K at round 0)."""
    X0 = rng.normal(size=(n, D)); U = rng.normal(size=n); base = logits_r(X0, U, gamma)
    st = R.St(n); ii = np.arange(n); A = np.zeros((T, n), int); Y = np.zeros((T, n)); G = {s: np.zeros((T, n)) for s in ("lin", "log", "mem7", "tail2")}
    prev = None
    for t in range(T):
        P = np.full((n, K), 1.0 / K)
        if t > 0: P = (1 - q) * P; P[ii, prev] += q
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        z = base[ii, a] - kappa * st.feat("lin", a)
        y = (rng.random(n) < expit(z)).astype(float); A[t], Y[t] = a, y
        for s in G: G[s][t] = st.feat(s, a)
        st.step(a); prev = a
    return dict(X0=X0, A=A, Y=Y, G=G, e=np.full(n, 1.0 / K), n=n, T=T)
