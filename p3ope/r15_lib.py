"""R15: generator W7, structurally different from every earlier generator (W1-W6 are all logit-additive in the click logit,
with fatigue a function of the SAME item's repeat count). W7 breaks four of those properties at once:
  1. multiplicative fatigue on the click PROBABILITY:  p = expit(base) * exp(-kappa_uk * s)   (not logit-additive; it bites harder
     on high-click items, which is exactly where a sharper candidate policy concentrates its showings);
  2. category satiation: showing item j also tires the user of items in j's category (weight PHI); the audit's models only count
     same-item repeats, so this state variable is outside every fitted model;
  3. recovery: the fatigue state decays by factor RDEC per round (RDEC = 1 means no recovery);
  4. taste x fatigue interaction at the user-item level: a hidden per-(user,item) affinity v_uk shifts the click logit AND scales
     the fatigue rate, kappa_uk = kappa * exp(RHO * v_uk - RHO^2/2) (RHO may be negative: favourites tire slower).
Each WORLD (wid) draws its own category map, PHI, RDEC, RHO sign and item multipliers, so worlds are independent draws of structure,
not copies of one shape. Same K, D, T_OBS, T_EVAL, old/new policies and slice design as r8_lib. Output dict identical to r8_lib.sim_w3.
"""
import numpy as np
from scipy.special import expit
from p3ope import r2_lib as R
from p3ope import exp13_lib as L
from p3ope.exp13_lib import K, D, logits_r, pi_old_full, pi_old_nominal, pi_new, T_OBS, T_EVAL, TN, ALPHA, TAU_OLD

GV = 0.5          # sd of the hidden per-(user,item) click-logit shift
NCAT = K // 2


def world(wid):
    r = np.random.default_rng([2026, 15, int(wid)])
    return dict(cat=r.permutation(K) // 2, phi=float(r.uniform(0.3, 1.0)), rdec=float(r.uniform(0.6, 1.0)),
                rho=float(r.choice([-0.7, 0.7])), mk=np.exp(0.4 * r.normal(size=K) - 0.08))


class State:
    def __init__(self, n, w):
        self.n, self.w = n, w; self.si = np.zeros((n, K)); self.sc = np.zeros((n, NCAT)); self.ii = np.arange(n)

    def s(self, a):
        w = self.w; si = self.si[self.ii, a]; sc = self.sc[self.ii, w["cat"][a]]
        return si + w["phi"] * (sc - si)

    def step(self, a):
        w = self.w; self.si *= w["rdec"]; self.sc *= w["rdec"]; self.si[self.ii, a] += 1; self.sc[self.ii, w["cat"][a]] += 1


def _p(base, v, kappa, w, a, st, ii):
    ku = kappa * np.exp(w["rho"] * v[ii, a] - w["rho"] ** 2 / 2) * w["mk"][a]
    return expit(base[ii, a] + GV * v[ii, a]) * np.exp(-ku * st.s(a))


def sim_w7(n, rng, wid, kappa, beta, gamma, mode="old", T=T_OBS):
    w = world(wid); X0 = rng.normal(size=(n, D)); U = rng.normal(size=n); base = logits_r(X0, U, gamma); v = rng.normal(size=(n, K))
    Pold = pi_old_full(X0, U, ALPHA, TAU_OLD, beta); Punif = np.full((n, K), 1.0 / K)
    st = State(n, w); cs = R.St(n); ii = np.arange(n); A = np.zeros((T, n), int); Y = np.zeros((T, n)); G = {s: np.zeros((T, n)) for s in ("lin", "log", "mem7", "tail2")}; prev = None
    for t in range(T):
        P = Punif if mode in ("slice", "tail") else Pold
        if mode == "tail" and t > 0: P = 0.5 * Punif; P[ii, prev] += 0.5
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        y = (rng.random(n) < _p(base, v, kappa, w, a, st, ii)).astype(float); A[t], Y[t] = a, y
        for s in G: G[s][t] = cs.feat(s, a)
        st.step(a); cs.step(a); prev = a
    e = np.full(n, 1.0 / K) if mode in ("slice", "tail") else pi_old_nominal(X0, ALPHA, TAU_OLD, beta)[ii, A[0]]
    return dict(X0=X0, A=A, Y=Y, G=G, e=e, n=n, T=T)


def _roll(Pc, base, v, kappa, w, ua, ur, T):
    n = Pc.shape[0]; st = State(n, w); ii = np.arange(n); out = np.empty(T)
    for t in range(T):
        a = (Pc > ua[t][:, None]).argmax(1); out[t] = (ur[t] < _p(base, v, kappa, w, a, st, ii)).mean(); st.step(a)
    return out


def true_lift_w7(wid, kappa, beta, gamma, H=T_EVAL, n=60000, seed=7):
    r = np.random.default_rng(seed); X0 = r.normal(size=(n, D)); U = r.normal(size=n); v = r.normal(size=(n, K)); base = logits_r(X0, U, gamma); w = world(wid)
    Pn = pi_new(X0, TN).cumsum(1); Po = pi_old_full(X0, U, ALPHA, TAU_OLD, beta).cumsum(1); ua, ur = L.draws(n, T_EVAL, seed + 1)
    return float((_roll(Pn, base, v, kappa, w, ua, ur, T_EVAL) - _roll(Po, base, v, kappa, w, ua, ur, T_EVAL))[:H].mean())
