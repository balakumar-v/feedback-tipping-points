"""R15-2: re-run 48 R14 audits (seeds 10000-10003 x 12 cells) with a larger bootstrap. usage: python -m experiments.r15_e2 B OUT"""
import sys, json, os, time, numpy as np, glob
from experiments import r14_e1 as E14
from p3ope import r8_lib as W

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit("usage: python -m experiments.r15_e2 B OUT")
    E14.B = int(sys.argv[1]); f = sys.argv[2]
    truth = {(r["kind"], r["kappa"]): r["true10"] for fn in glob.glob("results/round-14/r14_e1_*.jsonl") for r in map(json.loads, open(fn))}
    done = set()
    if os.path.exists(f): done = {(r["kind"], r["kappa"], r["seed"]) for r in map(json.loads, open(f))}
    out = open(f, "a"); T0 = time.time()
    for seed in range(10000, 10004):
        for kind, kappa in E14.CELLS6:
            if (kind, kappa, seed) in done: continue
            rec = E14.one(kind, kappa, seed, truth[(kind, kappa)]); rec["B"] = E14.B
            out.write(json.dumps(rec, default=float) + "\n"); out.flush()
        print("seed", seed, "elapsed", round(time.time() - T0), flush=True)
