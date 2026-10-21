"""Analysis of R4-1 (W2 generator) and R4-2 (slice near boundary). Thresholds = Addendum 6."""
import json, numpy as np, pandas as pd, sys
from analysis.an_percell import cp, cls, table, summ
def load(f): return pd.DataFrame([json.loads(l) for l in open(f)])
def r41():
    df=load("results/r4_e1.jsonl"); df["cls"]=cls(df.true10.values); print("R4-1 W2 runs",len(df),"seeds/cell",df.groupby(["kind","kappa"]).size().unique())
    print(table(df,["kind","kappa"],"v4").round(3).to_string(index=False))
    for v in ("v4","v3","lin_v"): summ(df,"R4-1 "+v,v)
    w=df[df.cls=="worse"]; b=df[df.cls=="better"]; ws=w[abs(w.true10)<=0.01]; strong=b[b.true10>=0.02]
    fa=(w.v4=="APPROVE").sum(); fan=(ws.v4=="APPROVE").sum(); fr=(b.v4=="REJECT").sum(); ab=(b.v4=="NEED").mean(); ca=(strong.v4=="APPROVE").mean()
    print("P39a pooled FA %d/%d CP95 upper %.3f (<=0.05?) -> %s"%(fa,len(w),cp(fa,len(w)),"PASS" if cp(fa,len(w))<=.05 and len(w)>=59 else "FAIL"))
    print("P39b near-boundary FA %d/%d CP95 upper %.3f (<=0.10?) -> %s"%(fan,len(ws),cp(fan,len(ws)),"PASS" if cp(fan,len(ws))<=.10 else "FAIL"))
    print("P39c FR %d/%d=%.3f (<=0.10) abstain on truly-better %.3f (<=0.50) -> %s"%(fr,len(b),fr/len(b),ab,"PASS" if fr/len(b)<=.10 and ab<=.5 else "FAIL"))
    print("P39d correct-approve (lift>=+0.02) %.3f n=%d (>=0.50) -> %s"%(ca,len(strong),"PASS" if ca>=.5 else "FAIL"))
    oof=df[df.kind.isin(["convex","quad"])&(df.cls=="worse")]
    print("descriptive out-of-family truly-worse n=%d: FA v4 %d, v3 %d, lin-only %d"%(len(oof),(oof.v4=="APPROVE").sum(),(oof.v3=="APPROVE").sum(),(oof.lin_v=="APPROVE").sum()))
def r42():
    df=load("results/r4_e2.jsonl"); df["cls"]=cls(df.true10.values); print("\nR4-2 slice runs",len(df),"seeds/cell",df.groupby("kappa").size().unique())
    print(table(df,["kappa"]).round(3).to_string(index=False)); summ(df,"R4-2 v3")
    w=df[df.cls=="worse"]; b=df[df.cls=="better"]; ws=w[abs(w.true10)<=0.01]
    fa=(w.v3=="APPROVE").sum(); fan=(ws.v3=="APPROVE").sum(); fr=(b.v3=="REJECT").sum()
    print("P40a all-worse FA %d/%d ; near-boundary %d/%d CP95 upper %.3f (<=0.10?) -> %s"%(fa,len(w),fan,len(ws),cp(fan,len(ws)),"PASS" if fa==0 and cp(fan,len(ws))<=.10 else "FAIL"))
    print("P40b FR %d/%d=%.3f (<=0.10) -> %s"%(fr,len(b),fr/max(len(b),1),"PASS" if fr/max(len(b),1)<=.10 else "FAIL"))
    nb=df[abs(df.true10)<=0.01]; print("descriptive abstain truly-better %.3f ; near-boundary runs n=%d abstain %.3f"%((b.v3=="NEED").mean(),len(nb),(nb.v3=="NEED").mean()))
if __name__=="__main__":
    r41()
    import os
    if os.path.exists("results/r4_e2.jsonl"): r42()
