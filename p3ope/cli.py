"""Command-line interface:  python -m p3ope {demo,audit,ope,summary,report,kinds}  (run from the repo root)."""
from __future__ import annotations

import argparse
import json
import sys

from p3ope import summary as S

BAR = "-" * 66


def _err(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _fmt_report(r) -> str:
    L = [BAR, f" Scenario : fatigue shape '{r.kind}', kappa = {r.kappa:g}, seed = {r.seed}",
         " Data     : 4,000 logged users (old policy) + 3,000-user randomised slice (simulated)", BAR,
         f" {'model':<7}{'verdict':<9}{'static lift >=':>15}{'10-round forecast':>20}   95% interval"]
    for name, s in r.shapes.items():
        L.append(f" {name:<7}{s.verdict:<9}{s.static_lift_lo:>+15.4f}{s.forecast_lift:>+20.4f}   [{s.forecast_lo:+.4f}, {s.forecast_hi:+.4f}]")
    L += [BAR, f" Rule v5 (4 shapes agree)      : {r.verdict_v5}",
          f" Rule v6 (+ coverage guard)    : {r.verdict_v6}   (unsupported exposure {r.unsupported_share:.1%}, limit 5%)",
          f" Rule v7 (+ free-form veto)    : {r.verdict}", BAR]
    if r.one_step_snips is not None:
        L.append(f" A one-step (static) estimate would say : lift {r.one_step_snips:+.4f}")
    if r.true_lift is not None:
        L.append(f" Simulator ground truth (10 rounds)     : lift {r.true_lift:+.4f}  ({'better' if r.true_lift > 0 else 'worse'} than the old policy)")
    L += [f"\n VERDICT: {r.verdict_label}" + (f"   [{r.outcome}]" if r.outcome else ""), f" ({r.seconds:.0f} s)"]
    return "\n".join(L)


def cmd_audit(a) -> int:
    from p3ope.audit import run_audit
    try:
        rep = run_audit(a.kind, a.kappa, a.seed, with_truth=not a.no_truth, progress=None if a.json else _err)
    except ValueError as e:
        _err(f"error: {e}")
        return 2
    print(json.dumps(rep.to_dict(), indent=2) if a.json else _fmt_report(rep))
    return 0


def cmd_demo(a) -> int:
    from p3ope.audit import run_audit
    print("DEMO - the same audit on two simulated policies. Each run takes about 10-15 s.\n")
    scenarios = [("cubic", 0.5, 1, "Looks fine to one-step OPE, but users tire of repeats: truly WORSE"),
                 ("q2", 0.1, 1, "Mild fatigue: truly BETTER")]
    for kind, kappa, seed, why in scenarios:
        print(f"## {why}")
        print(_fmt_report(run_audit(kind, kappa, seed, progress=_err)), "\n")
    print("Reading the result: a bad policy must never be APPROVED; a good one may be approved or sent for more data.")
    return 0


def cmd_ope(a) -> int:
    """MVP baseline: one-step IPW / SNIPS / DM / DR on the simulator (no fatigue), next to the exact truth."""
    import numpy as np
    from p3ope import ope_pilot as op
    if a.n < 200:
        _err("error: --n must be at least 200")
        return 2
    rng = np.random.default_rng(a.seed)
    logs = op.sample_logs(a.n, rng, beta=a.beta, gamma=a.gamma)
    probs = op.pi_new(logs["X"])
    est = op.estimates(op.terms(logs, probs, op.fit_q(logs["X"], logs["a"], logs["y"])))
    v_new = op.truth(op.pi_new, np.random.default_rng(a.seed + 1), gamma=a.gamma, beta=a.beta)
    v_old = op.truth(None, np.random.default_rng(a.seed + 1), gamma=a.gamma, beta=a.beta, old=True)
    old_obs = float(logs["y"].mean())
    print(f"One-step off-policy evaluation, {a.n:,} logged users, hidden-taste strength beta={a.beta:g}, gamma={a.gamma:g} (simulator)")
    print(f"  {'estimator':<10}{'new-policy value':>18}{'lift vs old':>14}")
    for name in ("ipw", "snips", "dm", "dr"):
        print(f"  {name.upper():<10}{est[name]:>18.4f}{est[name] - old_obs:>+14.4f}")
    print(f"  {'TRUTH':<10}{v_new:>18.4f}{v_new - v_old:>+14.4f}   (exact, by Monte Carlo)")
    print(f"  effective sample size {op.ess(op.terms(logs, probs)['w']):.0f} of {a.n}")
    if a.beta:
        print("  Hidden taste drives both the old policy's choice and the click, so these estimates are biased.")
    return 0


def cmd_summary(a) -> int:
    try:
        for path, tag in (("results/r12_e1.jsonl", "W5 held-out generator (pre-registered)"),
                          ("results/r12_e1_w4.jsonl", "W4 retro (descriptive)")):
            recs = S.load_records(path)
            print(f"\n== {tag}: {len(recs)} logged audits")
            for rule in ("v6", "v7"):
                h = S.headline(recs, rule)
                print(f"  {rule}: false approvals {h['false_approve']}/{h['n_worse']} (95% upper {h['fa_upper']:.3f}) | "
                      f"near-boundary {h['near_false_approve']}/{h['n_near']} | false rejects {h['false_reject']}/{h['n_better']} | "
                      f"correct approves {h['correct_approve']}/{h['n_better']} = {h['correct_approve_rate']:.2f}")
    except FileNotFoundError as e:
        _err(f"error: {e}")
        return 1
    return 0


def cmd_report(a) -> int:
    from p3ope.report import build
    try:
        print("wrote", build(a.out))
    except FileNotFoundError as e:
        _err(f"error: {e}")
        return 1
    return 0


def cmd_kinds(a) -> int:
    from p3ope.audit import KINDS
    print("Available fatigue shapes:", ", ".join(KINDS))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m p3ope", description="Measured-feedback tipping-point audit (simulator).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="run two audits end to end (~30 s)").set_defaults(fn=cmd_demo)
    q = sub.add_parser("audit", help="audit one simulated scenario")
    q.add_argument("--kind", default="cubic", help="fatigue shape (see `kinds`)")
    q.add_argument("--kappa", type=float, default=0.2, help="fatigue strength (>= 0)")
    q.add_argument("--seed", type=int, default=0)
    q.add_argument("--no-truth", action="store_true", help="skip the ground-truth computation")
    q.add_argument("--json", action="store_true", help="machine-readable output")
    q.set_defaults(fn=cmd_audit)
    o = sub.add_parser("ope", help="one-step IPW/SNIPS/DM/DR baseline vs ground truth (no fatigue)")
    o.add_argument("--n", type=int, default=20000)
    o.add_argument("--beta", type=float, default=0.0, help="hidden-taste strength in the old policy (0 = no confounding)")
    o.add_argument("--gamma", type=float, default=0.0, help="hidden-taste strength in the clicks")
    o.add_argument("--seed", type=int, default=0)
    o.set_defaults(fn=cmd_ope)
    sub.add_parser("summary", help="headline numbers from the logged runs").set_defaults(fn=cmd_summary)
    r = sub.add_parser("report", help="build the self-contained HTML dashboard from the logs")
    r.add_argument("--out", default="docs/dashboard.html")
    r.set_defaults(fn=cmd_report)
    sub.add_parser("kinds", help="list fatigue shapes").set_defaults(fn=cmd_kinds)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
