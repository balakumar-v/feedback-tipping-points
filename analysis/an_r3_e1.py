import json, numpy as np, pandas as pd
from scipy.stats import beta
def cp(k,n): return 1.0 if k==n else beta.ppf(.95,k+1,n-k)
df=pd.DataFrame([json.loads(l) for l in open("results/round-03/r3_e1.jsonl")]); df["cls"]=np.where(df.true10<-0.002,"worse",np.where(df.true10>0.002,"better","marg"))
print("pilots",len(df)); print(df.groupby("kappa").agg(n=("seed","count"),true=("true10","first"),A=("pilot",lambda x:(x=="APPROVE").sum()),N=("pilot",lambda x:(x=="NEED").sum()),R=("pilot",lambda x:(x=="REJECT").sum())).round(4))
nd=df[df.pilot=="NEED"].copy(); print("NEED pilots",len(nd))
for v in ("V0","V1","V2"):
    a=nd[f"after_{v}"]; unc=nd[a!="CAPPED"]; au=unc[f"after_{v}"]
    print(v,"median n* %.0f"%nd[f"n_{v}"].median(),"| share n*<=cap %.2f (%d/%d)"%(len(unc)/len(nd),len(unc),len(nd)),"| decisive among uncapped %.2f (%d/%d)"%((au!="NEED").mean() if len(unc) else np.nan,(au!="NEED").sum(),len(unc)),"| decisive overall (capped=abstain) %.2f"%((a.isin(["APPROVE","REJECT"])).mean()))
# false approvals / false rejects across pilot + after
fa_p=((df.pilot=="APPROVE")&(df.cls=="worse")).sum()
print("pilot false approvals",fa_p,"of truly-worse pilots",(df.cls=="worse").sum())
for v in ("V0","V1","V2"):
    a=nd[f"after_{v}"]; w=nd[nd.cls=="worse"]; b=nd[nd.cls=="better"]
    print(v,"FA after:",(w[f"after_{v}"]=="APPROVE").sum(),"/",(w[f"after_{v}"]!="CAPPED").sum(),"uncapped truly-worse | false reject after:",(b[f"after_{v}"]=="REJECT").sum(),"/",(b[f"after_{v}"]!="CAPPED").sum(),"uncapped truly-better; correct-approve after",(b[f"after_{v}"]=="APPROVE").sum())
print(nd.groupby("kappa").agg(n=("seed","count"),n0=("n_V0","median"),n1=("n_V1","median"),n2=("n_V2","median"),kstar=("kstar","mean")).round(0))
print(nd.groupby("kappa")[["after_V0","after_V1","after_V2"]].agg(lambda x:x.value_counts().to_dict()).to_string())
