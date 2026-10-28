"""R14-1/2: sealed generator W6 under the frozen rule v7, plus tipping margin vs CI-only score. usage: python -m experiments.r14_e1 S0 S1 OUT [cell-index-parity 0|1|all]"""
import sys, json, os, time, numpy as np
from p3ope import r2_lib as R
from p3ope import r8_lib as W
from p3ope import r12_lib as F
from experiments.r2_e5 import vs, comb, dr_terms
from experiments import r3_e1 as X
from experiments import r11_e1 as Q
B, NB = 30, 4000; R.NF = 3000; SH = ("lin", "log", "mem7", "tail2"); beta, gamma = .5, .8; NS = 3000; TS = 10
CELLS6 = [("sigm", .3), ("sigm", 1.2), ("sigm", 2.0), ("sigm", 3.0), ("hump", .3), ("hump", 3.0), ("hump", 5.0), ("hump", 8.0), ("logsq", .1), ("logsq", .8), ("logsq", 1.2), ("logsq", 2.0)]

def audit(db, ds):
    ns = ds["n"]; obs = db["Y"].mean(1); y0b = db["Y"][0]; rng = np.random.default_rng(int(ds["X0"][0, 0] * 1e9) % 2 ** 31)
    WUb = rng.poisson(1.0, size=(B, NB)).astype(float); WUs = rng.poisson(1.0, size=(B, ns)).astype(float); res = {}
    sn = R.snips0(db, WUb); sn_draws = sn[1]; one_step_lo = float(np.quantile(sn_draws, .025)); one_step_pt = float(sn[0])
    for s in SH + ("ff",):
        if s == "ff": b, Xs, ys = F.fit_ff(ds); pt = F.forecast_ff(b, beta, obs)
        else: b, Xs, ys = R.fit(ds, s, True); pt = R.forecast(b, s, True, "flat", beta, obs, 10)
        sl = np.empty(B); fl = np.empty(B); kb = np.empty(B)
        for i in range(B):
            bi = R.newton_fast(Xs, ys, np.tile(WUs[i], ds["T"]), b, 3); vi = dr_terms(ds, bi)
            sl[i] = (WUs[i] @ vi) / WUs[i].sum() - (WUb[i] @ y0b) / WUb[i].sum(); ob = (db["Y"] @ WUb[i]) / WUb[i].sum()
            fl[i] = F.forecast_ff(bi, beta, ob) if s == "ff" else R.forecast(bi, s, True, "flat", beta, ob, 10)
            if s == "lin": kb[i] = R.kappa_of(bi)
        slo, shi = np.quantile(sl, [.025, .975]); lo, hi = np.quantile(fl, [.025, .975])
        res[s] = dict(v=vs(slo, shi, lo, hi), slo=float(slo), shi=float(shi), flo=float(lo), fhi=float(hi), fpt=float(pt), fsd=float(fl.std(ddof=1)))
        if s == "lin":
            kh = R.kappa_of(b); ks = X.kstar(b, beta, obs); se = float(kb.std(ddof=1))
            res[s].update(k=float(kh), kstar=float(ks), se_k=se, margin=float((kh - ks) / se))
    return res, one_step_pt, one_step_lo

def one(kind, kappa, seed, tl):
    cid = sum(map(ord, f"{kind}{kappa}"))
    db = W.sim_w3(NB, np.random.default_rng([seed, cid, 411]), kind, kappa, beta, gamma, "old")
    ds = W.sim_w3(NS, np.random.default_rng([seed, cid, NS, 412]), kind, kappa, beta, gamma, "tail", T=TS)
    res, sn_pt, sn_lo = audit(db, ds); csup, uns = Q.guard(ds); v5 = comb([res[s]["v"] for s in SH]); v6 = "NEED" if (v5 == "APPROVE" and uns > .05) else v5
    v7 = "NEED" if (v6 == "APPROVE" and res["ff"]["v"] != "APPROVE") else v6
    rec = dict(gen="W6", kind=kind, kappa=kappa, seed=seed, true10=tl, unsup=uns, v5=v5, v6=v6, v7=v7, one_step_pt=sn_pt, one_step_lo=sn_lo)
    for s in SH + ("ff",):
        for key, val in res[s].items(): rec[f"{s}_{key}"] = val
    return rec

if __name__ == "__main__":
    s0, s1, f = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; par = sys.argv[4] if len(sys.argv) > 4 else "all"
    cells = CELLS6 if par == "all" else [c for i, c in enumerate(CELLS6) if i % 2 == int(par)]
    done = set()
    if os.path.exists(f): done = {(r["kind"], r["kappa"], r["seed"]) for r in map(json.loads, open(f))}
    out = open(f, "a"); T0 = time.time()
    for kind, kappa in cells:
        tl = W.true_lift_w3(kind, kappa, beta, gamma)
        for seed in range(s0, s1):
            if (kind, kappa, seed) in done: continue
            out.write(json.dumps(one(kind, kappa, seed, tl), default=float) + "\n"); out.flush()
        print("W6", kind, kappa, "true10 %+.4f" % tl, "elapsed", round(time.time() - T0), flush=True)
