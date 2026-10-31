"""R8 analysis: P49a-b (logs-only under taste), P50a-c (held-out W3 slice audit). python -m analysis.an_r8"""
import json, glob, numpy as np, pandas as pd
from scipy.stats import beta as Be
def cp_up(x, n): return 1.0 if x >= n else float(Be.ppf(0.95, x + 1, n - x))
def load(p): return pd.DataFrame([json.loads(l) for f in sorted(glob.glob(p)) for l in open(f)])
def cls(t): return "worse" if t < -0.002 else ("better" if t > 0.002 else "marg")
def table(df, keys):
    df = df.assign(cls=df.true10.map(cls)); g = df.groupby(keys + ["true10", "cls"]).v4.value_counts().unstack(fill_value=0)
    for c in ("APPROVE", "NEED", "REJECT"):
        if c not in g: g[c] = 0
    g["n"] = g[["APPROVE", "NEED", "REJECT"]].sum(1); print(g[["n", "APPROVE", "NEED", "REJECT"]].round(4).to_string())
e1 = load("results/round-08/r8_e1.jsonl")
if len(e1):
    print("== R8-1 logs-only UNDER hidden taste, v4 (16/cell)"); table(e1, ["m", "kappa"])
    e1["cls"] = e1.true10.map(cls)
    for m in (1.0, 2.0):
        x = e1[e1.m == m]; w = x[x.cls == "worse"]; b = x[x.cls == "better"]
        fa = int((w.v4 == "APPROVE").sum()); print(f"taste x{m:g}: v4 FA {fa}/{len(w)} CP95 upper {cp_up(fa, len(w)):.3f} | truly-better n={len(b)} v4 approve {(b.v4=='APPROVE').sum()} reject {(b.v4=='REJECT').sum()} | mean one-step {x.s_pt.mean():+.3f}")
    b = e1[e1.cls == "better"]; fr = int((b.v4 == "REJECT").sum())
    print(f"P49b v5 false rejects (taste x1+x2 pooled): {fr}/{len(b)} = {fr/max(len(b),1):.3f}")
    w1 = e1[(e1.m == 1.0) & (e1.cls == "worse")]; fa = int((w1.v4 == "APPROVE").sum())
    print(f"P49a v4 FA at taste x1: {fa}/{len(w1)} upper {cp_up(fa, len(w1)):.3f}  ->", "PASS" if cp_up(fa, len(w1)) <= .05 else "FAIL")
e2 = load("results/round-08/r8_e2.jsonl")
if len(e2):
    print("\n== R8-2 held-out W3 slice audit, taste x1, 3,000 users (16/cell)"); table(e2, ["kind", "kappa"])
    e2["cls"] = e2.true10.map(cls); w = e2[e2.cls == "worse"]; nb = w[w.true10.abs() <= 0.01]; b = e2[e2.cls == "better"]
    fa = int((w.v4 == "APPROVE").sum()); fan = int((nb.v4 == "APPROVE").sum()); fr = int((b.v4 == "REJECT").sum())
    print(f"P50a FA {fa}/{len(w)} CP95 upper {cp_up(fa,len(w)):.3f} ->", "PASS" if cp_up(fa, len(w)) <= .05 else "FAIL")
    print(f"P50b near-boundary FA {fan}/{len(nb)} upper {cp_up(fan,len(nb)):.3f} ->", "PASS" if cp_up(fan, len(nb)) <= .10 else "FAIL")
    print(f"P50c false rejects {fr}/{len(b)} = {fr/max(len(b),1):.3f} ->", "PASS" if fr / max(len(b), 1) <= .10 else "FAIL")
    print(f"descriptive: truly-better abstain {(b.v4=='NEED').mean():.3f} correct-approve {(b.v4=='APPROVE').sum()}/{len(b)}")
    print("per-shape FA:", {k: f"{int((g.v4=='APPROVE').sum())}/{len(g)}" for k, g in w.groupby("kind")})
