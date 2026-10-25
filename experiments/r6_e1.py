"""R6 which layer binds. usage: python -m experiments.r6_e1 OUT"""
import sys, json, os, time, numpy as np
from p3ope import r2_lib as R
from experiments import r3_e1 as X
CALLS=[]; _vs=X.vs
def vs_rec(slo,shi,lo,hi): CALLS.append((float(slo),float(shi),float(lo),float(hi))); return _vs(slo,shi,lo,hi)
X.vs=vs_rec
M=1.0; beta,gamma=.5*M,.8*M
def one(kappa,ns,seed,tl):
    CALLS.clear(); rng=np.random.default_rng([seed,int(kappa*100),99])
    db=R.simulate(X.NB,rng,"lin",kappa,0,beta,gamma,"old"); ds=R.simulate(ns,np.random.default_rng([seed,int(kappa*100),ns,98]),"lin",kappa,0,beta,gamma,"slice")
    res,obs=X.audit(db,ds,beta); rec=dict(kappa=kappa,ns=ns,seed=seed,true10=tl,v3=res["v3"])
    for s,(slo,shi,lo,hi) in zip(X.SH,CALLS):
        rec[f"{s}_slo"]=slo; rec[f"{s}_flo"]=lo; rec[f"{s}_spt"]=float(res[s]["spt"]); rec[f"{s}_fpt"]=float(res[s]["pt"]); rec[f"{s}_sds"]=float(res[s]["sd_s"]/np.sqrt(ns)); rec[f"{s}_sdf"]=float(res[s]["sd_f"]/np.sqrt(ns))
    return rec
if __name__=="__main__":
    f=sys.argv[1]; done=set()
    if os.path.exists(f): done={(r["kappa"],r["ns"],r["seed"]) for r in map(json.loads,open(f))}
    out=open(f,"a"); T0=time.time()
    for kappa in (0.0,0.2):
        tl=R.true_lift("lin",kappa,0,beta,gamma)
        for ns in (3000,8000):
            for seed in range(900,916):
                if (kappa,ns,seed) in done: continue
                out.write(json.dumps(one(kappa,ns,seed,tl))+"\n"); out.flush()
            print("kappa",kappa,"ns",ns,"elapsed",round(time.time()-T0),flush=True)
