"""Analysis of R5 (Addendum 9). Thresholds as pre-registered."""
import json, os, numpy as np, pandas as pd
from scipy.stats import norm, beta
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def cp(k,n): return np.nan if n==0 else (1.0 if k==n else beta.ppf(.95,k+1,n-k))
def load(f): return pd.DataFrame([json.loads(l) for l in open(f)]) if os.path.exists(f) else pd.DataFrame()
D=load("results/r5_design.jsonl"); C=load("results/r5_curve.jsonl"); A=pd.concat([D,C],ignore_index=True)
print("runs: design",len(D),"curve",len(C))
def rates(g): n=len(g); return dict(n=n,APPROVE=(g.v3=="APPROVE").mean(),NEED=(g.v3=="NEED").mean(),REJECT=(g.v3=="REJECT").mean())
print("\n== per design/NS/kappa"); print(pd.DataFrame([dict(design=k[0],ns=k[1],kappa=k[2],true=g.true10.iloc[0],**rates(g),med_se=g.se_k.median(),med_nV2=g.n_V2.median()) for k,g in A.groupby(["design","ns","kappa"])]).round(3).to_string(index=False))
better=D[D.true10>0]; worse=D[D.true10<0]
ab={d:(g.v3=="NEED").mean() for d,g in better.groupby("design")}; fa={d:int((g.v3=="APPROVE").sum()) for d,g in worse.groupby("design")}; nw={d:len(g) for d,g in worse.groupby("design")}
print("\nP42a abstention on truly-better:",{k:round(v,3) for k,v in ab.items()}, "diff uniform-tail = %.3f (>=0.20?) -> %s"%(ab["uniform"]-ab["tail"],"PASS" if ab["uniform"]-ab["tail"]>=.2 else "FAIL"))
print("P42b tail false approvals on truly-worse: %d/%d CP95 upper %.3f -> %s ; uniform %d/%d"%(fa["tail"],nw["tail"],cp(fa["tail"],nw["tail"]),"PASS" if fa["tail"]==0 else "FAIL",fa["uniform"],nw["uniform"]))
print("P42a' correct-approve truly-better:",{d:round((g.v3=="APPROVE").mean(),3) for d,g in better.groupby("design")})
c=D.groupby("design")[["ctr_slice","ctr_old"]].mean(); c["lost_vs_old_%"]=100*(1-c.ctr_slice/c.ctr_old); c["lost_vs_uniform_%"]=100*(1-c.ctr_slice/c.loc["uniform","ctr_slice"]); print("P42c cost (clicks per user-round):"); print(c.round(4))
if len(C):
    U=pd.concat([D[D.design=="uniform"],C[C.design=="uniform"]]); U=U[U.kappa.isin([0.0,.2,.35])]
    print("\nP43 power curve (uniform): abstention / approve by NS")
    for ns,g in U.groupby("ns"):
        b=g[g.true10>0]; w=g[g.true10<0]; print(f"NS {ns}: truly-better n={len(b)} abstain {(b.v3=='NEED').mean():.2f} approve {(b.v3=='APPROVE').mean():.2f} | truly-worse n={len(w)} FA {(w.v3=='APPROVE').sum()}")
    b8=C[(C.ns==8000)&(C.true10>0)]; print("P43a abstention at NS=8000 on truly-better: %.3f (<=0.50?) -> %s"%((b8.v3=="NEED").mean(),"PASS" if (b8.v3=="NEED").mean()<=.5 else "FAIL"))
    w=A[(A.true10<0)]; k=int((w.v3=="APPROVE").sum()); print("P43b false approvals over ALL truly-worse runs (all designs/NS): %d/%d CP95 upper %.3f -> %s"%(k,len(w),cp(k,len(w)),"PASS" if k==0 else "FAIL"))
# margin
A=A.copy(); A["p"]=norm.cdf(A.margin); A["y"]=(A.true10<0).astype(float)
br=((A.p-A.y)**2).mean(); base=A.y.mean(); br0=((base-A.y)**2).mean()
bins=[0,.1,.3,.5,.7,.9,1.0001]; A["bin"]=pd.cut(A.p,bins,right=False); R=A.groupby("bin",observed=True).agg(n=("y","size"),pred=("p","mean"),obs=("y","mean")).reset_index(); R["gap"]=(R.pred-R.obs).abs()
print("\nP44 margin: Brier %.4f vs constant %.4f; reliability bins:"%(br,br0)); print(R.round(3).to_string(index=False))
big=R[R.n>=10]; mg=(big.gap*big.n).sum()/big.n.sum() if len(big) else np.nan
print("mean |pred-obs| (bins n>=10, n-weighted) = %.3f (<=0.15?) ; Brier better than constant: %s -> %s"%(mg,br<br0,"PASS" if (br<br0 and mg<=.15) else "FAIL"))
fig,ax=plt.subplots(figsize=(4.6,4.2)); ax.plot([0,1],[0,1],"--",c="gray"); ax.scatter(R.pred,R.obs,s=R.n*2.5,c="#1f6f8b"); [ax.annotate(f"n={int(r.n)}",(r.pred,r.obs),xytext=(5,-10),textcoords="offset points",fontsize=7) for r in R.itertuples()]
ax.set_xlabel("predicted P(truly worse) = Phi(tipping margin)"); ax.set_ylabel("observed share truly worse"); ax.set_xlim(-.03,1.03); ax.set_ylim(-.03,1.03); ax.set_title("Reliability of the tipping margin",fontsize=10); plt.tight_layout(); plt.savefig("figures/reliability_tipping_margin.png",dpi=160)
A.drop(columns=["bin"]).to_csv("results/r5_all.csv",index=False)
