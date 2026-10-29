import json, glob, numpy as np, pandas as pd, sys
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
rows = [json.loads(l) for f in glob.glob("results/w2_*.jsonl") if "smoke" not in f for l in open(f)]
df = pd.DataFrame(rows); df["cls"] = np.where(df.true_lift < -0.002, "worse", np.where(df.true_lift > 0.002, "better", "marg"))
df["grp"] = df.cell.str[0]
def fa(v, cls, col="v_logs"):
    s = df[df.cell == v] if False else None
g = df.groupby("cell", sort=False)
def summ(x):
    c = x.cls.iloc[0]; n = len(x); r = dict(n=n, true=x.true_lift.iloc[0], cls=c, kh=x.kh.mean(), kh_bias=(x.kh - x.kappa).mean(), kh_sd=x.kh.std(),
        cov=((x.k_lo <= x.kappa) & (x.kappa <= x.k_hi)).mean(), kstar=x.kstar.replace(np.inf, np.nan).mean(), kstar_true=x.kstar_true.iloc[0],
        fc=x.fc_lift.mean(), fc_sign_err=((x.fc_lift > 0) != (x.true_lift > 0)).mean(),
        APP=(x.v_logs == "APPROVE").mean(), REJ=(x.v_logs == "REJECT").mean(), NEED=(x.v_logs == "NEED_DATA").mean(), onestepAPP=(x.v_onestep == "APPROVE").mean())
    if "v_slice" in x and x.v_slice.notna().any():
        r.update(ks_bias=(x.ks - x.kappa).mean(), ks_sd=x.ks.std(), sAPP=(x.v_slice == "APPROVE").mean(), sREJ=(x.v_slice == "REJECT").mean(), sNEED=(x.v_slice == "NEED_DATA").mean(),
                 fc_s=x.fc_lift_s.mean(), fc_h=x.fc_lift_h.mean(), err_b=(x.fc_lift - x.true_lift).abs().mean(), err_s=(x.fc_lift_s - x.true_lift).abs().mean(), err_h=(x.fc_lift_h - x.true_lift).abs().mean())
    return pd.Series(r)
T = pd.DataFrame({k: summ(x).to_dict() for k, x in g}).T; print(T.to_string(float_format=lambda v: "%.3f" % v if isinstance(v, float) else str(v)))
def rate(sub, col, val): return (sub[col] == val).mean() if len(sub) else np.nan
print("\n=== pooled claims ===")
A = df[df.grp == "A"]; Aw = A[A.cls == "worse"]
print("P1 per-cell mean|kh-k|:", A.groupby("cell").apply(lambda x: (x.kh - x.kappa).abs().mean()).round(3).to_dict())
print("P1 pooled CI coverage (A):", round(((A.k_lo <= A.kappa) & (A.kappa <= A.k_hi)).mean(), 3), "n", len(A))
print("P2 A truly-worse n=%d: three-way false-approval %.3f | one-step false-approval %.3f | REJECT %.3f NEED %.3f" % (len(Aw), rate(Aw, "v_logs", "APPROVE"), rate(Aw, "v_onestep", "APPROVE"), rate(Aw, "v_logs", "REJECT"), rate(Aw, "v_logs", "NEED_DATA")))
Ab = A[A.cls == "better"]; print("   A truly-better n=%d: APPROVE %.3f REJECT(false) %.3f NEED %.3f; one-step APPROVE %.3f" % (len(Ab), rate(Ab, "v_logs", "APPROVE"), rate(Ab, "v_logs", "REJECT"), rate(Ab, "v_logs", "NEED_DATA"), rate(Ab, "v_onestep", "APPROVE")))
far = A[(A.kappa - A.kstar_true).abs() >= 0.2]; print("   far-from-tipping cells (|k-k*|>=0.2) n=%d NEED rate %.3f" % (len(far), rate(far, "v_logs", "NEED_DATA")))
Af = A[A.kstar.replace(np.inf, np.nan).notna()]; print("P3 |kstar-kstar_true|<=0.10 frac: %.3f (n=%d)" % (((Af.kstar - Af.kstar_true).abs() <= 0.10).mean(), len(Af)))
Bd = df[df.grp == "B"]; Bw = Bd[Bd.cls == "worse"]
print("P4 B logs-only: kh bias per cell", Bd.groupby("cell").apply(lambda x: (x.kh - x.kappa).mean()).round(3).to_dict())
print("   B truly-worse n=%d: three-way false-approval %.3f | one-step false-approval %.3f | REJECT %.3f NEED %.3f" % (len(Bw), rate(Bw, "v_logs", "APPROVE"), rate(Bw, "v_onestep", "APPROVE"), rate(Bw, "v_logs", "REJECT"), rate(Bw, "v_logs", "NEED_DATA")))
print("P5 B slice: ks bias per cell", Bd.groupby("cell").apply(lambda x: (x.ks - x.kappa).mean()).round(3).to_dict())
print("   B truly-worse: slice-audit false-approval %.3f REJECT %.3f NEED %.3f" % (rate(Bw, "v_slice", "APPROVE"), rate(Bw, "v_slice", "REJECT"), rate(Bw, "v_slice", "NEED_DATA")))
Bb = Bd[Bd.cls == "better"]; print("   B truly-better n=%d: slice APPROVE %.3f REJECT %.3f NEED %.3f | logs APPROVE %.3f" % (len(Bb), rate(Bb, "v_slice", "APPROVE"), rate(Bb, "v_slice", "REJECT"), rate(Bb, "v_slice", "NEED_DATA"), rate(Bb, "v_logs", "APPROVE")))
print("P11 (B, kappa=.4 cell) whole-slice vs hybrid vs bulk |err| wins:")
for cell, x in Bd.groupby("cell"):
    eb, es, eh = (x.fc_lift - x.true_lift).abs(), (x.fc_lift_s - x.true_lift).abs(), (x.fc_lift_h - x.true_lift).abs()
    print("   %s slice<hyb %.2f slice<bulk %.2f | mean|err| bulk %.4f hyb %.4f slice %.4f" % (cell, (es < eh).mean(), (es < eb).mean(), eb.mean(), eh.mean(), es.mean()))
for gname in ("C", "F", "D", "G", "E"):
    X = df[df.grp == gname]; Xw = X[X.cls == "worse"]
    print(f"P6/7 group {gname}: n={len(X)} truly-worse n={len(Xw)}: false-approval {rate(Xw,'v_logs','APPROVE'):.3f}; one-step false-approval {rate(Xw,'v_onestep','APPROVE'):.3f}; truly-better n={(X.cls=='better').sum()}: false-reject {rate(X[X.cls=='better'],'v_logs','REJECT'):.3f}; forecast sign error {((X.fc_lift>0)!=(X.true_lift>0)).mean():.3f}")
