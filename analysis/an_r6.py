import json, numpy as np, pandas as pd
df=pd.DataFrame([json.loads(l) for l in open("results/r6.jsonl")]); SH=("lin","log","mem7")
df["static_bound"]=df.lin_slo<=0   # static interval identical across shapes
df["fc_bound"]=df[[f"{s}_flo" for s in SH]].min(axis=1)<=0
print("runs",len(df)); print(df.groupby(["kappa","ns"]).agg(n=("seed","size"),APPROVE=("v3",lambda x:(x=="APPROVE").sum()),NEED=("v3",lambda x:(x=="NEED").sum()),REJECT=("v3",lambda x:(x=="REJECT").sum()),static_lo_le0=("static_bound","mean"),fc_lo_le0=("fc_bound","mean"),sd_static=("lin_sds","median"),sd_fc_lin=("lin_sdf","median"),sd_fc_log=("log_sdf","median"),sd_fc_mem7=("mem7_sdf","median"),spt=("lin_spt","median"),fpt=("lin_fpt","median")).round(4).to_string())
N=df[df.v3=="NEED"]; print("\nNEED runs",len(N))
h1=N.static_bound.mean(); h2=N.fc_bound.mean(); print("H1 static lower end <=0 in %.3f of NEED runs (>=0.70?) -> %s"%(h1,"PASS" if h1>=.7 else "FAIL"))
print("H2 any-shape forecast lower end <=0 in %.3f of NEED runs (<=0.50?) -> %s"%(h2,"PASS" if h2<=.5 else "FAIL"))
print("both bind %.3f | static only %.3f | forecast only %.3f | neither (shape disagreement?) %.3f"%((N.static_bound&N.fc_bound).mean(),(N.static_bound&~N.fc_bound).mean(),(~N.static_bound&N.fc_bound).mean(),(~N.static_bound&~N.fc_bound).mean()))
for k,g in N.groupby("kappa"): print("kappa",k,"NEED",len(g),"static binds %.2f forecast binds %.2f"%(g.static_bound.mean(),g.fc_bound.mean()))
print("static SD / forecast SD (lin) median ratio: %.2f"%(df.lin_sds/df.lin_sdf).median())
