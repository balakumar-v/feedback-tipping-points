"""Measured-kappa audit. Users see T_OBS rounds of the OLD policy; reward logit = base(x,a) + gamma*u*c_a - kappa*count(user,a).
Estimate kappa from (a) the observational logs, (b) a small uniformly-randomised exposure slice. Forecast the NEW policy's cumulative lift with the fitted model.
Compare verdicts with: one-step OPE (blind to dynamics) and the truth."""
import numpy as np, time, warnings
warnings.filterwarnings("ignore")
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
from sklearn.linear_model import LogisticRegression
op.NL = 0.0
rng = np.random.default_rng(1414); T0 = time.time()
N, NS, T_OBS, T_EVAL, ALPHA, TAU_OLD, TN = 8000, 1500, 6, 10, 0.8, 1.0, 0.5

def design(X, a, count):
    oh = np.eye(K)[a]
    return np.hstack([(X[:, None, :] * oh[:, :, None]).reshape(len(X), K * D), oh, count[:, None]])

def simulate_obs(n, rng, kappa, beta, gamma, policy="old"):
    X = rng.normal(size=(n, D)); U = rng.normal(size=n); base = logits_r(X, U, gamma)
    counts = np.zeros((n, K)); rows = []
    for t in range(T_OBS):
        if policy == "old": P = pi_old_full(X, U, ALPHA, TAU_OLD, beta)
        else: P = np.full((n, K), 1.0 / K)           # randomised exposure slice
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1); c = counts[np.arange(n), a]
        y = (rng.random(n) < expit(base[np.arange(n), a] - kappa * c)).astype(float)
        rows.append((design(X, a, c), y)); counts[np.arange(n), a] += 1
    return np.vstack([r[0] for r in rows]), np.concatenate([r[1] for r in rows])

def fit(Xd, y):
    m = LogisticRegression(C=10.0, max_iter=400).fit(Xd, y); return m.coef_[0], m.intercept_[0]

def rollout_lift(pol_new, pol_old, base_fn, kappa, n, rng, T):
    X = rng.normal(size=(n, D)); U = rng.normal(size=n); base = base_fn(X, U)
    res = []
    for pol in (pol_new, pol_old):
        r2 = np.random.default_rng(int(rng.integers(1 << 30))) if False else None
    draws = rng.random((T, n)); noise = rng.random((T, n)); out = []
    for pol in (pol_new, pol_old):
        counts = np.zeros((n, K)); tot = 0.0
        for t in range(T):
            P = pol(X, U); a = (P.cumsum(1) > draws[t][:, None]).argmax(1)
            p = expit(base[np.arange(n), a] - kappa * counts[np.arange(n), a]); tot += (noise[t] < p).mean(); counts[np.arange(n), a] += 1
        out.append(tot / T)
    return out[0] - out[1]

def run(kappa_true, beta, gamma, reps=3):
    rows = []
    for r in range(reps):
        Xo, yo = simulate_obs(N, rng, kappa_true, beta, gamma, "old"); Xs, ys = simulate_obs(NS, rng, kappa_true, beta, gamma, "slice")
        co, io = fit(Xo, yo); cs, is_ = fit(Xs, ys)
        k_obs, k_sl = -co[-1], -cs[-1]
        W_o = co[:K * D].reshape(K, D); b_o = co[K * D:K * D + K] + io
        pn = lambda X, U: pi_new(X, TN); po = lambda X, U: pi_old_full(X, U, ALPHA, TAU_OLD, beta)
        true_lift = rollout_lift(pn, po, lambda X, U: logits_r(X, U, gamma), kappa_true, 20000, np.random.default_rng(5 + r), T_EVAL)
        # forecast with the fitted bulk model; the new policy is the same softmax over TRUE logits (known policy), logger probabilities known
        pred = {}
        for name, kh in (("obs", k_obs), ("slice", k_sl)):
            pred[name] = rollout_lift(pn, po, lambda X, U: X @ W_o.T + b_o, kh, 20000, np.random.default_rng(5 + r), T_EVAL)
        zero_lift = rollout_lift(pn, po, lambda X, U: logits_r(X, U, gamma), 0.0, 20000, np.random.default_rng(5 + r), 1)   # one-step (round-0) true lift
        rows.append((k_obs, k_sl, true_lift, pred["obs"], pred["slice"], zero_lift))
    a = np.array(rows); return a.mean(0), a.std(0)

print("columns: kappa_true | kappa_hat(obs logs) | kappa_hat(random slice) | TRUE 10-round lift | forecast w/ obs kappa | forecast w/ slice kappa | one-step lift (what static OPE sees)")
for beta, gamma, label in [(0.0, 0.0, "no hidden taste"), (0.5, 0.8, "hidden taste (logger sees it)")]:
    print("\n==", label)
    for kt in [0.0, 0.2, 0.4, 0.6]:
        m, s = run(kt, beta, gamma)
        print(f"kappa={kt:.1f} | {m[0]:+.3f}±{s[0]:.3f} | {m[1]:+.3f}±{s[1]:.3f} | {m[2]:+.4f} | {m[3]:+.4f} | {m[4]:+.4f} | {m[5]:+.4f}", flush=True)
print("elapsed", round(time.time() - T0, 1))
