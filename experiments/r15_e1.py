"""R15-1: frozen rule v7 on 40 independent W7 worlds (Addendum 20). usage: python -m experiments.r15_e1 SEED0 SEED1 OUT [W0 W1]
Seeds 20000-20002 x worlds 0-39 = 120 audits (about 13 min on one core)."""
import sys, json, os, time, numpy as np
from p3ope import r15_lib as W7
from experiments import r14_e1 as E14
from experiments.r2_e5 import comb
from experiments import r11_e1 as Q
B, NB, NS, TS, SH, beta, gamma = E14.B, E14.NB, E14.NS, E14.TS, E14.SH, E14.beta, E14.gamma
NW = 40


def kappa_of_world(wid):
    r = np.random.default_rng([2026, 15, int(wid), 1]); return float(np.round(np.exp(r.uniform(np.log(0.03), np.log(0.6))), 4))


def one(wid, seed, tl):
    kappa = kappa_of_world(wid)
    db = W7.sim_w7(NB, np.random.default_rng([seed, wid, 711]), wid, kappa, beta, gamma, "old")
    ds = W7.sim_w7(NS, np.random.default_rng([seed, wid, NS, 712]), wid, kappa, beta, gamma, "tail", T=TS)
    res, sn_pt, sn_lo = E14.audit(db, ds); csup, uns = Q.guard(ds); v5 = comb([res[s]["v"] for s in SH]); v6 = "NEED" if (v5 == "APPROVE" and uns > .05) else v5
    v7 = "NEED" if (v6 == "APPROVE" and res["ff"]["v"] != "APPROVE") else v6
    rec = dict(gen="W7", world=wid, kind=f"w{wid}", kappa=kappa, seed=seed, true10=tl, unsup=uns, v5=v5, v6=v6, v7=v7, one_step_pt=sn_pt, one_step_lo=sn_lo)
    for s in SH + ("ff",):
        for key, val in res[s].items(): rec[f"{s}_{key}"] = val
    return rec


if __name__ == "__main__":
    if len(sys.argv) < 4: sys.exit("usage: python -m experiments.r15_e1 SEED0 SEED1 OUT [W0 W1]")
    s0, s1, f = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    w0, w1 = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, NW)
    done = set()
    if os.path.exists(f): done = {(r["world"], r["seed"]) for r in map(json.loads, open(f))}
    out = open(f, "a"); T0 = time.time()
    for wid in range(w0, w1):
        tl = W7.true_lift_w7(wid, kappa_of_world(wid), beta, gamma)
        for seed in range(s0, s1):
            if (wid, seed) in done: continue
            out.write(json.dumps(one(wid, seed, tl), default=float) + "\n"); out.flush()
        print("W7 world", wid, "kappa", kappa_of_world(wid), "true10 %+.4f" % tl, "elapsed", round(time.time() - T0), flush=True)
