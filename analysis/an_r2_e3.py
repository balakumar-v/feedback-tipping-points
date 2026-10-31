import json, numpy as np, pandas as pd
from scipy.stats import beta
def cp(k,n): return 1.0 if k==n else beta.ppf(.95,k+1,n-k)
pd.set_option("display.width",220)
df=pd.DataFrame([json.loads(l) for f in ("results/round-02/r2_e3_a.jsonl","results/round-02/r2_e3_b.jsonl") for l in open(f)])
df["cls"]=np.where(df.true10<-0.002,"worse",np.where(df.true10>0.002,"better","marg"))
g=df.groupby(["kind","kappa"],sort=False).agg(n=("seed","count"),true10=("true10","first"),true6=("true6","first"),cls=("cls","first"),A3=("v3",lambda x:(x=="APPROVE").mean()),N3=("v3",lambda x:(x=="NEED").mean()),R3=("v3",lambda x:(x=="REJECT").mean()),A1=("v1",lambda x:(x=="APPROVE").mean()),N1=("v1",lambda x:(x=="NEED").mean()),R1=("v1",lambda x:(x=="REJECT").mean()))
print(g.round(3).to_string())
w=df[df.cls=="worse"]; b=df[df.cls=="better"]
for nm,vk in (("three-shape v3","v3"),("linear-only v1","v1")):
    fa=(w[vk]=="APPROVE").sum(); print(nm,"worse n=%d FA=%d CP95 upper %.3f"%(len(w),fa,cp(fa,len(w))),"| better n=%d correct-approve %.3f false-reject %.3f NEED %.3f"%(len(b),(b[vk]=="APPROVE").mean(),(b[vk]=="REJECT").mean(),(b[vk]=="NEED").mean()))
    wc=w[w.kind!="convex"]; fa=(wc[vk]=="APPROVE").sum(); print("   excluding convex: worse n=%d FA=%d"%(len(wc),fa))
    wx=w[w.kind=="convex"]; print("   convex worse n=%d FA=%d"%(len(wx),(wx[vk]=="APPROVE").sum()))
x=df[(df.kind=="sat")&(df.kappa==0.9)]; print("P29 sat .9 truth",x.true10.iloc[0],"v3 R/N/A",(x.v3=="REJECT").mean(),(x.v3=="NEED").mean(),(x.v3=="APPROVE").mean(),"v1 R",(x.v1=="REJECT").mean())
# false rejects by rule
for nm,vk in (("v3","v3"),("v1","v1")): print(nm,"false-reject among truly-better",(b[vk]=="REJECT").sum(),"/",len(b))
# horizon-6 vs 10 truth sign disagreement
dd=df.groupby(["kind","kappa"]).agg(t6=("true6","first"),t10=("true10","first")); print("cells where sign(true6)!=sign(true10):",dd[(dd.t6>0)!=(dd.t10>0)].round(4).to_dict("index"))
# forecast H6 vs H10 point error lin shape
df["e10"]=df.lin_pt-df.true10; df["e6"]=df.lin_pt6-df.true6
print("lin-shape forecast median |err| H10 %.4f H6 %.4f"%(df.e10.abs().median(),df.e6.abs().median()))
