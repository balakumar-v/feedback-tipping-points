"""R10-1 n* with a pilot-uncertainty band. usage: python -m experiments.r10_e1 S0 S1 OUT"""
import sys, json, numpy as np
from p3ope import r2_lib as R
from experiments import r3_e1 as X
X.SH = ("lin",); M = 1.0; beta, gamma = .5, .8; Z = 1.96 + 0.84
def one(kappa, seed, tl):
    rng = np.random.default_rng([seed, int(kappa * 10), 99])
    db = R.simulate(X.NB, rng, "lin", kappa, 0, beta, gamma, "old"); dp = R.simulate(X.NS0, rng, "lin", kappa, 0, beta, gamma, "slice")
    res, _ = X.audit(db, dp, beta); r = res["lin"]; e, sd = r["pt"], r["sd_f"]; se = sd / np.sqrt(X.NS0)
    f = lambda a: np.inf if a <= 0 else (Z * sd / a) ** 2
    return dict(kappa=kappa, seed=seed, true10=tl, est=e, sd_f=sd, n_pt=f(abs(e)), n_lo=f(abs(e) + 1.96 * se), n_hi=f(abs(e) - 1.96 * se))
if __name__ == "__main__":
    s0, s1 = int(sys.argv[1]), int(sys.argv[2]); out = open(sys.argv[3], "a")
    for k in (0.0, .2, .3, .4, .6):
        tl = R.true_lift("lin", k, 0, .5 * M, .8 * M)
        for s in range(s0, s1): out.write(json.dumps(one(k, s, tl), default=float) + "\n"); out.flush()
        print("kappa", k, "true10 %+.4f" % tl, flush=True)
