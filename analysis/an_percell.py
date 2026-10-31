"""Per-kappa-cell verdict table on REAL round-2 logs (analysis only, no new runs; POST-HOC, not pre-registered).
Columns: n runs, true 10-round lift, class, APPROVE/NEED/REJECT rates, false-approval (truly worse), false-reject (truly better).
Also: near-boundary stratum (|true lift| <= 0.01 and truly worse) pooled Clopper-Pearson bound."""
import json, numpy as np, pandas as pd
from scipy.stats import beta
def cp(k,n): return np.nan if n==0 else (1.0 if k==n else beta.ppf(.95,k+1,n-k))
def cls(t): return np.where(t<-0.002,"worse",np.where(t>0.002,"better","marg"))
def table(df,keys,vcol="v3"):
    df=df.copy(); df["cls"]=cls(df.true10.values); rows=[]
    for k,g in df.groupby(keys,sort=False):
        n=len(g); a=(g[vcol]=="APPROVE").sum(); nd=(g[vcol]=="NEED").sum(); r=(g[vcol]=="REJECT").sum(); c=g.cls.iloc[0]
        rows.append(dict(cell=k if isinstance(k,str) else "/".join(map(str,k)),n=n,true=g.true10.iloc[0],cls=c,A=a/n,N=nd/n,R=r/n,
                         FA=(a if c=="worse" else np.nan),FR=(r if c=="better" else np.nan),abstain=nd/n))
    return pd.DataFrame(rows)
def summ(df,name,vcol="v3",edge=0.01):
    df=df.copy(); df["cls"]=cls(df.true10.values); w=df[df.cls=="worse"]; b=df[df.cls=="better"]
    wn=w[abs(w.true10)<=edge]; bn=b[abs(b.true10)<=edge]
    fa=(w[vcol]=="APPROVE").sum(); fan=(wn[vcol]=="APPROVE").sum(); fr=(b[vcol]=="REJECT").sum(); frn=(bn[vcol]=="REJECT").sum()
    print(f"[{name}] truly-worse n={len(w)} FA={fa} CP95upper={cp(fa,len(w)):.3f} | near-boundary worse (|lift|<={edge}) n={len(wn)} FA={fan} CP95upper={cp(fan,len(wn)):.3f}")
    print(f"[{name}] truly-better n={len(b)} FR={fr} ({fr/max(len(b),1):.3f}) CP95upper={cp(fr,len(b)):.3f} | near-boundary better n={len(bn)} FR={frn} | abstain overall {(df[vcol]=='NEED').mean():.3f}; abstain on truly-better {(b[vcol]=='NEED').mean():.3f}; correct-approve {(b[vcol]=='APPROVE').mean():.3f}")
if __name__=="__main__":
    e3=pd.DataFrame([json.loads(l) for f in ("results/round-02/r2_e3_a.jsonl","results/round-02/r2_e3_b.jsonl") for l in open(f)])
    print("== R2-3 logs only (REAL world), three-shape rule v3; seeds per cell:",e3.groupby(["kind","kappa"]).size().unique())
    t=table(e3,["kind","kappa"]); print(t.round(3).to_string(index=False)); summ(e3,"R2-3 v3"); summ(e3,"R2-3 linear-only","v1") if "v1" in e3 else None
    e5=pd.DataFrame([json.loads(l) for l in open("results/round-02/r2_e5.jsonl")]); print("\n== R2-5 slice audit (REAL), seeds:",sorted(e5.seed.unique())[:3],"..",len(e5))
    for m,g in e5.groupby("m"):
        print("--- taste x%g"%m); print(table(g,["kappa"]).round(3).to_string(index=False)); summ(g,"R2-5 m=%g"%m)
    summ(e5,"R2-5 all m"); summ(e5[e5.m==1.0],"R2-5 m=1")
