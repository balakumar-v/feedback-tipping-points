"""R7-4 slice audit at the 8,000-user cap under the final four-shape rule. usage: python -m experiments.r7_e4 S0 S1 OUT [KAPPAS]"""
import sys, json, os, time
from p3ope import r2_lib as R
from experiments import r7_e3 as E
E.NS=8000
if __name__=="__main__":
    s0,s1,f=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
    ks=[float(x) for x in sys.argv[4].split(",")] if len(sys.argv)>4 else (0.0,.2); done=set()
    if os.path.exists(f): done={(r["kappa"],r["seed"]) for r in map(json.loads,open(f))}
    out=open(f,"a"); T0=time.time()
    for kappa in ks:
        tl=R.true_lift("lin",kappa,0,E.beta,E.gamma)
        for seed in range(s0,s1):
            if (kappa,seed) in done: continue
            out.write(json.dumps(E.one(kappa,seed,tl),default=float)+"\n"); out.flush()
        print("kappa",kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
