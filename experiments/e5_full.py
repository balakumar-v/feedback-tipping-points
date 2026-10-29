"""E5a full OBD 'men', memory-safe. usage: python3 e5_full.py DATA_PATH OUT.json"""
import sys, types, numpy as np, json, time
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
from sklearn.linear_model import LogisticRegression
data_path = Path(sys.argv[1]); rng = np.random.default_rng(0); out = {}
def run(lp, ep):
    t0 = time.time()
    ds = OpenBanditDataset(behavior_policy=lp, campaign="men", data_path=data_path); bf = ds.obtain_batch_bandit_feedback()
    n = bf["n_rounds"]; A, L = ds.n_actions, ds.len_list
    if ep == "bts": pol = BernoulliTS(n_actions=A, len_list=L, is_zozotown_prior=True, campaign="men", random_state=12345); ad = pol.compute_batch_action_dist(n_sim=100000)
    else: ad = Random(n_actions=A, len_list=L).compute_batch_action_dist(n_rounds=1)
    ad = ad[0]   # (A, L) context-free
    print(lp, "->", ep, "n", n, "ad shape", ad.shape, "col sums", ad.sum(0).round(4), flush=True)
    gt = float(OpenBanditDataset.calc_on_policy_policy_value_estimate(behavior_policy=ep, campaign="men", data_path=data_path))
    ctx, act, pos, y, ps = bf["context"].astype(np.float32), bf["action"], bf["position"], bf["reward"].astype(np.float64), bf["pscore"]
    w = ad[act, pos] / ps
    # reward model (fit on a 1M-row cap for speed), chunked prediction
    sub = rng.choice(n, size=min(n, 1_000_000), replace=False)
    def feats(c, a, p): return np.hstack([c, np.eye(A, dtype=np.float32)[a], np.eye(L, dtype=np.float32)[p]])
    m = LogisticRegression(max_iter=300, C=0.1).fit(feats(ctx[sub], act[sub], pos[sub]), y[sub])
    qa = np.empty(n); dm = np.zeros(n); CH = 100_000
    for s in range(0, n, CH):
        e = min(n, s + CH); qa[s:e] = m.predict_proba(feats(ctx[s:e], act[s:e], pos[s:e]))[:, 1]
    # DM per row: sum_a ad[a,pos]*q(x,a,pos) -- computed per (a, p) block over rows at that position
    for s in range(0, n, CH):
        e = min(n, s + CH); c = ctx[s:e]; pp = pos[s:e]; k = e - s
        for a in range(A):
            qq = m.predict_proba(feats(c, np.full(k, a), pp))[:, 1]
            dm[s:e] += ad[a, pp] * qq
    ipw_t = w * y; dr_t = dm + w * (y - qa)
    def sn(wt, yy): return (wt * yy).sum() / wt.sum()
    est = dict(ipw=ipw_t.mean(), snips=sn(w, y), dm=dm.mean(), dr=dr_t.mean())
    ess = w.sum() ** 2 / (w ** 2).sum() / n
    B = 300; boots = {k: np.empty(B) for k in est}
    for b in range(B):
        c = rng.poisson(1.0, n).astype(np.float64)
        boots["ipw"][b] = (c * ipw_t).sum() / c.sum(); boots["snips"][b] = (c * w * y).sum() / (c * w).sum()
        boots["dm"][b] = (c * dm).sum() / c.sum(); boots["dr"][b] = (c * dr_t).sum() / c.sum()
    ci = {k: np.quantile(v, [.025, .975]) for k, v in boots.items()}
    r = dict(n=int(n), A_B_CTR=gt, est={k: float(v) for k, v in est.items()}, ci={k: [float(x) for x in v] for k, v in ci.items()},
             rel_err={k: float((v - gt) / gt) for k, v in est.items()}, in_ci={k: bool(ci[k][0] <= gt <= ci[k][1]) for k in ci},
             ci_width={k: float(ci[k][1] - ci[k][0]) for k in ci}, ess_over_n=float(ess), max_w_share=float(w.max() / w.sum()),
             naive_log_ctr=float(y.mean()), naive_rel_err=float((y.mean() - gt) / gt), clicks_logged=int(y.sum()), secs=round(time.time() - t0))
    return r
for lp, ep in (("random", "bts"), ("bts", "random")):
    out[f"{lp}_logs_evaluate_{ep}"] = run(lp, ep); print(json.dumps(out[f"{lp}_logs_evaluate_{ep}"], indent=1), flush=True)
    json.dump(out, open(sys.argv[2], "w"), indent=1)
