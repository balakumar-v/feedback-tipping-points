"""R13-1 guard stress: rule v7 when the new policy repeats beyond the slice's support (run with P3_TN=0.2; default 0.5 reproduces R12).
usage: P3_TN=0.2 python -m experiments.r13_e1 S0 S1 OUT   (W5 cells; records v5 = four shapes agree, v6 = + coverage guard, v7 = + free-form veto)"""
import sys, json, os, time, numpy as np
from p3ope import r8_lib as W
from experiments.r2_e5 import comb
from experiments import r11_e1 as Q
from experiments import r12_e1 as F

def one(kind, kappa, seed, tl):
    cid = sum(map(ord, f"{kind}{kappa}")); t0 = time.time()
    db = W.sim_w3(F.NB, np.random.default_rng([seed, cid, 411]), kind, kappa, F.beta, F.gamma, "old")
    ds = W.sim_w3(F.NS, np.random.default_rng([seed, cid, F.NS, 412]), kind, kappa, F.beta, F.gamma, "tail", T=F.TS)
    res = F.audit(db, ds); csup, uns = Q.guard(ds); v5 = comb([res[s]["v"] for s in F.SH])
    v6 = "NEED" if (v5 == "APPROVE" and uns > .05) else v5
    v7 = "NEED" if (v6 == "APPROVE" and res["ff"]["v"] != "APPROVE") else v6
    rec = dict(gen="W5", tn=float(os.environ.get("P3_TN", 0.5)), kind=kind, kappa=kappa, seed=seed, true10=tl, csup=csup, unsup=uns,
               guard_fires=bool(uns > .05), v5=v5, v6=v6, v7=v7, ff_v=res["ff"]["v"], sec=round(time.time() - t0, 1))
    for s in F.SH: rec[f"{s}_v"] = res[s]["v"]
    return rec

if __name__ == "__main__":
    if len(sys.argv) < 4: sys.exit("usage: P3_TN=0.2 python -m experiments.r13_e1 SEED0 SEED1 OUT")
    s0, s1, f = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; done = set()
    if os.path.exists(f): done = {(r["kind"], r["kappa"], r["seed"]) for r in map(json.loads, open(f))}
    out = open(f, "a"); T0 = time.time()
    for kind, kappa in F.CELLS5:
        tl = W.true_lift_w3(kind, kappa, F.beta, F.gamma)
        for seed in range(s0, s1):
            if (kind, kappa, seed) in done: continue
            out.write(json.dumps(one(kind, kappa, seed, tl), default=float) + "\n"); out.flush()
        print("W5", kind, kappa, "true10 %+.4f" % tl, "elapsed", round(time.time() - T0), flush=True)
