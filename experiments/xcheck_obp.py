import numpy as np, logging
logging.disable(logging.INFO)
from obp.ope import InverseProbabilityWeighting as IPW, SelfNormalizedInverseProbabilityWeighting as SN, DoublyRobust as DR, DirectMethod as DM
d = np.load("xcheck.npz")
n, K = d["pn"].shape
ad = d["pn"][:, :, None]; pos = np.zeros(n, dtype=int)
q = d["Q"][:, :, None]
print("obp :", {
 "ipw":  round(IPW().estimate_policy_value(reward=d["y"], action=d["a"], pscore=d["e"], action_dist=ad, position=pos), 6),
 "snips":round(SN().estimate_policy_value(reward=d["y"], action=d["a"], pscore=d["e"], action_dist=ad, position=pos), 6),
 "dm":   round(DM().estimate_policy_value(action_dist=ad, estimated_rewards_by_reg_model=q, position=pos), 6),
 "dr":   round(DR().estimate_policy_value(reward=d["y"], action=d["a"], pscore=d["e"], action_dist=ad, estimated_rewards_by_reg_model=q, position=pos), 6)})
