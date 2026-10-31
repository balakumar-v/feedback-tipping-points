"""Analysis of R14 (Addendum 19). Thresholds as pre-registered. usage: python -m analysis.an_r14"""
import json, glob, numpy as np, pandas as pd
from scipy.stats import beta, norm, mannwhitneyu
def cp(k, n): return np.nan if n == 0 else (1.0 if k == n else beta.ppf(.95, k + 1, n - k))
def auc(score, y):
    s1, s0 = score[y == 1], score[y == 0]
    return mannwhitneyu(s1, s0, alternative="greater").statistic / (len(s1) * len(s0))
D = pd.DataFrame([json.loads(l) for f in sorted(glob.glob("results/round-14/r14_e1_*.jsonl")) for l in open(f)])
D = D.drop_duplicates(["kind", "kappa", "seed"]); print("audits:", len(D))
M = 0.002
D["cls"] = np.where(D.true10 < -M, "worse", np.where(D.true10 > M, "better", "marginal"))
w = D[D.cls == "worse"]; b = D[D.cls == "better"]; nb = w[w.true10.abs() <= 0.01]
print("truly worse", len(w), "near-boundary", len(nb), "truly better", len(b), "marginal", (D.cls == "marginal").sum())
def fa(g, col, val="APPROVE"): return int((g[col] == val).sum())
k = fa(w, "v7"); print("P58a v7 false approvals on truly-worse: %d/%d CP95 upper %.3f (<=0.05?) -> %s" % (k, len(w), cp(k, len(w)), "PASS" if cp(k, len(w)) <= .05 else "FAIL"))
k2 = fa(nb, "v7"); print("P58b near-boundary: %d/%d CP95 upper %.3f (<=0.10?) -> %s" % (k2, len(nb), cp(k2, len(nb)), "PASS" if cp(k2, len(nb)) <= .10 else "FAIL"))
fr = fa(b, "v7", "REJECT"); print("P58c false rejects: %d/%d = %.3f (<=0.10?) -> %s" % (fr, len(b), fr / len(b), "PASS" if fr / len(b) <= .1 else "FAIL"))
ca = fa(b, "v7"); print("P58d correct-approve: %d/%d = %.3f (>=0.25?) -> %s ; abstain %d" % (ca, len(b), ca / len(b), "PASS" if ca / len(b) >= .25 else "FAIL", fa(b, "v7", "NEED")))
print("\n== descriptive, same runs: false approvals on truly-worse / correct-approve on truly-better / false rejects")
rows = []
for name, col in (("single lin", "lin_v"), ("single log", "log_v"), ("single mem7", "mem7_v"), ("single tail2", "tail2_v"), ("free-form alone", "ff_v"), ("v5 four-shape", "v5"), ("v6 +guard", "v6"), ("v7 +veto (final)", "v7")):
    rows.append((name, fa(w, col), cp(fa(w, col), len(w)), fa(nb, col), fa(b, col), fa(b, col, "REJECT")))
one_fa = int((w.one_step_lo > 0).sum()); one_ca = int((b.one_step_lo > 0).sum())
rows.append(("one-step logs gate (SNIPS lower>0)", one_fa, cp(one_fa, len(w)), int((nb.one_step_lo > 0).sum()), one_ca, int((b.one_step_lo <= 0).sum())))
print(pd.DataFrame(rows, columns=["rule", "FA/144", "CP95up", "FA near-bdry/48", "correct-approve/48", "reject-or-not-approve/48"]).round(3).to_string(index=False))
print("\nper cell v7 (A=approve N=need R=reject):")
print(D.groupby(["kind", "kappa"]).apply(lambda g: pd.Series(dict(true=g.true10.iloc[0], A=(g.v7 == "APPROVE").sum(), N=(g.v7 == "NEED").sum(), R=(g.v7 == "REJECT").sum(), v6A=(g.v6 == "APPROVE").sum(), linA=(g.lin_v == "APPROVE").sum(), ffA=(g.ff_v == "APPROVE").sum(), guard_ok=(g.unsup <= .05).mean())), include_groups=False).round(4).to_string())
# margin vs CI-only
E = D[D.cls != "marginal"].copy(); E["y"] = (E.true10 < 0).astype(int)
E["p_margin"] = norm.cdf(E.lin_margin); E["z_ci"] = E.lin_fpt / E.lin_fsd; E["p_ci"] = norm.cdf(-E.z_ci)
br_m = ((E.p_margin - E.y) ** 2).mean(); br_c = ((E.p_ci - E.y) ** 2).mean(); br0 = ((E.y.mean() - E.y) ** 2).mean()
am = auc(E.lin_margin.values, E.y.values); ac = auc(-E.z_ci.values, E.y.values)
print("\nR14-2 on %d non-marginal runs (worse %d): Brier margin %.4f | CI-only %.4f | constant %.4f" % (len(E), E.y.sum(), br_m, br_c, br0))
print("P59a Brier(margin) < constant: %s ; P59b AUC margin %.3f vs CI-only %.3f (margin >= CI-only - 0.02?) -> %s" % (br_m < br0, am, ac, "PASS" if am >= ac - .02 else "FAIL"))
print("per-generator AUC margin / CI-only:", {k: (round(auc(g.lin_margin.values, g.y.values), 3), round(auc(-g.z_ci.values, g.y.values), 3)) for k, g in E.groupby("kind") if 0 < g.y.sum() < len(g)})
nn = E[E.v7 == "NEED"]; print("among v7-NEED runs (n=%d, worse %d): AUC margin %.3f | CI-only %.3f" % (len(nn), nn.y.sum(), auc(nn.lin_margin.values, nn.y.values), auc(-nn.z_ci.values, nn.y.values)))
print("P59a gap: mean(p_margin) %.3f vs base rate %.3f; margin>0 share among worse %.3f, among better %.3f" % (E.p_margin.mean(), E.y.mean(), (E[E.y == 1].lin_margin > 0).mean(), (E[E.y == 0].lin_margin > 0).mean()))
# P59c saved data
A = pd.read_csv("results/round-05/r5_all.csv"); A = A[A.true10.abs() > M]; need = A[A.v3 == "NEED"]; yy = (need.true10 < 0).astype(int).values
print("\nP59c saved R5 runs with 3-shape verdict NEED: n=%d (worse %d): AUC margin %.3f (>=0.70?) -> %s" % (len(need), yy.sum(), auc(need.margin.values, yy), "PASS" if auc(need.margin.values, yy) >= .7 else "FAIL"))
