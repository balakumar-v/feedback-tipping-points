"""R2-3 three-shape guard (logs-only, no taste). usage: python -m experiments.r2_e3 SEED0 SEED1 OUT"""
import sys, json, time, numpy as np
from p3ope import r2_lib as R
B,N=40,4000
R.NF=3000
CELLS=[("lin",k) for k in (.2,.4,.6,.8,1.0)]+[("sat",k) for k in (.4,.9,1.5,2.5,4.0)]+[(t,k) for t in ("decay","window") for k in (.4,.9,1.5,2.5)]+[("convex",k) for k in (.2,.4,.6,.9)]
SH=("lin","log","mem7")
def vs(slo,shi,lo,hi):
    if shi<=0 or hi<=0: return "REJECT"
    if slo>0 and lo>0: return "APPROVE"
    return "NEED"
def comb(vl):
    if all(v=="APPROVE" for v in vl): return "APPROVE"
    if all(v=="REJECT" for v in vl): return "REJECT"
    return "NEED"
def audit(kind,kappa,seed,tl,tl6):
    cid=sum(map(ord,f"{kind}{kappa}"))
    rng=np.random.default_rng([seed,cid,33])
    d=R.simulate(N,rng,kind,kappa,0,0,0,"old"); n=N; T=d["T"]
    WU=rng.poisson(1.0,size=(B,n)).astype(float)
    s_pt,sb=R.snips0(d,WU); s_lo,s_hi=np.quantile(sb,[.025,.975]); obs=d["Y"].mean(1)
    rec=dict(kind=kind,kappa=kappa,seed=seed,true10=tl,true6=tl6,s_pt=s_pt,s_lo=s_lo,s_hi=s_hi)
    vl={}
    for s in SH:
        b,Xd,y=R.fit(d,s); pt=R.forecast(b,s,False,"flat",0,obs,10); pt6=R.forecast(b,s,False,"flat",0,obs,6); fl=np.empty(B)
        for i in range(B):
            bi=R.newton_fast(Xd,y,np.tile(WU[i],T),b,3); obs_i=(d["Y"]@WU[i])/WU[i].sum()
            fl[i]=R.forecast(bi,s,False,"flat",0,obs_i,10)
        lo,hi=np.quantile(fl,[.025,.975]); v=vs(s_lo,s_hi,lo,hi); vl[s]=v
        rec.update({f"{s}_k":R.kappa_of(b),f"{s}_pt":pt,f"{s}_pt6":pt6,f"{s}_lo":lo,f"{s}_hi":hi,f"{s}_v":v})
    rec["v3"]=comb(list(vl.values())); rec["v1"]=vl["lin"]
    return rec
if __name__=="__main__":
    s0,s1,out=int(sys.argv[1]),int(sys.argv[2]),open(sys.argv[3],"a"); T0=time.time()
    for kind,kappa in CELLS:
        tl=R.true_lift(kind,kappa,0,0,0,H=10); tl6=R.true_lift(kind,kappa,0,0,0,H=6)
        for seed in range(s0,s1): out.write(json.dumps(audit(kind,kappa,seed,tl,tl6),default=float)+"\n"); out.flush()
        print(kind,kappa,"true10 %+.4f true6 %+.4f"%(tl,tl6),"elapsed",round(time.time()-T0),flush=True)
