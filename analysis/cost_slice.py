"""R4-3 cost of the randomised slice (descriptive). Stand-in simulator: clicks per user-round, old policy vs uniform-random slice, 6 logged rounds."""
import numpy as np
from p3ope import r2_lib as R
rng=np.random.default_rng(9); n=60000
for kappa in (0.0,.4,.8):
    o=R.simulate(n,rng,"lin",kappa,0,.5,.8,"old"); s=R.simulate(n,rng,"lin",kappa,0,.5,.8,"slice")
    co,cs=o["Y"].mean(),s["Y"].mean(); print(f"kappa {kappa}: CTR old {co:.4f} uniform {cs:.4f} -> uniform loses {100*(1-cs/co):.1f}% of clicks; per 1000 slice users x 6 rounds = {1000*6*(co-cs):.1f} clicks lost")
print("OBD real (RESULTS.md): Random 0.005124 vs BTS 0.006743 -> uniform loses %.1f%% of clicks"%(100*(1-0.005124/0.006743)))
