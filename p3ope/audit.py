"""One-call entry point for the final audit rule (v7).

This module does NOT add new statistics. It wires together the pieces that were
frozen in Rounds 11-12 so that the audit can be run, explained and demonstrated
from a single function:

    from p3ope.audit import run_audit
    report = run_audit("cubic", 0.2, seed=1)
    print(report.verdict)            # APPROVE | REJECT | NEED_DATA

Pipeline (identical to ``experiments/r12_e1.one``, so a run with the same
kind / kappa / seed reproduces the logged record in ``results/r12_e1.jsonl``):

1. Simulate 4,000 users of *logged* data from the old policy (hidden taste drives
   both the old policy's choices and the clicks).
2. Simulate a 3,000-user randomised *slice* (10 rounds, repeat-heavy design with
   known propensities).
3. For each of four fatigue shapes (lin, log, mem7, tail2) plus a free-form
   count-curve model (ff): fit on the slice, bootstrap users, and ask whether
   BOTH the static lift and the 10-round forecast lift are clearly > 0 (APPROVE),
   clearly <= 0 (REJECT) or neither (NEED).
4. Combine: all four shapes must agree (rule v5); a coverage guard blocks APPROVE
   if the slice never saw the repeat counts the new policy produces (v6); the
   free-form model can veto an APPROVE (v7).

Everything here is simulator-based: the "ground truth" is known only because the
simulator is ours. Nothing in this module touches real user data.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Callable, Optional

import numpy as np

from p3ope import r2_lib as R
from p3ope import r8_lib as W
from experiments import r11_e1 as Q          # coverage guard (rule v6)
from experiments import r12_e1 as F          # audit() with the free-form model (rule v7)
from experiments.r2_e5 import comb           # "all shapes agree" combiner

SHAPES = F.SH                                 # ("lin", "log", "mem7", "tail2")
BASE_KINDS = ("lin", "log", "mem7", "sat", "convex", "quad", "kink", "tail2", "decay", "window")
KINDS = tuple(W.NEW_SHAPES) + BASE_KINDS      # every fatigue shape the simulator can generate
GUARD_LIMIT = 0.05                            # max share of new-policy exposure the slice may leave unsupported
VERDICT_LABEL = {"APPROVE": "APPROVE", "REJECT": "REJECT", "NEED": "NEED RANDOMIZED DATA"}


@dataclass
class ShapeResult:
    """Outcome of one fatigue model on the slice."""
    shape: str
    verdict: str            # APPROVE | REJECT | NEED
    static_lift_lo: float   # lower 95% bound of the static (round-0) lift
    forecast_lift: float    # point forecast of the 10-round lift
    forecast_lo: float      # 95% bootstrap interval of the forecast
    forecast_hi: float


@dataclass
class AuditReport:
    kind: str
    kappa: float
    seed: int
    verdict: str                              # final (rule v7): APPROVE | REJECT | NEED
    verdict_v5: str                           # four shapes agree
    verdict_v6: str                           # + coverage guard
    unsupported_share: float                  # new-policy exposure the slice has no data for
    guard_ok: bool
    shapes: dict = field(default_factory=dict)   # name -> ShapeResult (lin, log, mem7, tail2, ff)
    one_step_snips: Optional[float] = None    # what a one-step (static) estimate says
    true_lift: Optional[float] = None         # simulator ground truth (10-round lift)
    seconds: float = 0.0

    @property
    def verdict_label(self) -> str:
        return VERDICT_LABEL[self.verdict]

    @property
    def outcome(self) -> Optional[str]:
        """Compare the verdict with the simulator truth (None if truth not computed)."""
        if self.true_lift is None:
            return None
        if self.verdict == "NEED":
            return "abstained"
        good = self.true_lift > 0
        return "correct" if (self.verdict == "APPROVE") == good else "WRONG"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["verdict_label"], d["outcome"] = self.verdict_label, self.outcome
        return d


def validate(kind: str, kappa: float, seed: int) -> None:
    if kind not in KINDS:
        raise ValueError(f"unknown fatigue shape {kind!r}; choose one of: {', '.join(KINDS)}")
    if not isinstance(kappa, (int, float)) or not np.isfinite(kappa) or kappa < 0:
        raise ValueError(f"kappa must be a finite number >= 0 (got {kappa!r})")
    if not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError(f"seed must be a non-negative integer (got {seed!r})")


def run_audit(kind: str, kappa: float, seed: int = 0, with_truth: bool = True,
              progress: Optional[Callable[[str], None]] = None) -> AuditReport:
    """Run the final audit on one simulated scenario (about 10-15 s on one CPU core)."""
    validate(kind, kappa, seed)
    say = progress or (lambda msg: None)
    t0 = time.time()
    beta, gamma = F.beta, F.gamma
    cid = sum(map(ord, f"{kind}{kappa}"))     # same stream ids as experiments/r12_e1.one -> reproducible

    say(f"simulating {F.NB:,} logged users and a {F.NS:,}-user randomised slice")
    db = W.sim_w3(F.NB, np.random.default_rng([seed, cid, 411]), kind, kappa, beta, gamma, "old")
    ds = W.sim_w3(F.NS, np.random.default_rng([seed, cid, F.NS, 412]), kind, kappa, beta, gamma, "tail", T=F.TS)

    say("fitting 4 fatigue shapes + free-form model, bootstrapping users")
    res = F.audit(db, ds)
    _, unsupported = Q.guard(ds)

    v5 = comb([res[s]["v"] for s in SHAPES])
    v6 = "NEED" if (v5 == "APPROVE" and unsupported > GUARD_LIMIT) else v5
    v7 = "NEED" if (v6 == "APPROVE" and res["ff"]["v"] != "APPROVE") else v6

    shapes = {s: ShapeResult(s, res[s]["v"], res[s]["slo"], res[s]["fpt"], res[s]["flo"], res[s]["fhi"])
              for s in SHAPES + ("ff",)}
    report = AuditReport(kind, float(kappa), int(seed), v7, v5, v6, float(unsupported),
                         unsupported <= GUARD_LIMIT, shapes,
                         one_step_snips=float(R.snips0(db)[0]))
    if with_truth:
        say("computing simulator ground truth (60,000 users)")
        report.true_lift = float(W.true_lift_w3(kind, kappa, beta, gamma))
    report.seconds = round(time.time() - t0, 1)
    return report
