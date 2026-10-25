"""Headline statistics computed from the raw run logs in ``results/`` (no pandas needed).

The numbers are the same ones ``analysis/an_r12.py`` prints; ``tests/`` checks that they match.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict

from scipy.stats import beta as _Beta

MARGIN = 0.002        # |true 10-round lift| <= MARGIN counts as "marginal"
NEAR_BOUNDARY = 0.01  # "near boundary" = truly worse, but only slightly


def clopper_pearson_upper(x: int, n: int, conf: float = 0.95) -> float:
    """One-sided exact binomial upper bound (1.0 when every trial failed)."""
    return 1.0 if x >= n else float(_Beta.ppf(conf, x + 1, n - x))


def load_records(path: str) -> list:
    if not os.path.exists(path):
        raise FileNotFoundError(f"result log not found: {path} (run from the repository root)")
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def classify(true10: float) -> str:
    return "worse" if true10 < -MARGIN else "better" if true10 > MARGIN else "marginal"


def headline(records: list, rule: str) -> dict:
    """False approvals, false rejects and correct approvals for one rule column (e.g. 'v7')."""
    worse = [r for r in records if classify(r["true10"]) == "worse"]
    near = [r for r in worse if abs(r["true10"]) <= NEAR_BOUNDARY]
    better = [r for r in records if classify(r["true10"]) == "better"]
    fa = sum(r[rule] == "APPROVE" for r in worse)
    fa_near = sum(r[rule] == "APPROVE" for r in near)
    fr = sum(r[rule] == "REJECT" for r in better)
    ca = sum(r[rule] == "APPROVE" for r in better)
    return dict(rule=rule, runs=len(records),
                false_approve=fa, n_worse=len(worse), fa_upper=clopper_pearson_upper(fa, len(worse)),
                near_false_approve=fa_near, n_near=len(near), near_upper=clopper_pearson_upper(fa_near, len(near)),
                false_reject=fr, n_better=len(better), correct_approve=ca,
                correct_approve_rate=ca / max(len(better), 1))


def cells(records: list, rules=("v6", "v7")) -> list:
    """One row per (shape, kappa) cell with verdict counts for each rule."""
    grp = defaultdict(list)
    for r in records:
        grp[(r["kind"], r["kappa"], r["true10"])].append(r)
    rows = []
    for (kind, kappa, t), rs in sorted(grp.items()):
        rows.append(dict(kind=kind, kappa=kappa, true10=t, cls=classify(t), n=len(rs),
                         **{rule: dict(Counter(x[rule] for x in rs)) for rule in rules}))
    return rows
