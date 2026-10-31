"""POST-HOC, exploratory (NOT pre-registered): does an APPROVE margin m (lower ends > m instead of > 0) remove the R4-1 near-tie false approvals? Uses stored interval ends in out/r4_e1.jsonl."""
import json, numpy as np, pandas as pd
from analysis.an_percell import cp, cls
df=pd.DataFrame([json.loads(l) for l in open("results/round-04/r4_e1.jsonl")]); df["cls"]=cls(df.true10.values)
SH=("lin","log","mem7","tail2")
def appr(r,m): return (r.s_lo>m) and all(r[f"{s}_lo"]>m for s in SH)
w=df[df.cls=="worse"]; b=df[df.cls=="better"]; strong=b[b.true10>=0.02]
print("cell-level v4 false approval (m=0):"); print(w.groupby(["kind","kappa"]).apply(lambda g:(g.v4=="APPROVE").sum()).to_string())
print("\nmargin m | FA/144 (CP95 upper) | correct-approve all truly-better | correct-approve lift>=+0.02")
for m in (0,.001,.002,.003,.005):
    fa=sum(appr(r,m) for _,r in w.iterrows()); ca=np.mean([appr(r,m) for _,r in b.iterrows()]); cs=np.mean([appr(r,m) for _,r in strong.iterrows()])
    print(f"{m:.3f} | {fa}/{len(w)} ({cp(fa,len(w)):.3f}) | {ca:.3f} | {cs:.3f}")
