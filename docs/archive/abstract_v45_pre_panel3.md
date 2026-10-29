# Measured Feedback Tipping Points: A Pre-Rollout Audit for Ranking Policies

*Perceptron Hackathon 2026, Problem 3. Balakumar V, Kishore Kumar J, K Asvitha. Code: github.com/balakumar-v/feedback-tipping-points. Data-flow diagram: `figures/p3_diagram.png` (Figure 1).*

## 1. Problem & Theme chosen

Theme 2 (Cause and Effect), Problem 3. An audit reads old logs and a candidate ranking policy, then returns **APPROVE**, **REJECT** or **NEED RANDOMIZED DATA** (abstain, with the extra data size needed).

## 2. Understanding of the challenge

The crux is identifiability: the old policy shaped the logs, so a new policy's value is recoverable only with overlap, known propensities (logged show-probabilities) and no hidden confounder. Two traps fake a gain:

- **Hidden taste** (unlogged preference driving display and click). IPW, SNIPS, DM and DR (standard one-step estimators) report +0.154 to +0.158 lift in our simulator; truth is +0.100.
- **Fatigue** (click odds fall with repeats). One-step estimates score round 0 only: for cubic fatigue they say +0.084, the true 10-round lift is −0.019.

Users are assumed independent. The static layer scores round 0 only, so no trajectory weights need clipping; weights stay unclipped (capping moved an Open Bandit Dataset [OBD] error from −7% to +7–12%) and a low ESS/n warns.

## 3. Proposed approach (Figure 1 shows the data flow)

1. **Static layer.** IPW, SNIPS, DM, cross-fitted DR on round-0 logs; user-level Poisson-bootstrap 95% intervals (B = 30).
2. **Randomised slice.** 3,000 users × 10 rounds with known propensities: round 0 uniform, later rounds repeat the previous item with probability 0.5, else uniform. This exposes fatigue that logs cannot identify. Uniform serving cost 24% of OBD clicks, so slices cap at 8,000 users.
3. **Fatigue models.** logit(click) = base(context, item) + f(c) + round term, c = the user's earlier showings of the item. Four shapes of f: c; log(1+c); 0.7-discounted recency; c + max(c−2, 0) (long repeat runs weigh more). A fifth, free-form model gives each count its own coefficient (1…6, ≥7). Both policies roll out 10 rounds; the forecast subtracts the old policy's logged-minus-modelled reward (anchor).
4. **Tipping point.** Bisection finds κ*, the linear fatigue strength where forecast lift is 0. The margin Φ((κ̂ − κ*)/SE) is reported, not a verdict input.
5. **Verdict** (two-sided 95% intervals). **APPROVE:** static and 10-round lower ends > 0 under all four shapes, a *coverage guard* (at most 5% of forecast showings beyond the repeat counts the slice actually observed, so we never extrapolate) and a *free-form veto* (its lower ends > 0 too). **REJECT:** a static or 10-round upper end ≤ 0 under all four shapes. **NEED RANDOMIZED DATA:** otherwise. Logs-only audits never approve, since hidden taste is untestable from logs.

## 4. Minimum Viable

`python -m p3ope ope` runs IPW, SNIPS, DM, DR against exact simulator truth. After a uniform 1.0 click-logit drop post-launch, before/after has the wrong sign in 200/200 runs (−0.060 vs true +0.075); SNIPS and DR 95% intervals cover truth in 187/200. OBD control: DR is 8.8% below the A/B click rate and its interval misses.

## 5. Stretch ambitions

Dropped last-first: (1) KuaiRand [3]: κ̂ on real repeats and a shuffled-round placebo, our only real-data check of the dynamics. (2) Marginal-sensitivity bounds [8, 9] (implemented, unit-tested) in the verdict.

## 6. Novelty / differentiation

Claim to test: a verdict built on measured fatigue approves fewer worse policies than one-step OPE, before/after or the best single model. Beyond IPW/DR on OBD [1, 2]: (a) a fatigue tipping point κ*, like E-value tipping analysis [7] but for dynamics; (b) targeted randomization for repeat-heavy histories; (c) abstention by guard and veto, added after fresh-generator failures. Prior work [4, 5, 6, 10–12] handles non-stationarity, static debiasing or fatigue planning, but gives no launch verdict or slice.

## 7. Evaluation plan

**Truth:** exact 60,000-user Monte Carlo lift in our simulators; OBD A/B rates as a real static check. **Metrics:** false approval with a one-sided 95% Clopper–Pearson bound (also near the boundary, |true lift| ≤ 0.01); false reject; correct approve; abstention; decision value (mean true lift of approved policies, each harm counted λ = 1, 5, 10 times). **Baselines:** before/after; one-step OPE; best single shape.

**Preregistered criterion** (Addendum 19; sealed generator added after the rule froze): false approval ≤ 5% (≤ 2/144), near-boundary ≤ 10%, false reject ≤ 10%, correct approve ≥ 25%, else we report failure. Result: 0/144, 0/48, 0/48, 26/48; one-step gate 144/144 false approvals.

**Ablation (post hoc).** Linear-only also scored 0/144 on the sealed generator, so it cannot show the guard or veto helps. On the two generators seen while building the rule, four-shape agreement gave 13/216 false approvals, the tail-weighted shape alone 13/216, the free-form model alone 1/216, the final rule 1/216. Safety comes mainly from the free-form model; four-shape agreement is a cross-check. Decision value (λ = 1, sealed): final rule +0.0037 per audit, oracle +0.0068, one-step gate −0.0023.

## 8. Feasibility and Risks

**Team.** Balakumar V (simulation, bootstrap inference): estimators. Kishore Kumar J (pandas pipelines): engineering, loaders. K Asvitha (experiment design, plotting, demo UI): evaluation, demo. *[Add one prior project each.]* Prototype and tests exist; about 14 of 28 engineer-days remain.

**Compute.** One audit: about 6–8 s, about 200 MB, one CPU core, no GPU. A 192-audit grid is about 20 min; seeds are independent, so runs split across cores.

**Plan.** 10–16 Nov: KuaiRand mapping (riskiest), go/no-go 16 Nov; fallback OBD plus synthetic families still meets the MVP. 17–23 Nov: OBD loader. 24–30 Nov: sensitivity bounds, midway report 1 Dec. 2–6 Dec: ablations. 7–10 Dec: buffer. 11–14 Dec: rehearsal. **Drop order if week 3 slips:** demo UI, sensitivity bounds, KuaiRand placebo.

**Risks.** (1) Near the tipping point it abstains: 16/16 at +0.005 lift even at 8,000 users. (2) Late-onset fatigue: earlier rules falsely approved 37/144 and 18/144 before the veto. (3) Hidden taste biases slice κ̂ low (−0.05). (4) The n* pilot band covers the oracle in 85% of pilots (target 90%). (5) Truth is simulated. (6) KuaiRand may have few repeats.

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
