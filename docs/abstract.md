# Measured Feedback Tipping Points: A Pre-Rollout Audit for Ranking Policies

*Perceptron Hackathon 2026, Problem 3. Balakumar V, Kishore Kumar J, K Asvitha. Code: github.com/balakumar-v/feedback-tipping-points*

## 1. Problem & Theme chosen

Theme 2 (Cause and Effect), Problem 3. An audit that judges a new ranking policy from old logs and returns **APPROVE**, **REJECT** or **NEED RANDOMIZED DATA** [abstain, with the extra data size needed].

## 2. Understanding of the challenge

The crux is identifiability: the old policy shaped the logs, so a new policy's value is recoverable only with overlap [the logger showed what the new policy shows], known propensities [logged show-probabilities] and no hidden confounder. Two traps fake a gain:

- **Hidden taste** [unlogged preference driving display and click]: IPW, SNIPS, DM and DR [inverse-propensity, self-normalised, direct-method, doubly robust estimators] report +0.154 to +0.158 lift in our simulator; truth is +0.100.
- **Fatigue** [click odds fall with repeats]: one-step estimates score round 0 only. For cubic fatigue they say +0.084; true 10-round lift is −0.019.

Users are assumed independent. Weights are unclipped (capping moved an Open Bandit Dataset [OBD] error from −7% to +7–12%); low ESS/n [effective sample size] warns.

## 3. Proposed approach

1. **Static layer.** IPW, SNIPS, DM, cross-fitted DR on round-0 logs; user-level Poisson-bootstrap 95% intervals (B = 30).
2. **Targeted slice.** 3,000 users × 10 rounds: round 0 uniform, later rounds repeat the previous item with probability 0.5, else uniform; propensities known. Repeat-heavy histories expose fatigue logs cannot identify. Uniform serving cost 24% of OBD clicks, so slices cap at 8,000 users.
3. **Fatigue models.** logit(click) = base(context, item) + f(c) + round term, c = the user's earlier showings of the item. f: c; log(1+c); 0.7-discounted recency; tail-weighted c + max(c−2, 0). A fifth, free-form model fits one coefficient per count (1…6, ≥7). Both policies roll out 10 rounds; the forecast subtracts the old policy's logged-minus-modelled mean reward (anchor).
4. **Tipping point.** Bisection finds κ*, the linear fatigue strength where forecast lift is 0. The margin Φ((κ̂ − κ*)/SE), SE = bootstrap SD of κ̂, is reported, not a verdict input.
5. **Verdict** (two-sided 95% intervals). **APPROVE:** static and 10-round lower ends > 0 under all four shapes, a coverage guard (≤ 5% of forecast showings above the largest repeat count the slice shows 100 times) and a free-form veto (its lower ends > 0 too). **REJECT:** under all four shapes, a static or 10-round upper end ≤ 0. **NEED RANDOMIZED DATA:** otherwise. Logs-only audits never approve: hidden taste is untestable from logs.

## 4. Minimum Viable

Official MVP (IPW/DR and a case that differs from before/after): `python -m p3ope ope` runs IPW, SNIPS, DM, DR against exact simulator truth. After a uniform 1.0 click-logit drop post-launch, before/after has the wrong sign in 200/200 runs (−0.060 vs true +0.075); SNIPS and DR 95% intervals cover truth in 187/200. OBD control: DR is 8.8% below the A/B click rate and its interval misses.

## 5. Stretch ambitions

Dropped last-first: (1) KuaiRand [3] (randomly exposed videos): κ̂ on real repeats, shuffled-round placebo. (2) Marginal-sensitivity bounds [8, 9] (implemented, unit-tested) added to the verdict: how much hidden confounding an APPROVE survives.

## 6. Novelty / differentiation

Claim to test: a verdict built on measured fatigue approves fewer worse policies than one-step OPE, before/after or the best single model. Beyond IPW/DR on OBD [1, 2]: (a) a fatigue tipping point κ*, like E-value tipping analysis [7] but for dynamics; (b) targeted randomization for repeat-heavy histories; (c) abstention via guard and veto, added after fresh-generator failures. Prior work: [4, 5] handle non-stationarity without a launch verdict or slice; [6] assumes stationary reward; [10] debiases a static effect; [11, 12] model fatigue for planning; [13] covers reserve prices.

