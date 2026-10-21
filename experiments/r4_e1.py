"""R4-1 second generator W2, logs only. usage: python -m experiments.r4_e1 S0 S1 OUT"""
import sys, json, os, time, numpy as np
from p3ope import r2_lib as R
from p3ope import r4_lib as W2
from experiments import r2_e3 as E
from experiments import r3_e3 as X   # sets E.B=30, E.SH incl tail2, R.NF=3000
R.simulate=lambda n,rng,kind,kappa,delta,beta,gamma,mode="old",T=R.T_OBS: W2.sim_w2(n,rng,kind,kappa,delta,beta,gamma,mode,T)
CELLS=[("lin",k) for k in (.4,.8,1.0,1.2,1.5,2.0)]+[("convex",k) for k in (.4,.9,1.5)]+[("quad",k) for k in (.1,.3,.4,.8)]
if __name__=="__main__":
    s0,s1=int(sys.argv[1]),int(sys.argv[2]); done=set()
    if os.path.exists(sys.argv[3]): done={(json.loads(l)["kind"],json.loads(l)["kappa"],json.loads(l)["seed"]) for l in open(sys.argv[3])}
    out=open(sys.argv[3],"a"); T0=time.time()
    for kind,kappa in CELLS:
        tl=W2.true_lift_w2(kind,kappa)
        for seed in range(s0,s1):
            if (kind,kappa,seed) in done: continue
            rec=E.audit(kind,kappa,seed,tl,tl); rec["v3"],rec["v4"]=X.rules(rec); out.write(json.dumps(rec,default=float)+"\n"); out.flush()
        print(kind,kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
