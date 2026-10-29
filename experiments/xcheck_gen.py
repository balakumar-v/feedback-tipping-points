import numpy as np
from p3ope.ope_pilot import *
rng = np.random.default_rng(11)
logs = sample_logs(20000, rng, alpha=0.5, tau=1.0)
pn = pi_new(logs["X"])
Q = fit_q(logs["X"], logs["a"], logs["y"])
t = terms(logs, pn, Q)
est = estimates(t)
print("mine:", {k: round(v, 6) for k, v in est.items()})
np.savez("xcheck.npz", a=logs["a"], y=logs["y"], e=logs["e"], pn=pn, Q=Q)
