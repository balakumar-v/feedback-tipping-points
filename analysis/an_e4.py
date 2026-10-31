import json, numpy as np, pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
df = pd.DataFrame([json.loads(l) for l in open("results/round-01/e4_sizing.jsonl")]); print("rows", len(df))
rows = []
for (m, ns), x in df.groupby(["m", "ns"]):
    rows.append(dict(m=m, ns=ns, kb_bias=(x.kb - 0.4).mean(), ks_bias=(x.ks - 0.4).mean(), ks_sd=x.ks.std(), c_sd_sqrt_n=x.ks.std() * np.sqrt(ns), ks_se=x.ses.mean(), ks_cov=x.ks_in_ci.mean(),
                     kappa_test_power=(x.zk.abs() > 1.96).mean(), bulk_static_bias=x.sn_bias.mean(), slice_static_bias=x.vs_bias.mean(), static_test_power=(x.zs.abs() > 1.96).mean()))
print(pd.DataFrame(rows).to_string(float_format=lambda v: "%.3f" % v))
for m in (1.0, 2.0):
    x0 = df[df.m == m]; print("\nm", m, "true 10-round lift %.4f" % x0.true_lift.iloc[0]); r2 = []
    for ns, y in x0.groupby("ns"):
        eb, eh, es = (y.fc_bulk - y.true_lift).abs(), (y.fc_hyb - y.true_lift).abs(), (y.fc_slice - y.true_lift).abs()
        r2.append(dict(ns=ns, err_bulk=eb.mean(), err_hyb=eh.mean(), err_slice=es.mean(), slice_beats_hyb=(es < eh).mean(), slice_beats_bulk=(es < eb).mean(),
                       sign_err_bulk=((y.fc_bulk > 0) != (y.true_lift > 0)).mean(), sign_err_hyb=((y.fc_hyb > 0) != (y.true_lift > 0)).mean(), sign_err_slice=((y.fc_slice > 0) != (y.true_lift > 0)).mean()))
    print(pd.DataFrame(r2).to_string(float_format=lambda v: "%.3f" % v))
