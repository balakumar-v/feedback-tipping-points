import json, numpy as np, pandas as pd
pd.set_option("display.width", 250)
df = pd.DataFrame(json.load(open("results/e2_rows.json"))); df["cls"] = np.where(df.true_lift < -0.002, "worse", np.where(df.true_lift > 0.002, "better", "marg"))
print("rows", len(df), "candidate classes per tau_old:\n", df.groupby(["tau_old"]).cls.value_counts().unstack().to_string())
print("\n--- per overlap level (tau_old): separate findings ---")
R = []
for tau, x in df.groupby("tau_old"):
    w = x[x.cls == "worse"]; b = x[x.cls == "better"]
    R.append(dict(tau_old=tau, ESS_n=x.ess.mean(), maxw=x.maxw.mean(), gap_dr_snips_over_ciw=x.gap.mean(), cov_ipw=x.ipw_cov.mean(), cov_snips=x.snips_cov.mean(), cov_dr=x.dr_cov.mean(),
                  FA_ipw=w.ipw_app.mean(), FA_snips=w.snips_app.mean(), FA_dr=w.dr_app.mean(), FR_dr=1 - b.dr_app.mean(), FA_naive_fav=w.naive_fav_app.mean(), FR_naive_adv=1 - b.naive_adv_app.mean()))
print(pd.DataFrame(R).to_string(float_format=lambda v: "%.3f" % v))
print("\n--- by ESS/n bin (all tau_old pooled; truly-worse candidates) ---")
df["bin"] = pd.cut(df.ess, [0, 0.05, 0.1, 0.3, 1.01], labels=["<0.05", "0.05-0.1", "0.1-0.3", ">0.3"])
R = []
for bn, x in df.groupby("bin", observed=True):
    w = x[x.cls == "worse"]; b = x[x.cls == "better"]
    R.append(dict(bin=bn, n=len(x), n_worse=len(w), cov_dr=x.dr_cov.mean(), cov_snips=x.snips_cov.mean(), FA_dr=w.dr_app.mean() if len(w) else np.nan, FA_snips=w.snips_app.mean() if len(w) else np.nan, FA_ipw=w.ipw_app.mean() if len(w) else np.nan, FR_dr=1 - b.dr_app.mean() if len(b) else np.nan))
print(pd.DataFrame(R).to_string(float_format=lambda v: "%.3f" % v))
w = df[df.cls == "worse"]; b = df[df.cls == "better"]
print("\npooled truly-worse n=%d: FA ipw %.3f snips %.3f dr %.3f | naive-fav %.3f ; truly-better n=%d: FR dr %.3f naive-adv %.3f" % (len(w), w.ipw_app.mean(), w.snips_app.mean(), w.dr_app.mean(), w.naive_fav_app.mean(), len(b), 1 - b.dr_app.mean(), 1 - b.naive_adv_app.mean()))
# disagreement as a flag for DR errors
df["bigerr"] = (df.dr_err.abs() > 0.02).astype(int)
from sklearn.metrics import roc_auc_score
for c in ("ess", "maxw", "gap"):
    s = -df[c] if c == "ess" else df[c]; print("AUC of", c, "for |DR err|>0.02:", round(roc_auc_score(df.bigerr, s), 3), "base rate", round(df.bigerr.mean(), 3))
df["miss"] = 1 - df.dr_cov
for c in ("ess", "maxw", "gap"):
    s = -df[c] if c == "ess" else df[c]; print("AUC of", c, "for DR CI miss:", round(roc_auc_score(df.miss, s), 3), "base rate", round(df.miss.mean(), 3))
