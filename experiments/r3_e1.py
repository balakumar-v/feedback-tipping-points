"""R3-1 closed-loop sizing. usage: python -m experiments.r3_e1 S0 S1 OUT"""
import sys, json, time, numpy as np
from p3ope import r2_lib as R
from experiments.r2_e5 import vs, comb, dr_terms
from p3ope.exp13_lib import K, T_OBS
B,NB=30,4000; R.NF=3000; SH=("lin","log","mem7"); ZA,ZP=1.96,0.84; CAP=8000; NS0=3000; M=1.0
def audit(db,ds,beta):
    ns=ds["n"]; obs=db["Y"].mean(1); y0b=db["Y"][0]; rng=np.random.default_rng(int(ds["X0"][0,0]*1e9)%2**31)
    WUb=rng.poisson(1.0,size=(B,NB)).astype(float); WUs=rng.poisson(1.0,size=(B,ns)).astype(float); res={}
    for s in SH:
        b,Xs,ys=R.fit(ds,s,True); v=dr_terms(ds,b); spt=v.mean()-y0b.mean(); pt=R.forecast(b,s,True,"flat",beta,obs,10)
        sl=np.empty(B); fl=np.empty(B); kb=np.empty(B)
        for i in range(B):
            bi=R.newton_fast(Xs,ys,np.tile(WUs[i],T_OBS),b,3); vi=dr_terms(ds,bi)
            sl[i]=(WUs[i]@vi)/WUs[i].sum()-(WUb[i]@y0b)/WUb[i].sum()
            fl[i]=R.forecast(bi,s,True,"flat",beta,(db["Y"]@WUb[i])/WUb[i].sum(),10); kb[i]=R.kappa_of(bi)
        slo,shi=np.quantile(sl,[.025,.975]); lo,hi=np.quantile(fl,[.025,.975])
        res[s]=dict(v=vs(slo,shi,lo,hi),spt=spt,pt=pt,sd_s=sl.std(ddof=1)*np.sqrt(ns),sd_f=fl.std(ddof=1)*np.sqrt(ns),sd_k=kb.std(ddof=1)*np.sqrt(ns),k=R.kappa_of(b),b=b)
    res["v3"]=comb([res[s]["v"] for s in SH]); return res,obs
def need(est,sd,z):
    return np.inf if est==0 else (z*sd/abs(est))**2
def n_verdict(res,z):
    out=[]
    for s in SH:
        r=res[s]; st=[(r["spt"],r["sd_s"]),(r["pt"],r["sd_f"])]
        if all(e>0 for e,_ in st): out.append(max(need(e,sd,z) for e,sd in st))
        else: out.append(min(need(e,sd,z) for e,sd in st if e<=0))
    return max(out)
def kstar(b,beta,obs):
    def f(k):
        b2=b.copy(); b2[K*R.D+K]=-k; return R.forecast(b2,"lin",True,"flat",beta,obs,10)
    lo,hi=0.0,4.0
    if f(lo)<=0: return 0.0
    if f(hi)>0: return 4.0
    for _ in range(9):
        mid=(lo+hi)/2
        if f(mid)>0: lo=mid
        else: hi=mid
    return (lo+hi)/2
def one(kappa,seed,tl):
    beta,gamma=.5*M,.8*M; rng=np.random.default_rng([seed,int(kappa*10),66])
    db=R.simulate(NB,rng,"lin",kappa,0,beta,gamma,"old"); dp=R.simulate(NS0,rng,"lin",kappa,0,beta,gamma,"slice")
    res,obs=audit(db,dp,beta); rec=dict(kappa=kappa,seed=seed,true10=tl,pilot=res["v3"],lin_k=res["lin"]["k"])
    if res["v3"]!="NEED": return rec
    ks=kstar(res["lin"]["b"],beta,obs); dk=abs(res["lin"]["k"]-ks)
    n0=np.inf if dk<1e-9 else (ZA*res["lin"]["sd_k"]/dk)**2
    ns_={"V0":n0,"V1":n_verdict(res,ZA),"V2":n_verdict(res,ZA+ZP)}
    rec["kstar"]=ks
    for v,n in ns_.items():
        rec[f"n_{v}"]=float(min(n,1e9))
        if n>CAP: rec[f"after_{v}"]="CAPPED"; continue
        n2=int(max(NS0,np.ceil(n))); ds2=R.simulate(n2,np.random.default_rng([seed,int(kappa*10),n2,67]),"lin",kappa,0,beta,gamma,"slice")
        r2,_=audit(db,ds2,beta); rec[f"after_{v}"]=r2["v3"]; rec[f"n2_{v}"]=n2
    return rec
if __name__=="__main__":
    import os
    s0,s1=int(sys.argv[1]),int(sys.argv[2]); done=set()
    if os.path.exists(sys.argv[3]): done={(json.loads(l)["kappa"],json.loads(l)["seed"]) for l in open(sys.argv[3])}
    out=open(sys.argv[3],"a"); T0=time.time()
    for kappa in (0.0,0.2,0.4,0.6,0.8,1.0):
        tl=R.true_lift("lin",kappa,0,.5*M,.8*M)
        for seed in range(s0,s1):
            if (kappa,seed) in done: continue
            out.write(json.dumps(one(kappa,seed,tl),default=float)+"\n"); out.flush()
        print("kappa",kappa,"true10 %+.4f"%tl,"elapsed",round(time.time()-T0),flush=True)
