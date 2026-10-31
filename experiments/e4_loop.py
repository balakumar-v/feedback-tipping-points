"""P12 closed loop: NEED_DATA from a 1500-user pilot slice -> size the slice by n* = max(n_kappa, n_static) -> re-audit with a fresh slice of n* users (cap 8000)."""
import sys, json, time, numpy as np, pandas as pd
from p3ope.exp13_lib import *
S0, S1, out = int(sys.argv[1]), int(sys.argv[2]), open(sys.argv[3], "a")
df = pd.DataFrame([json.loads(l) for l in open("results/round-01/e4_sizing.jsonl")]); C = float((df.ks.groupby([df.m, df.ns]).std() * np.sqrt(df.groupby(["m", "ns"]).ns.first())).median())
print("c = SD(kappa_slice)*sqrt(n) median over cells:", round(C, 3), flush=True)
N, NS0, B, CAP = 4000, 1500, 60, 8000; beta, gamma = 0.5, 0.8; T0 = time.time()

def slice_verdict(d, WU, ybar0, obs_old, Wb, bb, ns, rng, kind, kappa):
    ds = simulate_obs(ns, rng, kind, kappa, 0.0, beta, gamma, "slice"); bs, Xs, ys = fit_full(ds); Ws, bsv, ks = unpack(bs)
    ksb, WUs = boot_kappa(Xs, ys, bs, ns, T_OBS, B, rng); k_lo, k_hi = np.quantile(ksb, [.025, .975])
    v = K * pi_new(ds["X0"], TN)[np.arange(ns), ds["a"][0]] * ds["y"][0]; lift = v.mean() - ybar0.mean()
    lb = (WUs @ v) / WUs.sum(1) - (WU @ ybar0) / WU.sum(1); s_lo, s_hi = np.quantile(lb, [.025, .975])
    dl = calib_delta(Ws, bsv, ks, beta, obs_old); kst = tipping_kappa(Ws, bsv, beta, dl)
    return verdict(s_lo, s_hi, k_lo, k_hi, kst), ks, kst, lift, v.std(ddof=1)

for kappa in (0.0, 0.2, 0.4, 0.6):
    tl, _ = true_lift("lin", kappa, 0.0, beta, gamma); cls = "worse" if tl < -0.002 else ("better" if tl > 0.002 else "marg")
    for seed in range(S0, S1):
        rng = np.random.default_rng([seed, int(kappa * 10), 77])
        d = simulate_obs(N, rng, "lin", kappa, 0.0, beta, gamma, "old"); b, Xb, yb = fit_full(d); Wb, bb, _ = unpack(b)
        _, WU = boot_kappa(Xb, yb, b, N, T_OBS, B, rng); ybar0 = d["y"][0]; obs_old = d["y"].mean(1)
        v1, ks, kst, lift, sdv = slice_verdict(d, WU, ybar0, obs_old, Wb, bb, NS0, rng, "lin", kappa)
        rec = dict(kappa=kappa, seed=seed, true_lift=tl, cls=cls, v1=v1, ks=ks, kstar_s=kst, lift_s=lift)
        if v1 == "NEED_DATA":
            gap_k = abs(ks - kst) if np.isfinite(kst) else 1e9
            n_k = (1.96 * C / max(gap_k, 1e-6)) ** 2; n_s = (1.96 * sdv / max(abs(lift), 1e-6)) ** 2
            nstar = int(np.ceil(max(n_k, n_s, NS0))); rec.update(n_k=n_k, n_static=n_s, nstar=nstar)
            n2 = min(nstar, CAP); v2, ks2, kst2, lift2, _ = slice_verdict(d, WU, ybar0, obs_old, Wb, bb, n2, rng, "lin", kappa)
            rec.update(n2=n2, capped=nstar > CAP, v2=v2)
        out.write(json.dumps(rec, default=float) + "\n"); out.flush()
    print("kappa", kappa, "elapsed", round(time.time() - T0), flush=True)
