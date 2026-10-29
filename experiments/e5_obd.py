"""E5a OBD static check ('men' campaign). usage: python3 e5_obd.py DATA_PATH  (folder holding random/men/men.csv and bts/men/men.csv, e.g. the OBP 'obd' folder)
Random logs evaluate BTS and BTS logs evaluate Random, scored against the on-policy A/B CTR of the evaluated policy. Uses OBP source (torch/tqdm stubbed; PyPI blocked in this sandbox)."""
import sys, types, numpy as np, json
from pathlib import Path
import os; sys.path.insert(0, os.environ.get("ZR_OBP", "zr-obp"))
class _Stub(types.ModuleType):
    def __getattr__(self, k):
        if k.startswith("__"): raise AttributeError(k)
        v = _Stub(self.__name__ + "." + k) if k[0].islower() else type(k, (), {"__init__": lambda *a, **kw: None})
        setattr(self, k, v); return v
for name in ["tqdm", "torch", "torch.nn", "torch.nn.functional", "torch.optim", "torch.utils", "torch.utils.data"]: sys.modules[name] = _Stub(name)
sys.modules["tqdm"].tqdm = lambda x, *a, **k: x
from obp.dataset import OpenBanditDataset
from obp.policy import BernoulliTS, Random
from obp.ope import InverseProbabilityWeighting as IPW, SelfNormalizedInverseProbabilityWeighting as SN, DirectMethod as DM, DoublyRobust as DR
from sklearn.linear_model import LogisticRegression
data_path = Path(sys.argv[1]); rng = np.random.default_rng(0); out = {}
def run(log_pol, eval_pol):
    ds = OpenBanditDataset(behavior_policy=log_pol, campaign="men", data_path=data_path); bf = ds.obtain_batch_bandit_feedback()
    n = bf["n_rounds"]
    if eval_pol == "bts": pol = BernoulliTS(n_actions=ds.n_actions, len_list=ds.len_list, is_zozotown_prior=True, campaign="men", random_state=12345)
    else: pol = Random(n_actions=ds.n_actions, len_list=ds.len_list)
    ad = pol.compute_batch_action_dist(n_sim=100000) if eval_pol == "bts" else pol.compute_batch_action_dist(n_rounds=bf["n_rounds"])                      # (n_actions, len_list, 1) policy distribution, context-free
    ad = np.tile(ad, (n, 1, 1)) if ad.shape[0] != n else ad
    gt = OpenBanditDataset.calc_on_policy_policy_value_estimate(behavior_policy=eval_pol, campaign="men", data_path=data_path)
    # reward model: per-position logistic on user features + one-hot action (plain DM/DR baseline)
    from sklearn.preprocessing import OneHotEncoder
    X = np.hstack([bf["context"], np.eye(ds.n_actions)[bf["action"]], np.eye(ds.len_list)[bf["position"]]]); m = LogisticRegression(max_iter=300, C=0.1).fit(X, bf["reward"])
    q = np.zeros((n, ds.n_actions, ds.len_list))
    for a in range(ds.n_actions):
        for p in range(ds.len_list):
            Xa = np.hstack([bf["context"], np.tile(np.eye(ds.n_actions)[a], (n, 1)), np.tile(np.eye(ds.len_list)[p], (n, 1))]); q[:, a, p] = m.predict_proba(Xa)[:, 1]
    est = {}
    for nm, E in (("ipw", IPW()), ("snips", SN())):
        est[nm] = E.estimate_policy_value(reward=bf["reward"], action=bf["action"], position=bf["position"], pscore=bf["pscore"], action_dist=ad)
    est["dm"] = DM().estimate_policy_value(action_dist=ad, estimated_rewards_by_reg_model=q, position=bf["position"])
    est["dr"] = DR().estimate_policy_value(reward=bf["reward"], action=bf["action"], position=bf["position"], pscore=bf["pscore"], action_dist=ad, estimated_rewards_by_reg_model=q)
    # weights and bootstrap CI for SNIPS / IPW
    w = ad[np.arange(n), bf["action"], bf["position"]] / bf["pscore"]; ess = w.sum() ** 2 / (w ** 2).sum() / n
    idx = rng.integers(0, n, size=(300, n)); y = bf["reward"]
    ci = {"ipw": np.quantile((w[idx] * y[idx]).mean(1), [.025, .975]), "snips": np.quantile((w[idx] * y[idx]).sum(1) / w[idx].sum(1), [.025, .975])}
    ab_boot = None
    return dict(n=n, A_B_CTR=float(gt), est={k: float(v) for k, v in est.items()}, ess_over_n=float(ess), max_w_share=float(w.max() / w.sum()), ci={k: [float(x) for x in v] for k, v in ci.items()},
                naive_mean_logged_ctr=float(y.mean()), in_ci={k: bool(ci[k][0] <= gt <= ci[k][1]) for k in ci})
for lp, ep in (("random", "bts"), ("bts", "random")):
    out[f"{lp}_logs_evaluate_{ep}"] = run(lp, ep); print(lp, "->", ep, json.dumps(out[f"{lp}_logs_evaluate_{ep}"], indent=1), flush=True)
json.dump(out, open("results/e5_obd.json", "w"), indent=1)
