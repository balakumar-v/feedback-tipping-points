import numpy as np, time, warnings
warnings.filterwarnings("ignore")
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
from p3ope.slice_util import slice_logs
op.U_BOUNDED = True; op.NL = 0.0
rng = np.random.default_rng(1212); T0 = time.time()
ALPHA, TAU_OLD, TN, NB, NS, R = 0.8, 1.0, 0.5, 10000, 1000, 80
pn_fn = lambda X: pi_new(X, TN)
grid = np.round(np.arange(1.0, 6.01, 0.05), 2)
def compat_lambda(pa, y, e, lo_e, hi_e):
    """smallest Lambda whose bulk sensitivity interval overlaps the slice confidence interval"""
    for lam in grid:
        lo, hi = msm_bounds(pa, y, e, lam)
        if hi >= lo_e and lo <= hi_e: return lam, lo, hi
    lo, hi = msm_bounds(pa, y, e, grid[-1]); return grid[-1], lo, hi
print("Slice-calibrated Lambda: smallest Lambda at which the bulk MSM interval is compatible with the slice 95% CI. Slice n=1000, bulk n=10000, 80 reps.")
for m in [0.0, 1.0, 2.0]:
    beta, gamma = 0.4 * m, 0.5 * m; V = truth(pn_fn, rng, gamma=gamma); rec = []
    for r in range(R):
        B = sample_logs(NB, rng, alpha=ALPHA, tau=TAU_OLD, beta=beta, gamma=gamma)
        tb = terms(B, pn_fn(B["X"]), None); sn = tb["ipw"].sum() / tb["w"].sum()
        S = slice_logs(NS, rng, gamma); xs = terms(S, pn_fn(S["X"]), None)["ipw"]; th, se = xs.mean(), xs.std(ddof=1) / np.sqrt(NS)
        lam, lo, hi = compat_lambda(tb["pa"], B["y"], B["e"], th - 1.96 * se, th + 1.96 * se)
        # final report: union of slice CI and bulk interval at the calibrated Lambda
        f_lo, f_hi = min(lo, th - 1.96 * se), max(hi, th + 1.96 * se)
        rec.append((lam, lo <= V <= hi, hi - lo, f_lo <= V <= f_hi, f_hi - f_lo, (th - 1.96*se) <= V <= (th + 1.96*se), 3.92 * se, sn - V))
    a = np.array(rec, float)
    print(f"m={m}: bulk nominal bias {a[:,7].mean():+.4f} | calibrated Lambda mean {a[:,0].mean():.2f} | bulk interval@Lambda_hat: cover {a[:,1].mean():.2f} width {a[:,2].mean():.3f}"
          f" | union(bulk@Lambda_hat, slice CI): cover {a[:,3].mean():.2f} width {a[:,4].mean():.3f} | slice-only CI: cover {a[:,5].mean():.2f} width {a[:,6].mean():.3f}", flush=True)
print("elapsed", round(time.time() - T0, 1))
