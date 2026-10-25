"""R2-5 held-out evaluation of frozen rule v2 on the SLICE audit under hidden taste. usage: python -m experiments.r2_e5 M NS SEED0 SEED1 OUT"""
import sys, json, time, numpy as np
from p3ope import r2_lib as R
from scipy.special import expit
from p3ope.exp13_lib import K, T_OBS, pi_new, TN
B,NB=40,4000; R.NF=3000; SH=("lin","log","mem7"); KAPPAS=(0.0,0.2,0.4,0.6,0.8,1.0,1.5)
def vs(slo,shi,lo,hi):
    if shi<=0 or hi<=0: return "REJECT"
    if slo>0 and lo>0: return "APPROVE"
    return "NEED"
def comb(vl):
    if all(v=="APPROVE" for v in vl): return "APPROVE"
    if all(v=="REJECT" for v in vl): return "REJECT"
    return "NEED"
def dr_terms(ds,b):
    ns=ds["n"]; ii=np.arange(ns); Wf=b[:K*R.D].reshape(K,R.D); bf=b[K*R.D:K*R.D+K]
    q=expit(ds["X0"]@Wf.T+bf); Pn=pi_new(ds["X0"],TN); a0=ds["A"][0]
    return (Pn*q).sum(1)+K*Pn[ii,a0]*(ds["Y"][0]-q[ii,a0])
def audit(m,kappa,ns,seed,tl):
    beta,gamma=.5*m,.8*m
    rng=np.random.default_rng([seed,int(m*10),int(kappa*10),ns,55])
    db=R.simulate(NB,rng,"lin",kappa,0,beta,gamma,"old"); ds=R.simulate(ns,rng,"lin",kappa,0,beta,gamma,"slice")
    obs=db["Y"].mean(1); y0b=db["Y"][0]; WUb=rng.poisson(1.0,size=(B,NB)).astype(float); WUs=rng.poisson(1.0,size=(B,ns)).astype(float)
    rec=dict(m=m,kappa=kappa,ns=ns,seed=seed,true10=tl); vl={}
    for s in SH:
        b,Xs,ys=R.fit(ds,s,True); v=dr_terms(ds,b); spt=v.mean()-y0b.mean(); pt=R.forecast(b,s,True,"flat",beta,obs,10)
        sl=np.empty(B); fl=np.empty(B)
        for i in range(B):
            bi=R.newton_fast(Xs,ys,np.tile(WUs[i],T_OBS),b,3); vi=dr_terms(ds,bi)
            sl[i]=(WUs[i]@vi)/WUs[i].sum()-(WUb[i]@y0b)/WUb[i].sum()
            fl[i]=R.forecast(bi,s,True,"flat",beta,(db["Y"]@WUb[i])/WUb[i].sum(),10)
        slo,shi=np.quantile(sl,[.025,.975]); lo,hi=np.quantile(fl,[.025,.975]); vl[s]=vs(slo,shi,lo,hi)
        rec.update({f"{s}_k":R.kappa_of(b),f"{s}_s":spt,f"{s}_slo":slo,f"{s}_shi":shi,f"{s}_pt":pt,f"{s}_lo":lo,f"{s}_hi":hi,f"{s}_v":vl[s]})
    rec["v3"]=comb(list(vl.values())); rec["v1"]=vl["lin"]
    return rec
if __name__=="__main__":
    ms=[float(x) for x in sys.argv[1].split(",")]; ns=int(sys.argv[2]); s0,s1,out=int(sys.argv[3]),int(sys.argv[4]),open(sys.argv[5],"a"); T0=time.time()
    for m in ms:
        for kappa in KAPPAS:
            tl=R.true_lift("lin",kappa,0,.5*m,.8*m)
            for seed in range(s0,s1): out.write(json.dumps(audit(m,kappa,ns,seed,tl),default=float)+"\n"); out.flush()
            print("m",m,"kappa",kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
