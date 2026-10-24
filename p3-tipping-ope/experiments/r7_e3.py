"""R7-3 slice audit under the final four-shape rule (r3_e1.audit + tail2). usage: python -m experiments.r7_e3 S0 S1 OUT [KAPPAS comma list]"""
import sys, json, os, time, numpy as np
from p3ope import r2_lib as R
from experiments import r3_e1 as X
from experiments.r2_e5 import comb
X.SH=("lin","log","mem7","tail2")
M=1.0; beta,gamma=.5*M,.8*M; NS=3000
KAPPAS=(0.0,.2,.3,.35,.4,.6,.8,1.0,1.5)
def one(kappa,seed,tl):
    rng=np.random.default_rng([seed,int(kappa*100),111])
    db=R.simulate(X.NB,rng,"lin",kappa,0,beta,gamma,"old"); ds=R.simulate(NS,np.random.default_rng([seed,int(kappa*100),NS,112]),"lin",kappa,0,beta,gamma,"slice")
    res,obs=X.audit(db,ds,beta)
    v3=comb([res[s]["v"] for s in ("lin","log","mem7")]); v4=comb([res[s]["v"] for s in X.SH])
    rec=dict(kappa=kappa,seed=seed,true10=tl,v3=v3,v4=v4,lin_k=res["lin"]["k"])
    for s in X.SH: rec[f"{s}_v"]=res[s]["v"]; rec[f"{s}_spt"]=float(res[s]["spt"]); rec[f"{s}_fpt"]=float(res[s]["pt"])
    return rec
if __name__=="__main__":
    s0,s1,f=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
    ks=[float(x) for x in sys.argv[4].split(",")] if len(sys.argv)>4 else KAPPAS; done=set()
    if os.path.exists(f): done={(r["kappa"],r["seed"]) for r in map(json.loads,open(f))}
    out=open(f,"a"); T0=time.time()
    for kappa in ks:
        tl=R.true_lift("lin",kappa,0,beta,gamma)
        for seed in range(s0,s1):
            if (kappa,seed) in done: continue
            out.write(json.dumps(one(kappa,seed,tl),default=float)+"\n"); out.flush()
        print("kappa",kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
