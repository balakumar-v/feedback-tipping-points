"""Post-hoc ablation (panel fixes J3, J2): is four-shape agreement worth it, and what is a verdict worth?

Pools every saved log that stores per-shape verdicts (W4, W5 = generators seen while the rule was built;
W6 = sealed generator, never used for design). All numbers are descriptive and post hoc; they do not
change any pre-registered result.

usage: python -m analysis.an_ablation      (run from the repository root)
"""
import json
import numpy as np
from p3ope.summary import classify, clopper_pearson_upper as cp, load_records

SH = ("lin", "log", "mem7", "tail2")
DESIGN = ["results/r12_e1.jsonl", "results/r12_e1_w4.jsonl"]   # W5, W4: seen during rule building
SEALED = ["results/r14_e1_a.jsonl", "results/r14_e1_b.jsonl"]  # W6: sealed generator
LAMBDAS = (1, 5, 10)          # a false approval costs lambda times its harm


def agree(vs):
    return "APPROVE" if all(v == "APPROVE" for v in vs) else "REJECT" if all(v == "REJECT" for v in vs) else "NEED"


def rule_table(rs):
    """name -> list of verdicts, one per audit."""
    out = {}
    for s in SH:
        out[f"single shape {s}"] = [r[f"{s}_v"] for r in rs]
    out["free-form model alone"] = [r["ff_v"] for r in rs]
    four = [agree([r[f"{s}_v"] for s in SH]) for r in rs]
    out["four-shape agreement"] = four
    g = [("NEED" if v == "APPROVE" and r["unsup"] > .05 else v) for v, r in zip(four, rs)]
    out["four + coverage guard"] = g
    out["four + guard + veto (final v7)"] = [("NEED" if v == "APPROVE" and r["ff_v"] != "APPROVE" else v) for v, r in zip(g, rs)]
    return out


def score(rs, verdicts):
    worse = [(r, v) for r, v in zip(rs, verdicts) if classify(r["true10"]) == "worse"]
    better = [(r, v) for r, v in zip(rs, verdicts) if classify(r["true10"]) == "better"]
    fa = sum(v == "APPROVE" for _, v in worse)
    ca = sum(v == "APPROVE" for _, v in better)
    fr = sum(v == "REJECT" for _, v in better)
    return dict(fa=fa, nw=len(worse), up=cp(fa, len(worse)), ca=ca, nb=len(better), fr=fr)


def decision_value(rs, verdicts, lam):
    """Mean per-audit value in click-lift units: approve -> gain true10 (harm counted lam times); else 0."""
    tot = 0.0
    for r, v in zip(rs, verdicts):
        if v == "APPROVE":
            tot += r["true10"] if r["true10"] > 0 else lam * r["true10"]
    return tot / len(rs)


def report(title, rs):
    print(f"\n## {title}: {len(rs)} audits")
    t = rule_table(rs)
    t["one-step SNIPS gate (lower>0)"] = ["APPROVE" if r.get("one_step_lo", -1) > 0 else "NEED" for r in rs] if "one_step_lo" in rs[0] else None
    oracle = [("APPROVE" if r["true10"] > 0 else "REJECT") for r in rs]
    print(f"{'rule':34s} {'false-appr':>11s} {'CP95up':>7s} {'corr-appr':>10s} {'false-rej':>9s} " + " ".join(f"value(l={l})" for l in LAMBDAS))
    for name, vs in t.items():
        if vs is None:
            continue
        s = score(rs, vs)
        vals = " ".join(f"{decision_value(rs, vs, l):+10.4f}" for l in LAMBDAS)
        print(f"{name:34s} {s['fa']:>4d}/{s['nw']:<5d} {s['up']:7.3f} {s['ca']:>4d}/{s['nb']:<5d} {s['fr']:>9d} {vals}")
    print(f"{'oracle (approve iff truly better)':34s} {'':>11s} {'':>7s} {'':>10s} {'':>9s} " + " ".join(f"{decision_value(rs, oracle, l):+10.4f}" for l in LAMBDAS))
    return t


def margin_rule(rs, z=1.645):
    """Single best shape (lin) plus the tipping margin: approve only if lin approves AND kappa-hat is z SEs below kappa*."""
    out = []
    for r in rs:
        v = r["lin_v"]
        if v == "APPROVE" and not (r["lin_margin"] < -z):
            v = "NEED"
        out.append(v)
    return out


if __name__ == "__main__":
    des = [r for f in DESIGN for r in load_records(f)]
    sealed = [r for f in SEALED for r in load_records(f)]
    report("Generators used while building the rule (W4 + W5)", des)
    report("Sealed generator W6 (hump, log-square, sigmoid)", sealed)
    m = margin_rule(sealed)
    s = score(sealed, m)
    print(f"\nSingle shape lin + tipping margin (kappa-hat at least 1.645 SE below kappa*), W6: "
          f"false-approve {s['fa']}/{s['nw']} (CP95 upper {s['up']:.3f}), correct-approve {s['ca']}/{s['nb']}")
    pooled = des + sealed
    print(f"\nRead with care: the pooled set has {len(pooled)} audits from 3 generators built by the same team; "
          "descriptive only, not a new pre-registered test.")
