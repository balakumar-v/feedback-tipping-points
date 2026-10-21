"""R4-2 slice audit near the boundary (taste x1). usage: python -m experiments.r4_e2 S0 S1 OUT"""
import sys, json, os, time
from p3ope import r2_lib as R
from experiments import r2_e5 as E5
if __name__=="__main__":
    s0,s1=int(sys.argv[1]),int(sys.argv[2]); done=set()
    if os.path.exists(sys.argv[3]): done={(json.loads(l)["kappa"],json.loads(l)["seed"]) for l in open(sys.argv[3])}
    out=open(sys.argv[3],"a"); T0=time.time()
    for kappa in (.2,.25,.3,.35,.4):
        tl=R.true_lift("lin",kappa,0,.5,.8)
        for seed in range(s0,s1):
            if (kappa,seed) in done: continue
            out.write(json.dumps(E5.audit(1.0,kappa,3000,seed,tl),default=float)+"\n"); out.flush()
        print("kappa",kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
