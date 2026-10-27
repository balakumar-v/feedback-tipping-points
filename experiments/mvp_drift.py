"""MVP check (2): before/after comparison vs one-step OPE under adverse covariate drift (replaces the missing e1_table.py).
usage: [P3_DRIFT_MODE=dir|logit] python -m experiments.mvp_drift SEED0 SEED1 OUT [DRIFT=1.0]
Before: old policy logs (4,000 users, no drift). After: new policy deployed, covariates drift by DRIFT along op.DRIFT_DIR (lowers every item's click rate).
before/after = mean click after - mean click before.  OPE = SNIPS / DR on the BEFORE logs, 95% row bootstrap (B=300).  Truth = new minus old at drift 0 (300k users)."""
import sys, json, os, numpy as np
from p3ope import ope_pilot as op
N, DRIFT, B = 4000, 1.0, 300   # DRIFT is overridden by the optional 4th command-line argument
ALPHA, TAU_OLD, TN = 0.8, 1.0, 0.5   # same logger / candidate as the main audit (p3ope.exp13_lib defaults)
MODE = os.environ.get("P3_DRIFT_MODE", "dir")   # "dir" (covariate shift along DRIFT_DIR) or "logit" (uniform logit shift)
pol = lambda X: op.pi_new(X, TN)

def truth_lift():
    rng = np.random.default_rng(12345)
    return op.truth(pol, rng, alpha=ALPHA, tau=TAU_OLD) - op.truth(pol, rng, alpha=ALPHA, tau=TAU_OLD, old=True)

def after_mean(rng):
    # new policy running in the drifted world. MODE "dir": covariates shift along op.DRIFT_DIR (lowers the AVERAGE logit over items, not every item's);
    # MODE "logit": every item's click logit is lowered by DRIFT (a uniform adverse shift).
    shift = DRIFT * op.DRIFT_DIR if MODE == "dir" else 0.0
    X = rng.normal(size=(N, op.D)) + shift; P = pol(X); a = (P.cumsum(1) > rng.random((N, 1))).argmax(1)
    z = op.logits_r(X) - (DRIFT if MODE == "logit" else 0.0)
    return float((rng.random(N) < op.expit(z)[np.arange(N), a]).mean())

def one(seed, tl):
    rng = np.random.default_rng([seed, 7]); logs = op.sample_logs(N, rng, alpha=ALPHA, tau=TAU_OLD)
    ba = after_mean(rng) - logs["y"].mean()
    P = pol(logs["X"]); Q = op.fit_q(logs["X"], logs["a"], logs["y"], seed=seed); t = op.terms(logs, P, Q); y0 = logs["y"]
    sn = op.estimates(t)["snips"] - y0.mean(); dr = op.estimates(t)["dr"] - y0.mean()
    idx = rng.integers(0, N, size=(B, N)); ym = y0[idx].mean(1)
    sb = t["ipw"][idx].sum(1) / t["w"][idx].sum(1) - ym; db = t["dr"][idx].mean(1) - ym
    (slo, shi), (dlo, dhi) = np.quantile(sb, [.025, .975]), np.quantile(db, [.025, .975])
    return dict(seed=seed, truth=tl, before_after=ba, snips=sn, snips_lo=slo, snips_hi=shi, dr=dr, dr_lo=dlo, dr_hi=dhi,
                ba_wrong_sign=bool(ba < 0 < tl), snips_cov=bool(slo <= tl <= shi), dr_cov=bool(dlo <= tl <= dhi))

if __name__ == "__main__":
    if len(sys.argv) < 4: sys.exit("usage: python -m experiments.mvp_drift SEED0 SEED1 OUT")
    s0, s1, f = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; DRIFT = float(sys.argv[4]) if len(sys.argv) > 4 else DRIFT; tl = truth_lift(); done = set()
    if os.path.exists(f): done = {r["seed"] for r in map(json.loads, open(f))}
    out = open(f, "a")
    for s in range(s0, s1):
        if s not in done: out.write(json.dumps(one(s, tl), default=float) + "\n"); out.flush()
    rs = list(map(json.loads, open(f)))
    print("truth %+.4f runs %d | before/after wrong sign %.3f | SNIPS cover %.3f | DR cover %.3f" % (tl, len(rs),
          np.mean([r["ba_wrong_sign"] for r in rs]), np.mean([r["snips_cov"] for r in rs]), np.mean([r["dr_cov"] for r in rs])))
