"""E3 runner. usage: python3 exp13_e3.py GROUP SEED0 SEED1 OUT.jsonl   (GROUP in A,B,C,D,E or 'all'; cells defined in CELLS)"""
import sys, json, time, numpy as np
from p3ope.exp13_lib import *
B_BOOT, N_OBS, N_SLICE = 80, 4000, 1500
TASTE = (0.5, 0.8)
CELLS = []
for k in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0): CELLS.append(dict(id=f"A_lin_k{k}", grp="A", kind="lin", kappa=k, eta=0.0, beta=0.0, gamma=0.0, mode="old", slice=False))
for k in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0): CELLS.append(dict(id=f"B_taste_lin_k{k}", grp="B", kind="lin", kappa=k, eta=0.0, beta=TASTE[0], gamma=TASTE[1], mode="old", slice=True))
for kind in ("sat", "decay", "window", "convex"):
    for k in (0.2, 0.4, 0.6, 0.9): CELLS.append(dict(id=f"C_{kind}_k{k}", grp="C", kind=kind, kappa=k, eta=0.0, beta=0.0, gamma=0.0, mode="old", slice=False))
for kind in ("sat", "decay", "window"):   # grid extension (deviation from prereg grid): the prespecified kappa grid never produced a truly-worse truth for these forms
    for k in (1.5, 2.5, 4.0): CELLS.append(dict(id=f"F_{kind}_k{k}", grp="F", kind=kind, kappa=k, eta=0.0, beta=0.0, gamma=0.0, mode="old", slice=False))
for eta, k in ((0.1, 0.0), (0.2, 0.0), (0.3, 0.0), (0.2, 0.6)): CELLS.append(dict(id=f"D_drift_eta{eta}_k{k}", grp="D", kind="drift", kappa=k, eta=eta, beta=0.0, gamma=0.0, mode="old", slice=False))
for eta in (-0.2, -0.35, -0.5): CELLS.append(dict(id=f"G_revdrift_eta{eta}", grp="G", kind="drift", kappa=0.0, eta=eta, beta=0.0, gamma=0.0, mode="old", slice=False))   # exploratory: taste drifts AWAY from shown items
for k in (0.2, 0.6, 1.0): CELLS.append(dict(id=f"E_retrain_k{k}", grp="E", kind="lin", kappa=k, eta=0.0, beta=0.0, gamma=0.0, mode="retrain", slice=False))

def audit(c, seed, tl, tl0, kst_true):
    rng = np.random.default_rng(10_000 * (hash(c["id"]) % 1000 + 1) + seed) if False else np.random.default_rng([seed, abs(hash(c["id"])) % (2**31) if False else sum(map(ord, c["id"]))])
    d = simulate_obs(N_OBS, rng, c["kind"], c["kappa"], c["eta"], c["beta"], c["gamma"], c["mode"])
    b, Xd, y = fit_full(d); Wb, bb, kh = unpack(b)
    kb, WU = boot_kappa(Xd, y, b, N_OBS, T_OBS, B_BOOT, rng)
    k_lo, k_hi = np.quantile(kb, [.025, .975])
    s_pt, sb = static_snips(d, c["beta"], WU); s_lo, s_hi = np.quantile(sb, [.025, .975])
    obs_old = d["y"].mean(1)
    dl = 0.0 if c["mode"] == "retrain" else calib_delta(Wb, bb, kh, c["beta"], obs_old)
    kstar = tipping_kappa(Wb, bb, c["beta"], dl); fl = forecast_lift(Wb, bb, kh, c["beta"], dl)
    r = dict(cell=c["id"], seed=seed, kappa=c["kappa"], true_lift=tl, true_lift0=tl0, kstar_true=kst_true,
             kh=kh, k_lo=k_lo, k_hi=k_hi, k_sd=float(kb.std()), kstar=kstar, delta=dl, fc_lift=fl, s_pt=s_pt, s_lo=s_lo, s_hi=s_hi,
             v_logs=verdict(s_lo, s_hi, k_lo, k_hi, kstar), v_onestep=one_step_verdict(s_lo), gap=abs(kh - kstar) if np.isfinite(kstar) else None)
    if c["slice"]:
        ds = simulate_obs(N_SLICE, rng, c["kind"], c["kappa"], c["eta"], c["beta"], c["gamma"], "slice")
        bs, Xs, ys = fit_full(ds); Ws, bsv, ks = unpack(bs)
        ksb, WUs = boot_kappa(Xs, ys, bs, N_SLICE, T_OBS, B_BOOT, rng)
        ks_lo, ks_hi = np.quantile(ksb, [.025, .975])
        pn_a = pi_new(ds["X0"], TN)[np.arange(N_SLICE), ds["a"][0]]; v = K * pn_a * ds["y"][0]
        ybar0 = d["y"][0]
        lift_s = v.mean() - ybar0.mean()
        lift_sb = (WUs @ v) / WUs.sum(1) - (WU @ ybar0) / WU.sum(1)
        ss_lo, ss_hi = np.quantile(lift_sb, [.025, .975])
        dls = calib_delta(Ws, bsv, ks, c["beta"], obs_old); kstar_s = tipping_kappa(Ws, bsv, c["beta"], dls)
        fl_s = forecast_lift(Ws, bsv, ks, c["beta"], dls)
        dlh = calib_delta(Wb, bb, ks, c["beta"], obs_old); fl_h = forecast_lift(Wb, bb, ks, c["beta"], dlh)
        r.update(ks=ks, ks_lo=ks_lo, ks_hi=ks_hi, ks_sd=float(ksb.std()), kstar_s=kstar_s, fc_lift_s=fl_s, fc_lift_h=fl_h, ss_pt=lift_s, ss_lo=ss_lo, ss_hi=ss_hi,
                 v_slice=verdict(ss_lo, ss_hi, ks_lo, ks_hi, kstar_s), gap_s=abs(ks - kstar_s) if np.isfinite(kstar_s) else None)
    return r

if __name__ == "__main__":
    grp, s0, s1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    T0 = time.time(); f = open(out, "a")
    for c in CELLS:
        if grp != "all" and c["grp"] not in grp.split(","): continue
        tl, tl0 = true_lift(c["kind"], c["kappa"], c["eta"], c["beta"], c["gamma"])
        kst = true_tipping(c["beta"], c["gamma"]) if (c["kind"] == "lin" and c["mode"] == "old") else None
        for seed in range(s0, s1):
            f.write(json.dumps(audit(c, seed, tl, tl0, kst), default=float) + "\n"); f.flush()
        print(c["id"], "true lift %+.4f" % tl, "kstar_true", kst, "elapsed", round(time.time() - T0), flush=True)
