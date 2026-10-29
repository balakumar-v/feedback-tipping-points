# Measured Feedback Tipping Points: Did the Policy Work, or Did It Just Look Like It?

## 1. Problem and theme
Theme 2 (Cause and Effect in AI Decisions), Problem 3. A ranking policy is judged on outcomes it shaped itself, so a metric can rise because the policy is better, because of who saw it, or because users react to repeated exposure. We will build a pre-rollout audit with three verdicts: APPROVE, REJECT, or NEED RANDOMIZED DATA (with how much). [Team motivation.]

## 2. Understanding of the challenge
A policy can look good for three separate reasons: (1) static bias [the old policy used information the logs miss, or rarely tried what the new one favours]; (2) dynamics [deployment changes later exposure, e.g. repeat showings tire users]; (3) a before/after comparison [new-period minus old-period metric] that mixes both with drift. Off-policy evaluation (OPE) [estimating a new policy's value from the old policy's logs] addresses (1) only, one step ahead. In a pilot simulator, at fatigue strength kappa = 0.4 [kappa: drop in a user's click log-odds per earlier exposure of the same item], one-step OPE estimates +0.074 while the true 10-round lift is +0.010. The crux: kappa fitted on the same logs is biased by hidden taste [a user trait driving both what the old policy showed and what the user clicks], so the audit must judge its own evidence.

## 3. Proposed approach (Python, numpy, scikit-learn)
Pipeline: logs → static layer → dynamic layer → randomised slice → verdict.
- **Static layer.** IPW [inverse propensity weighting: weight logged outcomes by new-over-old action probability], SNIPS [self-normalised IPW] and DR [doubly robust: model prediction plus weighted residual], with user-level (or time-block) bootstrap intervals and ESS/n flags [effective sample size over n] marking thin overlap.
- **Dynamic layer.** Fit logit(click) = base(context, item) - kappa x (prior exposures of that item); bootstrap kappa-hat; simulate the new policy for T rounds; solve for the tipping point kappa* [the kappa where forecast lift reaches zero].
- **Identification.** A uniformly randomised exposure slice [users shown random items] refits the whole model, since the bulk reward model is confounded too.
- **Verdict.** APPROVE if the static-lift interval is above 0 and kappa-hat's upper bound is below kappa*; REJECT if the static upper bound is at most 0 or kappa-hat's lower bound exceeds kappa*; else NEED RANDOMIZED DATA, with slice size n* = (1.96 c / |kappa-hat - kappa*|)^2, c = SD(kappa-hat) x sqrt(users).
- **Data.** Simulator with exact counterfactuals; OBD [Open Bandit Dataset] "men" (Random and BTS [Bernoulli Thompson sampling] logs evaluate each other, scored against A/B click-through rate; static only); KuaiRand [randomly exposed videos with user IDs and timestamps] for fatigue.

## 4. Minimum viable
One command prints a table and a verdict covering both bullets: (1) IPW/SNIPS/DR on the simulator and OBD; (2) a concrete before/after contrast: simulator true lift +0.0185 while before/after under adverse drift averages -0.0039 and has the wrong sign in 85% of 200 runs. Simulator plus OBD is the guaranteed demo; dynamics are stretch.

## 5. Stretch
Uncertainty quantification: intervals for the lift, kappa-hat and kappa*, with coverage checks. Sensitivity analysis for unobserved confounding: first a bulk-versus-slice bias test, then optional worst-case bounds.

## 6. Novelty
Beyond the IPW/DR baseline we add: (a) a measured feedback strength with an interval, placed next to the tipping point where the policy stops working, instead of one lift number; (b) treating the audit's own evidence as suspect: hidden taste biases fatigue estimates, so a small randomised slice refits the model and is sized by a formula; (c) diagnostics reported as separate findings, not one trust score. Not a new estimator. Prior art we build on: IPW/DR, sensitivity bounds, non-stationary OPE (OPEN, NeurIPS 2022), launch/validate/reject outputs for marketplace policies (2026).

## 7. Evaluation plan
Baselines: naive before/after; one-step OPE alone; logs-only kappa-hat. Metrics: kappa-hat bias and coverage; interval coverage of the A/B click-through rate on OBD; false-approval rate [a truly worse policy approved; true lift below -0.002]; abstention rate on truly-better policies; ESS/n; n* adequacy. Stress tests: hidden-taste strength, wrong fatigue shape, drift, logger retraining. Pass/fail thresholds are written before each run and failures reported (so far 14 fixed in advance, 5 added later). Pilot sanity checks: with hidden taste, logs-only audits approved 40 of 80 truly-worse simulated runs, versus 0 of 80 with a 1,500-user slice.

## 8. Feasibility and risks
Team: [member 1: skills; simulator, audit], [member 2: skills; OBD, KuaiRand], [member 3: skills; evaluation, demo]. Plan: 10-16 Nov one-command audit, OBD pipeline with time-block intervals; 17-23 Nov MV demo script, inspect KuaiRand; 24-30 Nov KuaiRand kappa-hat, held-out forecast, slice-size curves; 1 Dec midway report; 2-8 Dec joint kappa* bootstrap, several fatigue shapes, sensitivity analysis; 9-14 Dec rehearsal, fallback demo; 15-18 Dec finals. Risks, from pilot runs: (1) n* is only a lower bound: re-auditing at n* decided 4 of 23 cases; fix: bootstrap kappa* jointly. (2) Wrong fatigue shape gave false rejects (saturating) and false approvals (accelerating); fix: fit several shapes, abstain when they disagree. (3) On full OBD, SNIPS and DR intervals missed the A/B rate by 7% to 12%; scoring BTS against its realised daily mix cut DR error to 2% (hindsight), so adaptive policies must be replayed and ESS/n (0.0004 for BTS scoring Random) must gate trust. (4) Our simulator shares the fitted model's family, so KuaiRand is the real test.