## 7. Evaluation plan

**Truth:** exact 60,000-user Monte Carlo lift in our simulators; OBD A/B rates as a real static check. **Metrics:** false approval [worse policy approved] with a one-sided 95% Clopper–Pearson upper bound, also near the boundary (|true lift| ≤ 0.01); false reject; correct approve; abstention. **Baselines:** before/after; one-step OPE; best single-shape gate. **Ablations:** shapes, guard, veto, margin vs CI-only score. A sharper policy must trigger the guard.

**Preregistered criterion** (Addendum 19; sealed generator with sigmoid, recovering-hump and log-square fatigue, added after the rule froze): false-approval upper bound ≤ 5% (≤ 2/144), near-boundary ≤ 10%, false reject ≤ 10%, correct approve ≥ 25%, else we report failure. Result: 0/144, 0/48, 0/48, 26/48. But linear-only also scored 0/144, so this family does not show the guard or veto helps (earlier family: linear-only 19/144, final rule 0/144). One-step gate: 144/144 false approvals. The margin tied a CI-only score (AUC 1.00 each): a unit, not extra accuracy.

## 8. Feasibility and Risks

**Team.** Balakumar V [simulation, bootstrap inference]: estimators. Kishore Kumar J [pandas pipelines]: engineering, loaders. K Asvitha [experiment design, plotting, demo UI]: evaluation, demo. [Add one prior project each.] Prototype, tests and run log exist; about 14 of 28 engineer-days remain.

**Plan.** 10–16 Nov: KuaiRand exposure mapping first (riskiest), go/no-go 16 Nov; fallback OBD plus synthetic families still meets the MVP. 17–23 Nov: OBD loader. 24–30 Nov: sensitivity bounds, midway report (1 Dec). 2–6 Dec: ablations. 7–10 Dec: buffer. 11–14 Dec: rehearsal. Cut order: sensitivity, demo UI.

**Risks.** (1) Near the tipping point it abstains: 16/16 at +0.005 lift even with 8,000 users. (2) Late-onset fatigue: earlier rules falsely approved 37/144 and 18/144 before the veto. (3) Hidden taste biases slice κ̂ low (−0.05; a random intercept removed only 16%), so verdicts rest on shape agreement and the veto. (4) B = 30 is coarse. (5) Truth is simulated. (6) KuaiRand may have few repeats.

## References

1. Dudík, Langford, Li. Doubly Robust Policy Evaluation and Learning. ICML 2011.
2. Saito et al. Open Bandit Dataset and Pipeline. NeurIPS D&B 2021.
3. Gao et al. KuaiRand. CIKM 2022.
4. Chandak et al. Off-Policy Evaluation for Action-Dependent Non-Stationary Environments. NeurIPS 2022.
5. Jagerman, Markov, de Rijke. When People Change their Mind. WSDM 2019.
6. Thomas, Theocharous, Ghavamzadeh. High Confidence Off-Policy Evaluation. AAAI 2015.
7. VanderWeele, Ding. Sensitivity Analysis in Observational Research: the E-value. Ann. Intern. Med. 2017.
8. Tan. A Distributional Approach for Causal Inference Using Propensity Scores. JASA 2006.
9. Kallus, Zhou. Confounding-Robust Policy Improvement. NeurIPS 2018.
10. Kallus, Puli, Shalit. Removing Hidden Confounding by Experimental Grounding. NeurIPS 2018.
11. Levine, Crammer, Mannor. Rotting Bandits. NeurIPS 2017.
12. Li et al. Modeling User Fatigue for Sequential Recommendation. SIGIR 2024. arXiv:2405.11764.
13. Shekhar, Howard. Decision Support for Marketplace Policies under Incomplete Evidence. arXiv:2605.12840, 2026.
