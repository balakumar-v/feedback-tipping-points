"""R8-2 held-out generator W3 (step/expo/late truths, per-item kappa, taste x fatigue coupling), SLICE audit at 3,000 users (MODE: uniform or tail), taste x1, final four-shape rule.
The rule is frozen (= r7_e3 / r3_e1.audit with four shapes). usage: python -m experiments.r8_e2 S0 S1 OUT"""
import sys, json, os, time, numpy as np
from p3ope import r2_lib as R
from p3ope import r8_lib as W
from experiments import r3_e1 as X
from experiments.r2_e5 import comb
X.SH = ("lin", "log", "mem7", "tail2"); beta, gamma = .5, .8; NS = 3000; MODE = os.environ.get("P3_SLICE", "slice")
CELLS = [c for c in [("step", .3), ("step", 1.2), ("step", 1.6), ("step", 2.0), ("expo", .04), ("expo", .15), ("expo", .2), ("expo", .4),
         ("late", .3), ("late", .8), ("late", 1.2), ("late", 2.0)] if os.environ.get("P3_CELLS","all")=="all" or c[0] in os.environ["P3_CELLS"].split(",")]
def one(kind, kappa, seed, tl):
    cid = sum(map(ord, f"{kind}{kappa}"))
    db = W.sim_w3(X.NB, np.random.default_rng([seed, cid, 211]), kind, kappa, beta, gamma, "old")
    ds = W.sim_w3(NS, np.random.default_rng([seed, cid, NS, 212]), kind, kappa, beta, gamma, MODE)
    res, obs = X.audit(db, ds, beta)
    rec = dict(kind=kind, kappa=kappa, seed=seed, true10=tl, lin_k=res["lin"]["k"], v4=comb([res[s]["v"] for s in X.SH]))
    for s in X.SH: rec[f"{s}_v"] = res[s]["v"]; rec[f"{s}_spt"] = float(res[s]["spt"]); rec[f"{s}_fpt"] = float(res[s]["pt"])
    return rec
if __name__ == "__main__":
    s0, s1, f = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; done = set()
    if os.path.exists(f): done = {(r["kind"], r["kappa"], r["seed"]) for r in map(json.loads, open(f))}
    out = open(f, "a"); T0 = time.time()
    for kind, kappa in CELLS:
        tl = W.true_lift_w3(kind, kappa, beta, gamma)
        for seed in range(s0, s1):
            if (kind, kappa, seed) in done: continue
            out.write(json.dumps(one(kind, kappa, seed, tl), default=float) + "\n"); out.flush()
        print(kind, kappa, "true10 %+.4f" % tl, "elapsed", round(time.time() - T0), flush=True)
