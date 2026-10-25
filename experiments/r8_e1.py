"""R8-1 logs-only audit UNDER HIDDEN TASTE, final four-shape rule v4 (every earlier logs-only run had no taste).
usage: python -m experiments.r8_e1 S0 S1 OUT   (taste x1 and x2: beta,gamma = .5m,.8m; linear fatigue)"""
import sys, json, os, time, numpy as np
from p3ope import r2_lib as R
from experiments.r2_e5 import vs, comb
B, N = 30, 4000; R.NF = 3000; SH = ("lin", "log", "mem7", "tail2")
MS = (1.0, 2.0); KAPPAS = (0.0, .2, .4, .6, .8, 1.0, 1.5)
def audit(m, kappa, seed, tl):
    beta, gamma = .5 * m, .8 * m
    rng = np.random.default_rng([seed, int(m * 10), int(kappa * 10), 88])
    d = R.simulate(N, rng, "lin", kappa, 0, beta, gamma, "old"); n, T = N, d["T"]
    WU = rng.poisson(1.0, size=(B, n)).astype(float)
    s_pt, sb = R.snips0(d, WU); s_lo, s_hi = np.quantile(sb, [.025, .975]); obs = d["Y"].mean(1)
    rec = dict(m=m, kappa=kappa, seed=seed, true10=tl, s_pt=s_pt, s_lo=s_lo, s_hi=s_hi); vl = {}
    for s in SH:
        b, Xd, y = R.fit(d, s); pt = R.forecast(b, s, False, "flat", beta, obs, 10); fl = np.empty(B)
        for i in range(B):
            bi = R.newton_fast(Xd, y, np.tile(WU[i], T), b, 3); obs_i = (d["Y"] @ WU[i]) / WU[i].sum()
            fl[i] = R.forecast(bi, s, False, "flat", beta, obs_i, 10)
        lo, hi = np.quantile(fl, [.025, .975]); vl[s] = vs(s_lo, s_hi, lo, hi)
        rec.update({f"{s}_k": R.kappa_of(b), f"{s}_pt": pt, f"{s}_lo": lo, f"{s}_hi": hi, f"{s}_v": vl[s]})
    rec["v4"] = comb(list(vl.values()))
    return rec
if __name__ == "__main__":
    s0, s1 = int(sys.argv[1]), int(sys.argv[2]); done = set()
    if os.path.exists(sys.argv[3]): done = {(r["m"], r["kappa"], r["seed"]) for r in map(json.loads, open(sys.argv[3]))}
    out = open(sys.argv[3], "a"); T0 = time.time()
    for m in MS:
        for kappa in KAPPAS:
            tl = R.true_lift("lin", kappa, 0, .5 * m, .8 * m)
            for seed in range(s0, s1):
                if (m, kappa, seed) in done: continue
                out.write(json.dumps(audit(m, kappa, seed, tl), default=float) + "\n"); out.flush()
            print("m", m, "kappa", kappa, "true10 %+.4f" % tl, "elapsed", round(time.time() - T0), flush=True)
