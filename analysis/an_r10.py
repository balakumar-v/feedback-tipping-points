import json, numpy as np, pandas as pd
d = pd.DataFrame([json.loads(l) for l in open("results/round-10/r10_e1.jsonl")]); Z = 2.8
d["orc"] = d.groupby("kappa").sd_f.transform("mean").pipe(lambda s: (Z * s / d.true10.abs()) ** 2)
d["in_band"] = (d.orc >= d.n_lo) & (d.orc <= d.n_hi); d["pt_ok"] = (d.n_pt / d.orc).between(.5, 2)
g = d.groupby("kappa").agg(n=("seed", "size"), true10=("true10", "first"), oracle=("orc", "first"), med_pt=("n_pt", "median"), med_lo=("n_lo", "median"), inf_hi=("n_hi", lambda x: np.isinf(x).mean()), in_band=("in_band", "mean"), pt_within2=("pt_ok", "mean"))
print(g.round(3).to_string()); print("P52a band coverage", round(d.in_band.mean(), 3), "| P52b point within 2x", round(d.pt_ok.mean(), 3))
a = d[d.n_hi <= 8000]; print("P52c affordable-declared", len(a), "oracle<=cap", (a.orc <= 8000).mean() if len(a) else None)
