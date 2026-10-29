"""R15-3 (post hoc, Addendum 20): why a randomised slice's pooled kappa-hat is biased low under hidden taste.
Exposure is randomised, so the bias is not confounding: the unlogged taste term widens the latent logit spread and shrinks the
pooled (marginal) log-odds slope toward zero (non-collapsibility of the logit). Supplying the true hidden term removes it.
usage: python -m experiments.r15_e3 [OUT.jsonl]"""
import sys, json, time, numpy as np
from scipy.special import expit
from p3ope import r2_lib as R
from p3ope.ope_pilot import C
from p3ope.exp13_lib import K, D, logits_r


def sim(n, rng, kappa, gamma, T=10):
    """repeat-heavy slice (round 0 uniform, then repeat previous item w.p. 0.5); also returns U for the oracle fit."""
    X0 = rng.normal(size=(n, D)); U = rng.normal(size=n); base = logits_r(X0, U, gamma)
    st = R.St(n); ii = np.arange(n); A = np.zeros((T, n), int); Y = np.zeros((T, n)); G = np.zeros((T, n)); prev = None
    for t in range(T):
        P = np.full((n, K), 1.0 / K)
        if t > 0: P = 0.5 * P; P[ii, prev] += 0.5
        a = (P.cumsum(1) > rng.random((n, 1))).argmax(1)
        y = (rng.random(n) < expit(base[ii, a] - kappa * st.feat("lin", a))).astype(float); A[t], Y[t], G[t] = a, y, st.feat("lin", a); st.step(a); prev = a
    return dict(X0=X0, A=A, Y=Y, G={"lin": G}, n=n, T=T, U=U)


def fit_oracle(d, gamma):
    Xd = R.design(d["X0"], d["A"], d["G"]["lin"], True); hid = (gamma * d["U"][None, :] * C[d["A"]]).reshape(-1)
    P = Xd.shape[1]; b = np.zeros(P); y = d["Y"].reshape(-1)
    for _ in range(12):
        p = expit(Xd @ b + hid); g = Xd.T @ (p - y) + R.RIDGE * b; H = (Xd * (p * (1 - p))[:, None]).T @ Xd + R.RIDGE * np.eye(P); b -= np.linalg.solve(H, g)
    return -b[K * D + K]


def run(kappa=0.8, seeds=12, n=3000):
    rows = []
    for m in (0.0, 1.0, 2.0, 3.0):
        gamma = 0.8 * m; ks, ko = [], []
        for seed in range(seeds):
            d = sim(n, np.random.default_rng([77, int(m * 10), seed]), kappa, gamma)
            b, _, _ = R.fit(d, "lin", True); ks.append(R.kappa_of(b)); ko.append(fit_oracle(d, gamma))
        rows.append(dict(taste=m, gamma=gamma, pooled_bias=float(np.mean(ks) - kappa), pooled_se=float(np.std(ks, ddof=1) / np.sqrt(seeds)),
                         oracle_bias=float(np.mean(ko) - kappa), attenuation_formula_bias=float(kappa / np.sqrt(1 + 0.346 * gamma ** 2) - kappa)))
    return rows


if __name__ == "__main__":
    t0 = time.time(); rows = run()
    for r in rows:
        print("taste x%.0f gamma %.2f | pooled bias %+.3f (se %.3f) | true hidden term supplied %+.3f | attenuation formula %+.3f" % (r["taste"], r["gamma"], r["pooled_bias"], r["pooled_se"], r["oracle_bias"], r["attenuation_formula_bias"]))
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            for r in rows: f.write(json.dumps(r) + "\n")
    print("elapsed %.0fs" % (time.time() - t0))
