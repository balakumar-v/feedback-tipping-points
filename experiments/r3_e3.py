"""R3-3 out-of-family stress + tail guard. usage: python -m experiments.r3_e3 S0 S1 OUT"""
import sys, json, time, numpy as np
from p3ope import r2_lib as R
from experiments import r2_e3 as E
E.B=30; E.SH=("lin","log","mem7","tail2"); R.NF=3000
CELLS=[("lin",k) for k in (.4,.8,1.0)]+[("convex",k) for k in (.2,.6,.9)]+[("quad",k) for k in (.05,.2,.4,.8)]
def rules(rec):
    v=[rec[f"{s}_v"] for s in ("lin","log","mem7")]; w=v+[rec["tail2_v"]]
    return E.comb(v),E.comb(w)
if __name__=="__main__":
    import os
    s0,s1=int(sys.argv[1]),int(sys.argv[2]); done=set()
    if os.path.exists(sys.argv[3]): done={(json.loads(l)["kind"],json.loads(l)["kappa"],json.loads(l)["seed"]) for l in open(sys.argv[3])}
    out=open(sys.argv[3],"a"); T0=time.time()
    for kind,kappa in CELLS:
        tl=R.true_lift(kind,kappa,0,0,0,H=10)
        for seed in range(s0,s1):
            if (kind,kappa,seed) in done: continue
            rec=E.audit(kind,kappa,seed,tl,tl); rec["v3"],rec["v4"]=rules(rec); out.write(json.dumps(rec,default=float)+"\n"); out.flush()
        print(kind,kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
