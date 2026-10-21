"""R2-4 round-index term + horizon. usage: python -m experiments.r2_e4 SEEDS OUT"""
import sys, json, time, numpy as np
from p3ope import r2_lib as R
S=int(sys.argv[1]); out=open(sys.argv[2],"a"); T0=time.time()
for kappa in (0.2,0.6):
    for delta in (0.0,0.1,0.2):
        t6=R.true_lift("lin",kappa,delta,0,0,H=6); t10=R.true_lift("lin",kappa,delta,0,0,H=10)
        for seed in range(S):
            rng=np.random.default_rng([seed,int(kappa*10),int(delta*10),44])
            d=R.simulate(4000,rng,"lin",kappa,delta,0,0,"old"); obs=d["Y"].mean(1)
            rec=dict(kappa=kappa,delta=delta,seed=seed,t6=t6,t10=t10)
            ba,_,_=R.fit(d,"lin",False); bb,_,_=R.fit(d,"lin",True)
            rec.update(k_a=R.kappa_of(ba),k_b=R.kappa_of(bb),theta=float(bb[-1]))
            for H in (6,10):
                rec[f"a_H{H}"]=R.forecast(ba,"lin",False,"flat",0,obs,H)
                rec[f"bflat_H{H}"]=R.forecast(bb,"lin",True,"flat",0,obs,H)
                rec[f"blin_H{H}"]=R.forecast(bb,"lin",True,"lin",0,obs,H)
            out.write(json.dumps(rec)+"\n")
    print("E4 kappa",kappa,round(time.time()-T0),flush=True)
