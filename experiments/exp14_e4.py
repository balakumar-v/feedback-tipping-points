"""E4: slice sizing/power for static lift and for kappa; whole-model-on-slice vs hybrid vs bulk forecasts. usage: python3 exp14_e4.py SEEDS OUT.jsonl"""
import sys, json, time, numpy as np
from p3ope.exp13_lib import *
from p3ope import ope_pilot as op
S = int(sys.argv[1]); out = open(sys.argv[2], "a"); T0 = time.time()
N_OBS, KAPPA = 4000, 0.4
for m in (0.0, 0.5, 1.0, 2.0):
    beta, gamma = 0.5 * m, 0.8 * m
    tl, tl0 = true_lift("lin", KAPPA, 0.0, beta, gamma)
    Vn = float(true_paths("lin", 0.0, 0.0, beta, gamma)[0][0])  # round-0 V_new (fatigue-free)
    for ns in (250, 500, 1000, 2000, 4000):
        for seed in range(S):
            rng = np.random.default_rng([seed, int(m * 10), ns])
            d = simulate_obs(N_OBS, rng, "lin", KAPPA, 0.0, beta, gamma, "old"); ds = simulate_obs(ns, rng, "lin", KAPPA, 0.0, beta, gamma, "slice")
            b, Xb, yb = fit_full(d); bs, Xs, ys = fit_full(ds)
            kb, ks = -b[-1], -bs[-1]; seb, ses = sandwich_se_kappa(Xb, yb, b, N_OBS, T_OBS), sandwich_se_kappa(Xs, ys, bs, ns, T_OBS)
            zk = (kb - ks) / np.hypot(seb, ses)
            pnb = pi_new(d["X0"], TN)[np.arange(N_OBS), d["a"][0]]; w = pnb / d["e"]; y0 = d["y"][0]; sn = (w * y0).sum() / w.sum()
            vb = (w * (y0 - sn)) ** 2; se_sn = np.sqrt(vb.sum()) / w.sum()
            v = K * pi_new(ds["X0"], TN)[np.arange(ns), ds["a"][0]] * ds["y"][0]; vs, se_v = v.mean(), v.std(ddof=1) / np.sqrt(ns)
            zs = (sn - vs) / np.hypot(se_sn, se_v)
            rec = dict(m=m, ns=ns, seed=seed, kb=kb, ks=ks, seb=seb, ses=ses, zk=zk, sn=sn, vs=vs, zs=zs, Vn=Vn, true_lift=tl,
                       ks_in_ci=int(abs(ks - KAPPA) <= 1.96 * ses), kb_in_ci=int(abs(kb - KAPPA) <= 1.96 * seb), sn_bias=sn - Vn, vs_bias=vs - Vn)
            if m in (1.0, 2.0):
                Wb, bb, _ = unpack(b); Ws, bsv, _ = unpack(bs); obs_old = d["y"].mean(1)
                dl_b = calib_delta(Wb, bb, kb, beta, obs_old); rec["fc_bulk"] = forecast_lift(Wb, bb, kb, beta, dl_b)
                dl_h = calib_delta(Wb, bb, ks, beta, obs_old); rec["fc_hyb"] = forecast_lift(Wb, bb, ks, beta, dl_h)
                dl_s = calib_delta(Ws, bsv, ks, beta, obs_old); rec["fc_slice"] = forecast_lift(Ws, bsv, ks, beta, dl_s)
            out.write(json.dumps(rec, default=float) + "\n"); out.flush()
        print("m", m, "ns", ns, "elapsed", round(time.time() - T0), flush=True)
