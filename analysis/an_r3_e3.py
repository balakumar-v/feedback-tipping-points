import json, numpy as np, pandas as pd
from scipy.stats import beta
def cp(k,n): return 1.0 if k==n else beta.ppf(.95,k+1,n-k)
df=pd.DataFrame([json.loads(l) for l in open("results/r3_e3.jsonl")]); df["cls"]=np.where(df.true10<-0.002,"worse",np.where(df.true10>0.002,"better","marg"))
g=df.groupby(["kind","kappa"],sort=False).agg(n=("seed","count"),true=("true10","first"),cls=("cls","first"),v3A=("v3",lambda x:(x=="APPROVE").mean()),v3N=("v3",lambda x:(x=="NEED").mean()),v3R=("v3",lambda x:(x=="REJECT").mean()),v4A=("v4",lambda x:(x=="APPROVE").mean()),v4N=("v4",lambda x:(x=="NEED").mean()),v4R=("v4",lambda x:(x=="REJECT").mean()),linA=("lin_v",lambda x:(x=="APPROVE").mean()))
print(g.round(3).to_string())
for nm,sub in (("out-of-family (convex+quad)",df[df.kind.isin(["convex","quad"])]),("in-family lin",df[df.kind=="lin"]),("all",df)):
    w=sub[sub.cls=="worse"]; b=sub[sub.cls=="better"]
    for vk in ("v3","v4"):
        fa=(w[vk]=="APPROVE").sum(); print(nm,vk,"worse n=%d FA=%d CP95 upper %.3f"%(len(w),fa,cp(fa,len(w))),"| better n=%d approve %.3f need %.3f reject %.3f"%(len(b),(b[vk]=="APPROVE").mean() if len(b) else np.nan,(b[vk]=="NEED").mean() if len(b) else np.nan,(b[vk]=="REJECT").mean() if len(b) else np.nan))
    fl=(w["lin_v"]=="APPROVE").sum(); print(nm,"lin-only worse FA",fl,"/",len(w))
