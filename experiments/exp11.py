"""Feedback-trap check suggested by the other report: does a one-step OPE lift survive repeated exposure?
Mechanism (an assumption, labelled as such): each repeat exposure of an action to the same user lowers its reward logit by kappa (fatigue).
Round-0 reward is fatigue-free, so one-step OPE on round-0 logs sees the static lift."""
import numpy as np
from p3ope import ope_pilot as op
from p3ope.ope_pilot import *
op.NL = 0.0
rng = np.random.default_rng(1313)
N, T, ALPHA, TAU_OLD, TN = 20000, 10, 0.8, 1.0, 0.5
X = rng.normal(size=(N, D))
base = logits_r(X)
def run(policy_probs_fn, kappa, rng):
    counts = np.zeros((N, K)); rew = []
    for t in range(T):
        P = policy_probs_fn(X)
        a = (P.cumsum(1) > rng.random((N, 1))).argmax(1)
        z = base[np.arange(N), a] - kappa * counts[np.arange(N), a]
        y = (rng.random(N) < expit(z)).astype(float); rew.append(y.mean()); counts[np.arange(N), a] += 1
    return np.array(rew)
old = lambda X: pi_old_full(X, None, ALPHA, TAU_OLD); new = lambda X: pi_new(X, TN)
print("kappa | round-0 lift (what one-step OPE estimates) | cumulative lift over 10 rounds (mean per round) | last-round lift")
for kappa in [0.0, 0.1, 0.2, 0.3, 0.4, 0.6]:
    ro = np.mean([run(old, kappa, np.random.default_rng(s)) for s in range(3)], axis=0)
    rn = np.mean([run(new, kappa, np.random.default_rng(s + 10)) for s in range(3)], axis=0)
    print(f"{kappa:4.1f} | {rn[0]-ro[0]:+.4f} | {rn.mean()-ro.mean():+.4f} | {rn[-1]-ro[-1]:+.4f}")
