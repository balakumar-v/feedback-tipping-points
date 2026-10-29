import numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
df = pd.read_csv("tasks.csv")
df["miss_dr"] = ((df.V < df.ci_lo_dr) | (df.V > df.ci_hi_dr)).astype(int)
df["miss_sn"] = ((df.V < df.ci_lo_sn) | (df.V > df.ci_hi_sn)).astype(int)
df["err_dr"] = (df.dr - df.V).abs()
df["big"] = (df.err_dr > 0.02).astype(int)
df["lw_dev"] = (df.mean_w - 1).abs()
df["log_gap"] = np.log1p(df.gap_dr_sn / df.ci_w.clip(lower=1e-6))
df["log_ess"] = np.log(df.ess); df["log_maxw"] = np.log(df.maxw); df["log_n"] = np.log(df.n)
print("n tasks", len(df)); print(df.groupby("fam")[["miss_dr","miss_sn","big","err_dr","ess","khat","lam_star"]].mean().round(3))
sets = {
 "ESS only": ["log_ess"],
 "k-hat only": ["khat"],
 "|mean(w)-1| only": ["lw_dev"],
 "all diagnostics": ["log_ess","log_maxw","khat","lw_dev","cv_w","log_gap","ci_w","lam_star","log_n"],
}
fams = ["A_clean","B_misspec","C_conf","D_loop"]
for target in ["miss_dr","big"]:
    print(f"\n=== target: {target} (leave-one-family-out AUC; 'in-family' = 5-fold within held-out family is not used) ===")
    rows = []
    for name, cols in sets.items():
        r = {"features": name}
        for hold in fams:
            tr, te = df[df.fam != hold], df[df.fam == hold]
            if te[target].nunique() < 2: r[hold] = np.nan; continue
            clf = GradientBoostingClassifier(n_estimators=150, max_depth=3, learning_rate=0.05, random_state=0) if name == "all diagnostics" else make_pipeline(StandardScaler(), LogisticRegression())
            clf.fit(tr[cols], tr[target]); r[hold] = roc_auc_score(te[target], clf.predict_proba(te[cols])[:, 1])
        rows.append(r)
    print(pd.DataFrame(rows).round(3).to_string(index=False))
# risk-coverage under leave-one-family-out for miss_dr
print("\n=== selective reporting: CI miscoverage among tasks the gate keeps (nominal 5%) ===")
out = []
for name, cols in sets.items():
    keep = {50: [], 80: []}; allp = pd.Series(index=df.index, dtype=float)
    for hold in fams:
        tr, te = df[df.fam != hold], df[df.fam == hold]
        clf = GradientBoostingClassifier(n_estimators=150, max_depth=3, learning_rate=0.05, random_state=0) if name == "all diagnostics" else make_pipeline(StandardScaler(), LogisticRegression())
        clf.fit(tr[cols], tr["miss_dr"]); allp[te.index] = clf.predict_proba(te[cols])[:, 1]
    for q in (50, 80):
        thr = np.quantile(allp, q / 100); kept = df[allp <= thr]
        out.append((name, q, len(kept), kept.miss_dr.mean(), kept.groupby("fam").miss_dr.mean().round(2).to_dict()))
print("ungated: miscoverage %.3f" % df.miss_dr.mean(), df.groupby("fam").miss_dr.mean().round(2).to_dict())
for o in out: print(f"{o[0]:18s} keep {o[1]}%: miscoverage {o[3]:.3f}  by family {o[4]}")
# simple rules
for name, mask in [("rule ESS/n>0.3", df.ess > 0.3), ("rule k-hat<0.5", df.khat < 0.5), ("rule k-hat<0.7", df.khat < 0.7), ("rule |mean(w)-1|<0.1", df.lw_dev < 0.1)]:
    k = df[mask]; print(f"{name:22s} keeps {mask.mean():.0%}: miscoverage {k.miss_dr.mean():.3f}  by family {k.groupby('fam').miss_dr.mean().round(2).to_dict()}")
