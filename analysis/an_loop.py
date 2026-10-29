import json, pandas as pd, numpy as np
df = pd.DataFrame([json.loads(l) for l in open("results/e4_loop.jsonl")]); df["capped"] = df.capped.fillna(False).astype(bool); print("rows", len(df))
for k, x in df.groupby("kappa"):
    need = x[x.v1 == "NEED_DATA"]
    print(f"kappa {k}: true {x.true_lift.iloc[0]:+.4f} {x.cls.iloc[0]} | pilot(1500) verdict: APP {np.mean(x.v1=='APPROVE'):.2f} REJ {np.mean(x.v1=='REJECT'):.2f} NEED {np.mean(x.v1=='NEED_DATA'):.2f} (n={len(x)})")
    if len(need):
        r = need[~need.capped]
        print(f"    NEED n={len(need)}: n* median {need.nstar.median():.0f} IQR [{need.nstar.quantile(.25):.0f},{need.nstar.quantile(.75):.0f}]; over cap 8000: {need.capped.mean():.2f}; n_k median {need.n_k.median():.0f}, n_static median {need.n_static.median():.0f}")
        print(f"    re-audit at min(n*,8000): APP {np.mean(need.v2=='APPROVE'):.2f} REJ {np.mean(need.v2=='REJECT'):.2f} NEED {np.mean(need.v2=='NEED_DATA'):.2f} | uncapped n={len(r)}: decisive {np.mean(r.v2!='NEED_DATA') if len(r) else float('nan'):.2f}")
        wrong = ((need.v2 == 'APPROVE') & (need.true_lift < -0.002)) | ((need.v2 == 'REJECT') & (need.true_lift > 0.002))
        print(f"    wrong verdicts after re-audit: {int(wrong.sum())} of {len(need)}")
tot = df[df.v1 == "NEED_DATA"]; print("ALL NEED:", len(tot), "decisive after n*:", round(np.mean(tot.v2 != "NEED_DATA"), 3), "| uncapped only:", round(np.mean(tot[~tot.capped].v2 != "NEED_DATA"), 3), "n_uncapped", int((~tot.capped).sum()), "| capped share", round(tot.capped.mean(), 3), "| n* median", tot.nstar.median(), "| n* median uncapped", tot[~tot.capped].nstar.median())
w = df[df.cls == "worse"]; fin_w = np.where(w.v1 == "NEED_DATA", w.v2, w.v1)
print("truly-worse n=%d: pilot false-approve %d, final false-approve %d, final REJECT %d" % (len(w), (w.v1 == "APPROVE").sum(), (fin_w == "APPROVE").sum(), (fin_w == "REJECT").sum()))
b = df[df.cls == "better"]; fin = np.where(b.v1 == "NEED_DATA", b.v2, b.v1); print("truly-better n=%d: final APPROVE %.3f REJECT(false) %.3f NEED %.3f" % (len(b), np.mean(fin == "APPROVE"), np.mean(fin == "REJECT"), np.mean(fin == "NEED_DATA")))
