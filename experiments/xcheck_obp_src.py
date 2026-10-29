# OBP cross-check using zr-obp source (v0.5.5, GitHub) in py3.13; torch stubbed (estimators are numpy-only). PyPI is blocked in this sandbox.
import sys, types, numpy as np, logging
import os; sys.path.insert(0, os.environ.get("ZR_OBP", "zr-obp"))
class _Stub(types.ModuleType):
    def __getattr__(self, k):
        if k.startswith("__"): raise AttributeError(k)
        v = _Stub(self.__name__ + "." + k) if k[0].islower() else type(k, (), {"__init__": lambda *a, **kw: None})
        setattr(self, k, v); return v
for name in ["tqdm", "torch", "torch.nn", "torch.nn.functional", "torch.optim", "torch.utils", "torch.utils.data"]:
    sys.modules[name] = _Stub(name)
sys.modules["tqdm"].tqdm = lambda x, *a, **k: x
import obp
from obp.ope import InverseProbabilityWeighting as IPW, SelfNormalizedInverseProbabilityWeighting as SN, DoublyRobust as DR, DirectMethod as DM
print("obp version", obp.__version__)
d = np.load("xcheck.npz")
n, K = d["pn"].shape
ad = d["pn"][:, :, None]; pos = np.zeros(n, dtype=int); q = d["Q"][:, :, None]
print("obp :", {
 "ipw":  round(IPW().estimate_policy_value(reward=d["y"], action=d["a"], pscore=d["e"], action_dist=ad, position=pos), 6),
 "snips":round(SN().estimate_policy_value(reward=d["y"], action=d["a"], pscore=d["e"], action_dist=ad, position=pos), 6),
 "dm":   round(DM().estimate_policy_value(action_dist=ad, estimated_rewards_by_reg_model=q, position=pos), 6),
 "dr":   round(DR().estimate_policy_value(reward=d["y"], action=d["a"], pscore=d["e"], action_dist=ad, estimated_rewards_by_reg_model=q, position=pos), 6)})
