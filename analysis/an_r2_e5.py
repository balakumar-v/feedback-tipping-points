import json, numpy as np, pandas as pd, sys
from scipy.stats import beta
def cp(k,n): return 1.0 if k==n else beta.ppf(.95,k+1,n-k)
df=pd.DataFrame([json.loads(l) for l in open("results/round-02/r2_e5.jsonl")]); df["cls"]=np.where(df.true10<-0.002,"worse",np.where(df.true10>0.002,"better","marg"))
g=df.groupby(["m","kappa"]).agg(n=("seed","count"),true=("true10","first"),cls=("cls","first"),v3A=("v3",lambda x:(x=="APPROVE").mean()),v3R=("v3",lambda x:(x=="REJECT").mean()),v3N=("v3",lambda x:(x=="NEED").mean()),v1A=("v1",lambda x:(x=="APPROVE").mean()),v1R=("v1",lambda x:(x=="REJECT").mean()),fc=("lin_pt","mean"))
print(g.round(3).to_string())
w=df[df.cls=="worse"]; b=df[df.cls=="better"]; bb=b[b.true10>=0.02]
for nm,vk in (("v3 (three-shape)","v3"),("v1 (linear-only)","v1")):
    fa=(w[vk]=="APPROVE").sum(); print(nm,"worse n=%d FA=%d CP95 upper %.3f"%(len(w),fa,cp(fa,len(w))),"| better n=%d correct-approve %.2f false-reject %.2f NEED %.2f | strong-better(>=.02) n=%d correct-approve %.2f"%(len(b),(b[vk]=="APPROVE").mean(),(b[vk]=="REJECT").mean(),(b[vk]=="NEED").mean(),len(bb),(bb[vk]=="APPROVE").mean()))
for m in sorted(df.m.unique()):
    x=w[w.m==m]; print("m",m,"worse n",len(x),"FA v3",(x.v3=="APPROVE").sum(),"FA v1",(x.v1=="APPROVE").sum(),"REJ v3 %.2f"%(x.v3=="REJECT").mean())
