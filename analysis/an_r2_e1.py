import json, numpy as np, pandas as pd
pd.set_option("display.width",220)
df=pd.DataFrame([json.loads(l) for l in open("results/r2_e1.jsonl")])
E1=df[df.exp=="E1"].copy()
for c in ("pool","ri","fe"): E1[c+"_b"]=E1[c]-E1.kappa
g=E1.groupby(["m","kappa","ns"]).agg(n=("seed","count"),pool_bias=("pool_b","mean"),pool_sd=("pool","std"),ri_bias=("ri_b","mean"),ri_sd=("ri","std"),fe_bias=("fe_b","mean"),fe_sd=("fe","std"),nd=("nd","mean"))
print(g.round(3).to_string())
a=g.loc[(2.0,0.8,3000)]
print("P20 pool bias m2 k.8 n3000: %.3f (<=-0.05?) ; monotone in m at k=.8,n=3000:"%a.pool_bias,[round(g.loc[(m,0.8,3000)].pool_bias,3) for m in (1.0,2.0,3.0)])
print("P21 fe |bias|<=.03 at n=3000 all cells:",g.xs(3000,level="ns").fe_bias.abs().max().round(3))
print("P22 fe SD<=.10 at n=3000:",g.xs(3000,level="ns").fe_sd.max().round(3))
print("P23 ri reduces |bias| >=50%% at m2 k.8 n3000: pool %.3f ri %.3f -> %.0f%% reduction"%(a.pool_bias,a.ri_bias,100*(1-abs(a.ri_bias)/abs(a.pool_bias))))
E2=df[df.exp=="E2"].copy(); E2["last_b"]=E2["last"]-E2.kappa; E2["every_b"]=E2.every-E2.kappa; E2["fe_b"]=E2.fe_on_lastworld-E2.kappa
g2=E2.groupby(["kappa","ns"]).agg(n=("seed","count"),last_bias=("last_b","mean"),last_sd=("last","std"),every_bias=("every_b","mean"),every_sd=("every","std"),fe_lastworld_bias=("fe_b","mean"))
print(g2.round(3).to_string())
for k in (0.4,0.8):
    r=g2.loc[(k,1500)]; print("P24 k",k,"last bias %.3f every bias %.3f ratio %.1f"%(r.last_bias,r.every_bias,abs(r.last_bias)/max(abs(r.every_bias),1e-9)))
