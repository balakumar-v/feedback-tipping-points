"""Analysis of R15 (Addendum 20). Thresholds as pre-registered. usage: python -m analysis.an_r15"""
import json, glob, os, numpy as np, pandas as pd
from scipy.stats import beta


def cp(k, n): return np.nan if n == 0 else (1.0 if k == n else float(beta.ppf(.95, k + 1, n - k)))


def load(pat): return pd.DataFrame([json.loads(l) for f in sorted(glob.glob(pat)) for l in open(f)])


def r15_1():
    D = load("results/round-15/r15_e1.jsonl")
    if not len(D): print("R15-1: no runs"); return
    D = D.drop_duplicates(["world", "seed"]); M = 0.002
    D["cls"] = np.where(D.true10 < -M, "worse", np.where(D.true10 > M, "better", "marginal"))
    w = D[D.cls == "worse"]; b = D[D.cls == "better"]; nb = w[w.true10.abs() <= 0.01]
    print("R15-1 W7: audits %d, worlds %d (worse %d, better %d, marginal %d); audits worse %d, near-boundary %d, better %d" % (
        len(D), D.world.nunique(), w.world.nunique(), b.world.nunique(), D[D.cls == "marginal"].world.nunique(), len(w), len(nb), len(b)))
    k = int((w.v7 == "APPROVE").sum()); lim = int(np.floor(.05 * len(w)))
    print("P60a false approvals %d/%d (limit %d), CP95 upper %.3f -> %s" % (k, len(w), lim, cp(k, len(w)), "PASS" if k <= lim else "FAIL"))
    k2 = int((nb.v7 == "APPROVE").sum()); lim2 = int(np.floor(.10 * len(nb)))
    print("P60b near-boundary %d/%d (limit %d) -> %s" % (k2, len(nb), lim2, "PASS" if k2 <= lim2 else "FAIL"))
    fr = int((b.v7 == "REJECT").sum()); print("P60c false rejects %d/%d = %.3f -> %s" % (fr, len(b), fr / max(len(b), 1), "PASS" if fr / max(len(b), 1) <= .1 else "FAIL"))
    ca = int((b.v7 == "APPROVE").sum()); print("P60d correct approve %d/%d = %.3f -> %s (abstain %d)" % (ca, len(b), ca / max(len(b), 1), "PASS" if ca / max(len(b), 1) >= .25 else "FAIL", int((b.v7 == "NEED").sum())))
    fw = w.groupby("world").v7.apply(lambda s: (s == "APPROVE").any()); kw = int(fw.sum())
    print("P60e worlds with any false approval %d/%d, world-level CP95 upper %.3f -> %s" % (kw, len(fw), cp(kw, len(fw)), "PASS" if kw <= 1 else "FAIL"))
    print("\nrule comparison on the same audits (false approvals on worse | near-boundary | correct approve on better | false rejects)")
    rows = []
    for name, col in (("single lin", "lin_v"), ("single log", "log_v"), ("single mem7", "mem7_v"), ("single tail2", "tail2_v"), ("free-form alone", "ff_v"), ("v5 four-shape", "v5"), ("v6 +guard", "v6"), ("v7 final", "v7")):
        rows.append((name, int((w[col] == "APPROVE").sum()), int((nb[col] == "APPROVE").sum()), int((b[col] == "APPROVE").sum()), int((b[col] == "REJECT").sum())))
    rows.append(("one-step logs gate", int((w.one_step_lo > 0).sum()), int((nb.one_step_lo > 0).sum()), int((b.one_step_lo > 0).sum()), int((b.one_step_lo <= 0).sum())))
    print(pd.DataFrame(rows, columns=["rule", "FA/%d" % len(w), "FA near-bdry/%d" % len(nb), "correct-approve/%d" % len(b), "reject-or-not/%d" % len(b)]).to_string(index=False))
    print("\nper world (true lift; A/N/R of v7 over its audits; guard ok share):")
    print(D.groupby("world").apply(lambda g: pd.Series(dict(kappa=g.kappa.iloc[0], true=round(g.true10.iloc[0], 4), A=(g.v7 == "APPROVE").sum(), N=(g.v7 == "NEED").sum(), R=(g.v7 == "REJECT").sum(), ff_A=(g.ff_v == "APPROVE").sum(), guard=(g.unsup <= .05).mean())), include_groups=False).to_string())


def r14_worlds():
    D = load("results/round-14/r14_e1_*.jsonl").drop_duplicates(["kind", "kappa", "seed"]); w = D[D.true10 < -0.002]
    c = w.groupby(["kind", "kappa"]).v7.apply(lambda s: (s == "APPROVE").any()); k = int(c.sum())
    print("\nR14 effective independent worlds: %d audits = %d worlds (cells) x %d fresh datasets; truly-worse worlds %d; worlds with a false approval %d; world-level CP95 upper %.3f (audit-level 0/%d bound %.3f)" % (
        len(D), D.groupby(["kind", "kappa"]).ngroups, len(D) // D.groupby(["kind", "kappa"]).ngroups, len(c), k, cp(k, len(c)), len(w), cp(int((w.v7 == "APPROVE").sum()), len(w))))


def r15_2():
    N = load("results/round-15/r15_e2.jsonl")
    if not len(N): print("\nR15-2: no runs"); return
    O = load("results/round-14/r14_e1_*.jsonl").drop_duplicates(["kind", "kappa", "seed"])
    M = N.merge(O, on=["kind", "kappa", "seed"], suffixes=("_B", "_30"))
    nd = int((M.v7_B != M.v7_30).sum()); w = M[M.true10_30 < -0.002]; fa = int((w.v7_B == "APPROVE").sum())
    print("\nR15-2 B=%d vs B=30 on %d identical datasets: v7 verdict changed in %d (limit 4) -> %s ; false approvals at B=%d: %d/%d -> %s" % (
        int(N.B.iloc[0]), len(M), nd, "PASS" if nd <= 4 else "FAIL", int(N.B.iloc[0]), fa, len(w), "PASS" if fa == 0 else "FAIL"))
    for s in ("lin", "log", "mem7", "tail2", "ff"):
        print("  %-5s forecast lower end: mean |change| %.4f ; width ratio B/30 %.2f ; sign of change mean %+.4f" % (s, (M[f"{s}_flo_B"] - M[f"{s}_flo_30"]).abs().mean(), ((M[f"{s}_fhi_B"] - M[f"{s}_flo_B"]) / (M[f"{s}_fhi_30"] - M[f"{s}_flo_30"])).mean(), (M[f"{s}_flo_B"] - M[f"{s}_flo_30"]).mean()))
    print("  verdict table (rows B=30, cols B=%d):" % int(N.B.iloc[0])); print(pd.crosstab(M.v7_30, M.v7_B).to_string())


def r15_3():
    f = "results/round-15/r15_e3.jsonl"
    if os.path.exists(f):
        print("\nR15-3 (post hoc) slice kappa-hat bias, true kappa 0.8:")
        for r in map(json.loads, open(f)): print("  taste x%.0f: pooled %+.3f | true hidden term supplied %+.3f | attenuation formula %+.3f" % (r["taste"], r["pooled_bias"], r["oracle_bias"], r["attenuation_formula_bias"]))


if __name__ == "__main__":
    r15_1(); r14_worlds(); r15_2(); r15_3()
