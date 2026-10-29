"""POST-HOC diagnostic of the E5 misses (not pre-registered). Random logs scoring BTS with (a) OBP static BTS dist, (b) BTS's realised weekly shares, (c) BTS's realised daily shares; BTS logs scoring Random with weight clipping; exact CIs for the A/B truth."""
import sys, types, numpy as np, json, pandas as pd
from pathlib import Path
from scipy.stats import beta
import os; sys.path.insert(0, os.environ.get("ZR_OBP", "zr-obp"))
class _Stub(types.ModuleType):
    def __getattr__(self, k):
        if k.startswith("__"): raise AttributeError(k)
        v = _Stub(self.__name__ + "." + k) if k[0].islower() else type(k, (), {"__init__": lambda *a, **kw: None})
        setattr(self, k, v); return v
for name in ["tqdm", "torch", "torch.nn", "torch.nn.functional", "torch.optim", "torch.utils", "torch.utils.data"]: sys.modules[name] = _Stub(name)
sys.modules["tqdm"].tqdm = lambda x, *a, **k: x
from obp.dataset import OpenBanditDataset
from obp.policy import BernoulliTS
from sklearn.linear_model import LogisticRegression
P = Path(__import__("os").environ.get("OBD_FULL", "obd_full")); rng = np.random.default_rng(1); out = {}
def cp(k, n): return [float(beta.ppf(.025, k, n - k + 1)), float(beta.ppf(.975, k + 1, n - k))]
# ground truth with exact CIs
dsb = OpenBanditDataset(behavior_policy="bts", campaign="men", data_path=P); bb = dsb.obtain_batch_bandit_feedback()
dsr = OpenBanditDataset(behavior_policy="random", campaign="men", data_path=P); br = dsr.obtain_batch_bandit_feedback()
for nm, b in (("bts", bb), ("random", br)):
    k, n = int(b["reward"].sum()), b["n_rounds"]; out[f"truth_{nm}"] = dict(ctr=k / n, exact95=cp(k, n))
print(json.dumps(out), flush=True)
A, L = 34, 3
# (b)/(c): BTS realised shares
tb = pd.to_datetime(dsb.data["timestamp"]); tr = pd.to_datetime(dsr.data["timestamp"])
db, dr_ = tb.dt.day.values, tr.dt.day.values
cnt_w = np.zeros((A, L)); np.add.at(cnt_w, (bb["action"], bb["position"]), 1); pi_week = cnt_w / cnt_w.sum(0, keepdims=True)
days = np.unique(db); pi_day = {}
for d in days:
    c = np.zeros((A, L)); m = db == d; np.add.at(c, (bb["action"][m], bb["position"][m]), 1); pi_day[d] = c / c.sum(0, keepdims=True)
pol = BernoulliTS(n_actions=A, len_list=L, is_zozotown_prior=True, campaign="men", random_state=12345); pi_static = pol.compute_batch_action_dist(n_sim=100000)[0]
ctx, act, pos, y, ps = br["context"].astype(np.float32), br["action"], br["position"], br["reward"].astype(float), br["pscore"]
n = br["n_rounds"]
def feats(c, a, p): return np.hstack([c, np.eye(A, dtype=np.float32)[a], np.eye(L, dtype=np.float32)[p]])
sub = rng.choice(n, size=min(n, 1_000_000), replace=False); m = LogisticRegression(max_iter=300, C=0.1).fit(feats(ctx[sub], act[sub], pos[sub]), y[sub])
qa = m.predict_proba(feats(ctx, act, pos))[:, 1]
Q = np.empty((n, A)); 
for a in range(A): Q[:, a] = m.predict_proba(feats(ctx, np.full(n, a), pos))[:, 1]
truth = out["truth_bts"]["ctr"]; res = {}
def est(name, pi_rows):   # pi_rows: (n, A) evaluated-policy probs for each row's position/day
    w = pi_rows[np.arange(n), act] / ps; dm = (pi_rows * Q).sum(1); dr = dm + w * (y - qa)
    def boot(f):
        v = np.empty(300)
        for b in range(300): c = rng.poisson(1.0, n).astype(float); v[b] = f(c)
        return [float(x) for x in np.quantile(v, [.025, .975])]
    r = dict(ipw=float((w * y).mean()), snips=float((w * y).sum() / w.sum()), dm=float(dm.mean()), dr=float(dr.mean()))
    r["ci_snips"] = boot(lambda c: (c * w * y).sum() / (c * w).sum()); r["ci_dr"] = boot(lambda c: (c * dr).sum() / c.sum())
    r["rel_err"] = {k: (r[k] - truth) / truth for k in ("ipw", "snips", "dm", "dr")}; r["ess_n"] = float(w.sum() ** 2 / (w ** 2).sum() / n)
    r["in_ci"] = {"snips": r["ci_snips"][0] <= truth <= r["ci_snips"][1], "dr": r["ci_dr"][0] <= truth <= r["ci_dr"][1]}
    res[name] = r; print(name, json.dumps(r), flush=True)
est("static_OBP_BTS", pi_static[:, pos].T)
est("realised_weekly_BTS", pi_week[:, pos].T)
est("realised_daily_BTS", np.stack([pi_day[d][:, p] if d in pi_day else pi_week[:, p] for d, p in zip(dr_, pos)]))
out["random_scores_bts"] = res
# reverse direction: BTS logs scoring Random, clipping sweep
w = (1 / A) / bb["pscore"]; yb = bb["reward"].astype(float); truth_r = out["truth_random"]["ctr"]; clip = {}
for cap in (None, 100, 50, 20, 10, 5):
    wc = w if cap is None else np.minimum(w, cap)
    clip[str(cap)] = dict(ipw=float((wc * yb).mean()), snips=float((wc * yb).sum() / wc.sum()), rel_snips=float(((wc * yb).sum() / wc.sum() - truth_r) / truth_r))
out["bts_scores_random_clip"] = clip; out["bts_pscore_quantiles"] = {q: float(np.quantile(bb["pscore"], q)) for q in (0, .001, .01, .1, .5, 1)}
out["bts_scores_random_w_quantiles"] = {q: float(np.quantile(w, q)) for q in (.5, .9, .99, .999, 1)}
print(json.dumps({k: out[k] for k in ("bts_scores_random_clip", "bts_pscore_quantiles", "bts_scores_random_w_quantiles")}, indent=1))
json.dump(out, open("results/e5_diag.json", "w"), indent=1)
