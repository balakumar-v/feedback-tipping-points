import time, numpy as np
from p3ope.exp13_lib import *
# 1) truth vs exp12: no taste, kappa 0.4 -> +0.0103 ; 0.6 -> -0.0013 (exp12 used 20000 users)
for k in (0.0, 0.4, 0.6):
    t=time.time(); print("true lin", k, true_lift("lin", k, 0, 0.0, 0.0), round(time.time()-t,1),"s")
print("true lin taste k=.4", true_lift("lin",0.4,0,0.5,0.8))
# 2) fit vs sklearn on one dataset
rng = np.random.default_rng(1); t=time.time()
d = simulate_obs(4000, rng, "lin", 0.4, 0, 0.0, 0.0); print("sim", round(time.time()-t,2))
t=time.time(); b, Xd, y = fit_full(d); print("fit", round(time.time()-t,2), "kappa_hat", -b[-1])
from sklearn.linear_model import LogisticRegression
m = LogisticRegression(C=10.0, max_iter=400).fit(Xd, y); print("sklearn kappa_hat", -m.coef_[0][-1])
t=time.time(); kb, WU = boot_kappa(Xd, y, b, 4000, T_OBS, 80, rng); print("boot", round(time.time()-t,1), "sd", kb.std(), "ci", np.quantile(kb,[.025,.975]))
print("sandwich se", sandwich_se_kappa(Xd, y, b, 4000, T_OBS))
Wf,bf,kh = unpack(b); pt,sb = static_snips(d, 0.0, WU); print("static", pt, np.quantile(sb,[.025,.975]))
obs_old = d["y"].mean(1); t=time.time()
dl = calib_delta(Wf,bf,kh,0.0,obs_old); print("delta", dl, "fc lift", forecast_lift(Wf,bf,kh,0.0,dl), "kstar", tipping_kappa(Wf,bf,0.0,dl), round(time.time()-t,1),"s")
t=time.time(); print("true tipping no taste", true_tipping(0.0,0.0), round(time.time()-t,1))
