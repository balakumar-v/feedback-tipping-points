"""R2-1 slice kappa estimators + R2-2 ablation. usage: python -m experiments.r2_e1 SEEDS OUT"""
import sys, json, time, numpy as np
from p3ope import r2_lib as R
S=int(sys.argv[1]); out=open(sys.argv[2],"a"); T0=time.time()
for mi,m in enumerate((1.0,2.0,3.0)):
    for kappa in (0.4,0.8):
        for ns in (1500,3000):
            for seed in range(S):
                rng=np.random.default_rng([seed,mi,int(kappa*10),ns,20])
                ds=R.simulate(ns,rng,"lin",kappa,0,0.5*m,0.8*m,"slice")
                b,Xs,ys=R.fit(ds,"lin"); kp=R.kappa_of(b)
                bri=R.newton_ri(Xs,ys,6,ns); kr=-bri[-1]
                kf,sef,nd=R.fe_kappa(ds["A"],ds["Y"])
                out.write(json.dumps(dict(exp="E1",m=m,kappa=kappa,ns=ns,seed=seed,pool=kp,ri=kr,fe=kf,fe_se=sef,nd=nd))+"\n")
    print("E1 m",m,round(time.time()-T0),flush=True)
# R2-2 ablation (m=1)
for kappa in (0.4,0.8):
    for ns in (1500,3000):
        for seed in range(S):
            rng=np.random.default_rng([seed,int(kappa*10),ns,22])
            dl=R.simulate(ns,rng,"lin",kappa,0,0.5,0.8,"lastslice")
            Alast=dl["A"][-1:]; 
            d1=dict(X0=dl["X0"],A=Alast,Y=dl["Y"][-1:],G={"lin":dl["G"]["lin"][-1:]})
            b1,_,_=R.fit(d1,"lin"); k_last=R.kappa_of(b1)
            ds=R.simulate(ns,rng,"lin",kappa,0,0.5,0.8,"slice"); k_every=R.kappa_of(R.fit(ds,"lin")[0])
            kf_last=R.fe_kappa(dl["A"],dl["Y"])[0]
            out.write(json.dumps(dict(exp="E2",kappa=kappa,ns=ns,seed=seed,last=k_last,every=k_every,fe_on_lastworld=kf_last))+"\n")
    print("E2 kappa",kappa,round(time.time()-T0),flush=True)
