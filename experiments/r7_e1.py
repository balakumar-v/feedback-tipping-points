"""R7-1 out-of-family false approval (v4). usage: python -m experiments.r7_e1 S0 S1 OUT"""
import sys, json, os, time
from p3ope import r2_lib as R
from experiments import r2_e3 as E
from experiments import r3_e3 as X   # sets E.B=30, E.SH incl tail2, R.NF=3000
CELLS=[("convex",.6),("convex",.9),("quad",.2),("quad",.4),("quad",.8)]
if __name__=="__main__":
    s0,s1=int(sys.argv[1]),int(sys.argv[2]); done=set()
    if os.path.exists(sys.argv[3]): done={(json.loads(l)["kind"],json.loads(l)["kappa"],json.loads(l)["seed"]) for l in open(sys.argv[3])}
    out=open(sys.argv[3],"a"); T0=time.time()
    for kind,kappa in CELLS:
        tl=R.true_lift(kind,kappa,0,0,0,H=10)
        for seed in range(s0,s1):
            if (kind,kappa,seed) in done: continue
            rec=E.audit(kind,kappa,seed,tl,tl); rec["v3"],rec["v4"]=X.rules(rec); out.write(json.dumps(rec,default=float)+"\n"); out.flush()
        print(kind,kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
