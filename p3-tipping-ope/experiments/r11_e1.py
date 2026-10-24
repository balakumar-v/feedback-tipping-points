"""R11-1 rule v6: repeat-heavy 10-round slice + coverage guard, held-out generator W4 (and W3 retro). usage: python -m experiments.r11_e1 S0 S1 OUT"""
import sys, json, os, time, numpy as np
from p3ope import r2_lib as R
from p3ope import r8_lib as W
from p3ope.exp13_lib import K, D, pi_new, TN, T_EVAL
from experiments.r2_e5 import vs, comb, dr_terms
from experiments import r3_e1 as X
B, NB = 30, 4000; R.NF = 3000; SH = ("lin", "log", "mem7", "tail2"); beta, gamma = .5, .8; NS = 3000; TS = 10
def exposure():
    rng = np.random.default_rng(5); n = 20000; X0 = rng.normal(size=(n, D)); Pn = pi_new(X0, TN).cumsum(1); st = R.St(n); ii = np.arange(n); cs = []
    for t in range(T_EVAL):
        a = (Pn > rng.random((n, 1))).argmax(1); cs.append(st.cnt[ii, a].copy()); st.step(a)
    return np.bincount(np.array(cs).ravel().astype(int), minlength=12) / (n * T_EVAL)
EXP = exposure()
def guard(ds):
    c = np.bincount(ds["G"]["lin"].ravel().astype(int), minlength=12); ok = np.where(c >= 100)[0]; csup = int(ok.max()) if len(ok) else -1
    return csup, float(EXP[csup + 1:].sum())
def audit(db, ds):
    ns=ds["n"]; obs=db["Y"].mean(1); y0b=db["Y"][0]; rng=np.random.default_rng(int(ds["X0"][0,0]*1e9)%2**31)
    WUb=rng.poisson(1.0,size=(B,NB)).astype(float); WUs=rng.poisson(1.0,size=(B,ns)).astype(float); res={}
    for s in SH:
        b,Xs,ys=R.fit(ds,s,True); v=dr_terms(ds,b); spt=v.mean()-y0b.mean(); pt=R.forecast(b,s,True,"flat",beta,obs,10)
        sl=np.empty(B); fl=np.empty(B); kb=np.empty(B)
        for i in range(B):
            bi=R.newton_fast(Xs,ys,np.tile(WUs[i],ds['T']),b,3); vi=dr_terms(ds,bi)
            sl[i]=(WUs[i]@vi)/WUs[i].sum()-(WUb[i]@y0b)/WUb[i].sum()
            fl[i]=R.forecast(bi,s,True,"flat",beta,(db["Y"]@WUb[i])/WUb[i].sum(),10); kb[i]=R.kappa_of(bi)
        slo,shi=np.quantile(sl,[.025,.975]); lo,hi=np.quantile(fl,[.025,.975])
        res[s]=dict(v=vs(slo,shi,lo,hi),spt=spt,pt=pt,sd_s=sl.std(ddof=1)*np.sqrt(ns),sd_f=fl.std(ddof=1)*np.sqrt(ns),sd_k=kb.std(ddof=1)*np.sqrt(ns),k=R.kappa_of(b),b=b)
    res["v3"]=comb([res[s]["v"] for s in SH]); return res,obs

CELLS4 = [("cliff4", .3), ("cliff4", 1.2), ("cliff4", 1.6), ("cliff4", 2.0), ("late4", .3), ("late4", 1.6), ("late4", 3.0), ("late4", 5.0), ("quadlate", .1), ("quadlate", .8), ("quadlate", 1.2), ("quadlate", 2.0)]
CELLS3 = [("step", 1.2), ("step", 1.6), ("step", 2.0), ("late", .8), ("late", 1.2), ("late", 2.0)]
def one(kind, kappa, seed, tl, gen):
    cid = sum(map(ord, f"{kind}{kappa}"))
    db = W.sim_w3(X.NB, np.random.default_rng([seed, cid, 311]), kind, kappa, beta, gamma, "old")
    ds = W.sim_w3(NS, np.random.default_rng([seed, cid, NS, 312]), kind, kappa, beta, gamma, "tail", T=TS)
    res, obs = audit(db, ds); csup, uns = guard(ds); v5 = comb([res[s]["v"] for s in SH]); v6 = "NEED" if (v5 == "APPROVE" and uns > 0.05) else v5
    rec = dict(gen=gen, kind=kind, kappa=kappa, seed=seed, true10=tl, csup=csup, unsup=uns, v5=v5, v6=v6)
    for s in SH: rec[f"{s}_v"] = res[s]["v"]
    return rec
if __name__ == "__main__":
    s0, s1, f = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; done = set()
    if os.path.exists(f): done = {(r["kind"], r["kappa"], r["seed"]) for r in map(json.loads, open(f))}
    out = open(f, "a"); T0 = time.time()
    for gen, cells in (("W4", CELLS4), ("W3", CELLS3)):
        for kind, kappa in cells:
            tl = W.true_lift_w3(kind, kappa, beta, gamma)
            for seed in range(s0, s1):
                if (kind, kappa, seed) in done: continue
                out.write(json.dumps(one(kind, kappa, seed, tl, gen), default=float) + "\n"); out.flush()
            print(gen, kind, kappa, "true10 %+.4f" % tl, "elapsed", round(time.time() - T0), flush=True)
