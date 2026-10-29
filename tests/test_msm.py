import numpy as np
from scipy.optimize import linprog
from p3ope.ope_pilot import msm_bounds

rng = np.random.default_rng(3)
worst = 0
for trial in range(200):
    n = rng.integers(5, 40)
    e = rng.uniform(0.02, 0.9, n); c = rng.uniform(0, 1, n) * (rng.random(n) > 0.2)
    if c.sum() == 0: continue
    y = (rng.random(n) < 0.4).astype(float)
    lam = rng.uniform(1.0, 4.0)
    lo_m, hi_m = msm_bounds(c, y, e, lam)
    # LP: upper = max, lower = min
    keep = c > 0; cc, yy, ee = c[keep], y[keep], e[keep]; m = len(cc)
    loW = 1 + (1/ee - 1)/lam; hiW = 1 + lam*(1/ee - 1)
    vals = []
    for sgn in (+1, -1):
        obj = np.concatenate([-sgn*cc*yy, [0.0]])
        A_eq = [np.concatenate([cc, [0.0]])]; b_eq = [1.0]
        A_ub, b_ub = [], []
        for i in range(m):
            r = np.zeros(m+1); r[i] = 1; r[m] = -hiW[i]; A_ub.append(r); b_ub.append(0)
            r = np.zeros(m+1); r[i] = -1; r[m] = loW[i]; A_ub.append(r); b_ub.append(0)
        res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)]*(m+1), method="highs")
        vals.append(-res.fun * sgn)   # sgn=+1 -> max value ; sgn=-1 -> -(min) -> min = -(-res.fun)... handled below
    up_lp = vals[0]
    lo_lp = vals[1]
    worst = max(worst, abs(up_lp - hi_m), abs(lo_lp - lo_m))
print("max abs diff between threshold-scan bounds and exact LP over 200 random cases:", worst)
