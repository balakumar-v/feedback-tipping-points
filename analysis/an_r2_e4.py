import json, numpy as np, pandas as pd
pd.set_option("display.width",220)
df=pd.DataFrame([json.loads(l) for l in open("results/round-02/r2_e4.jsonl")])
df["ka_b"]=df.k_a-df.kappa; df["kb_b"]=df.k_b-df.kappa
print(df.groupby(["kappa","delta"]).agg(n=("seed","count"),ka_bias=("ka_b","mean"),kb_bias=("kb_b","mean"),theta=("theta","mean"),t6=("t6","first"),t10=("t10","first")).round(3).to_string())
for v in ("a","bflat","blin"):
    for H,tc in ((6,"t6"),(10,"t10")):
        e=df[f"{v}_H{H}"]-df[tc]; nm=df[df[tc].abs()>0.002]
        print(v,"H",H,"median|err| %.4f"%e.abs().median(),"sign-correct (non-marginal) %.3f"%(((nm[f"{v}_H{H}"]>0)==(nm[tc]>0)).mean()),"n",len(nm))
d2=df[df.delta==0.2]; print("P25 no-round-term |bias| at delta .2:",d2.groupby("kappa").ka_b.mean().round(3).to_dict(),"; with round term all cells max |bias|:",df.groupby(["kappa","delta"]).kb_b.mean().abs().max().round(3))
print("true lift sign changes between H=6 and H=10 cells:",df.groupby(["kappa","delta"]).agg(t6=("t6","first"),t10=("t10","first")).round(4).to_dict("index"))
