"""R5 runs. usage: python -m experiments.r5_e1 MODE OUT   MODE = design | curve"""
import sys, json, os, time, numpy as np
from p3ope import r2_lib as R
from experiments import r3_e1 as X
from p3ope import r5_lib as T5
from scipy.stats import norm
M=1.0; beta,gamma=.5*M,.8*M
PLAN={"design":dict(seeds=range(700,716),kappas=(0.0,.2,.3,.35,.4),runs=[("uniform",3000),("tail",3000)]),
      "curve":dict(seeds=range(800,810),kappas=(0.0,.2,.35),runs=[("uniform",1500),("uniform",6000),("uniform",8000)])}
def one(design,ns,kappa,seed,tl):
    rng=np.random.default_rng([seed,int(kappa*100),88]); db=R.simulate(X.NB,rng,"lin",kappa,0,beta,gamma,"old")
    rs=np.random.default_rng([seed,int(kappa*100),ns,77,design=="tail"])
    ds=R.simulate(ns,rs,"lin",kappa,0,beta,gamma,"slice") if design=="uniform" else T5.simulate_tail(ns,rs,kappa,beta,gamma)
    res,obs=X.audit(db,ds,beta); ks=X.kstar(res["lin"]["b"],beta,obs); k=res["lin"]["k"]; se=res["lin"]["sd_k"]/np.sqrt(ns)
    return dict(design=design,ns=ns,kappa=kappa,seed=seed,true10=tl,v3=res["v3"],lin_k=k,kstar=ks,se_k=se,margin=(k-ks)/se,
                n_V2=float(min(X.n_verdict(res,X.ZA+X.ZP),1e9)),ctr_slice=float(ds["Y"].mean()),ctr_old=float(db["Y"].mean()))
if __name__=="__main__":
    P=PLAN[sys.argv[1]]; f=sys.argv[2]; done=set()
    if os.path.exists(f): done={(r["design"],r["ns"],r["kappa"],r["seed"]) for r in map(json.loads,open(f))}
    out=open(f,"a"); T0=time.time()
    for kappa in P["kappas"]:
        tl=R.true_lift("lin",kappa,0,beta,gamma)
        for design,ns in P["runs"]:
            for seed in P["seeds"]:
                if (design,ns,kappa,seed) in done: continue
                out.write(json.dumps(one(design,ns,kappa,seed,tl),default=float)+"\n"); out.flush()
        print(sys.argv[1],"kappa",kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
