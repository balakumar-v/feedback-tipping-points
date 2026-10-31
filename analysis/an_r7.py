"""R7 analysis (Addendum 11): out-of-family FA, logs-only linear under final four-shape rule, slice audit under four shapes."""
import json, glob, numpy as np, pandas as pd
from scipy.stats import beta
def cp(k,n): return np.nan if n==0 else (1.0 if k==n else beta.ppf(.95,k+1,n-k))
def cp2(k,n): return (beta.ppf(.025,k,n-k+1) if k>0 else 0.0, beta.ppf(.975,k+1,n-k) if k<n else 1.0)
def load(pat): return pd.DataFrame([json.loads(l) for f in sorted(glob.glob(pat)) for l in open(f)])
def cls(t): return np.where(t<-0.002,"worse",np.where(t>0.002,"better","marg"))
def cell(df,vcol):
    rows=[]
    for k,g in df.groupby(["kind","kappa"] if "kind" in df else ["kappa"],sort=False):
        n=len(g); rows.append(dict(cell=k,n=n,true=round(g.true10.iloc[0],4),cls=cls(g.true10.values)[0],A=(g[vcol]=="APPROVE").sum(),N=(g[vcol]=="NEED").sum(),R=(g[vcol]=="REJECT").sum()))
    return pd.DataFrame(rows)
def fa(df,vcol,mask=None):
    w=df[cls(df.true10.values)=="worse"]
    if mask is not None: w=w[mask(w)]
    k=(w[vcol]=="APPROVE").sum(); return k,len(w)
if __name__=="__main__":
    print("== R7-1 out-of-family, logs only (fresh seeds 1000-1031)")
    d=load("results/round-07/r7_e1_*.jsonl"); print(cell(d,"v4").to_string(index=False))
    for v in ("v4","v3"):
        k,n=fa(d,v); print(f"P45a {v}: FA {k}/{n} CP95 upper {cp(k,n):.4f}")
    old=pd.DataFrame([json.loads(l) for l in open("results/round-03/r3_e3.jsonl")]); old=old[old.kind.isin(["convex","quad"])]
    ko,no=fa(old,"v4"); kn,nn=fa(d,"v4"); print(f"earlier R3-3 real v4: FA {ko}/{no}; pooled {ko+kn}/{no+nn} CP95 upper {cp(ko+kn,no+nn):.4f}  (P45b <= 0.05)")
    kq,nq=fa(d,"v4",lambda w:(w.kind=="quad")&(w.kappa==.2)); print("quad .2 cell v4 FA",kq,"/",nq)
    print("\n== R7-2 linear fatigue, logs only, 20/cell")
    d=load("results/round-07/r7_e2_*.jsonl"); print("v4"); print(cell(d,"v4").to_string(index=False)); print("v3"); print(cell(d,"v3").to_string(index=False))
    k,n=fa(d,"v4"); print(f"P46b v4 FA {k}/{n} CP95 upper {cp(k,n):.4f}")
    for kap in (.2,.4):
        g=d[d.kappa==kap]; print(f"kappa {kap}: v4 correct-approve {(g.v4=='APPROVE').sum()}/{len(g)}  v3 {(g.v3=='APPROVE').sum()}/{len(g)}  false-reject v4 {(g.v4=='REJECT').sum()}")
    print("\n== R7-3 slice audit (taste x1, NS 3000, 16/cell)")
    d=load("results/round-07/r7_e3_*.jsonl"); d["kind"]="lin"
    print("v4"); print(cell(d,"v4").to_string(index=False)); print("v3 same runs"); print(cell(d,"v3").to_string(index=False))
    for v in ("v4","v3"):
        k,n=fa(d,v); kb,nb=fa(d,v,lambda w:abs(w.true10)<=0.01)
        b=d[cls(d.true10.values)=="better"]; s=b[b.true10>0.03]
        print(f"{v}: FA {k}/{n} CP95 upper {cp(k,n):.4f} | near-boundary FA {kb}/{nb} upper {cp(kb,nb):.4f} | truly-better n={len(b)} FR {(b[v]=='REJECT').sum()} abstain {(b[v]=='NEED').mean():.3f} correct-approve {(b[v]=='APPROVE').sum()}/{len(b)} | strong-better (k0) {(s[v]=='APPROVE').sum()}/{len(s)}")
    # pooled slice correct-approve at kappa 0, taste x1, NS 3000, uniform, v3 across seed sets
    e5=pd.DataFrame([json.loads(l) for l in open("results/round-02/r2_e5.jsonl")]); e5=e5[(e5.m==1.0)&(e5.kappa==0.0)]
    r5=pd.DataFrame([json.loads(l) for l in open("results/round-05/r5_design.jsonl")]); r5=r5[(r5.design=="uniform")&(r5.kappa==0.0)]
    r6=pd.DataFrame([json.loads(l) for l in open("results/round-06/r6.jsonl")]); r6=r6[(r6.kappa==0.0)&(r6.ns==3000)]
    a=[(e5.v3=="APPROVE").sum(),(r5.v3=="APPROVE").sum(),(r6.v3=="APPROVE").sum(),(d[d.kappa==0].v3=="APPROVE").sum()]
    n=[len(e5),len(r5),len(r6),len(d[d.kappa==0])]
    print("kappa0 v3 correct-approve by seed set (R2-5, R5, R6, R7-3):",list(zip(a,n)),"pooled",sum(a),"/",sum(n),"=%.3f"%(sum(a)/sum(n)),"CP95 two-sided",np.round(cp2(sum(a),sum(n)),3))
    print("\n== R7-4 slice audit at the 8,000 cap (taste x1, 16/cell)")
    d=load("results/round-07/r7_e4_*.jsonl"); d["kind"]="lin"
    print("v4"); print(cell(d,"v4").to_string(index=False)); print("v3 same runs"); print(cell(d,"v3").to_string(index=False))
    for v in ("v4","v3"):
        b=d[cls(d.true10.values)=="better"]; s=b[b.true10>0.03]
        print(f"{v}: truly-better n={len(b)} abstain {(b[v]=='NEED').mean():.3f} correct-approve {(b[v]=='APPROVE').sum()}/{len(b)} false reject {(b[v]=='REJECT').sum()} | kappa0 approve {(s[v]=='APPROVE').sum()}/{len(s)}")
