import numpy as np, time, warnings
warnings.filterwarnings("ignore")
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
from p3ope.slice_util import slice_logs
op.U_BOUNDED = True; op.NL = 0.0
rng = np.random.default_rng(1001); T0 = time.time()
ALPHA, TAU_OLD, TN, NB, R = 0.8, 1.0, 0.5, 10000, 100
pn_fn = lambda X: pi_new(X, TN)
print("Detection of hidden confounding: z-test of bulk DR vs slice IPW (two-sided, 5% level). m=0 row is the false-alarm rate.")
for m in [0.0, 0.5, 1.0, 2.0]:
    beta, gamma = 0.4 * m, 0.5 * m
    out = {}
    for ns in [300, 1000, 3000]:
        det = []
        for r in range(R):
            B = sample_logs(NB, rng, alpha=ALPHA, tau=TAU_OLD, beta=beta, gamma=gamma)
            xb = terms(B, pn_fn(B["X"]), fit_q(B["X"], B["a"], B["y"]))["dr"]
            S = slice_logs(ns, rng, gamma); xs = terms(S, pn_fn(S["X"]), None)["ipw"]
            z = abs(xs.mean() - xb.mean()) / np.sqrt(xs.var(ddof=1)/ns + xb.var(ddof=1)/NB); det.append(z > 1.96)
        out[ns] = np.mean(det)
    print(f"m={m}: detection rate by slice size: " + ", ".join(f"n_slice={k}: {v:.2f}" for k, v in out.items()), flush=True)
print("elapsed", round(time.time()-T0,1))
