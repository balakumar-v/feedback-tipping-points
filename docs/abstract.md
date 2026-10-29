# Measured Feedback Tipping Points: A Pre-Rollout Audit for Ranking Policies

*Perceptron Hackathon 2026, Problem 3. Balakumar V, Kishore Kumar J, K Asvitha. Code: github.com/balakumar-v/feedback-tipping-points*

## 1. Problem & Theme chosen

Theme 2 (Cause and Effect), Problem 3. An audit that judges a new ranking policy from old logs and returns **APPROVE**, **REJECT** or **NEED RANDOMIZED DATA** [abstain, with data size n*]. The candidate is sharper than the old policy (softmax, temperature 0.5).

## 2. Understanding of the challenge

The crux is identifiability: a new policy's value is recoverable from old logs only with overlap [the logger showed what the new policy shows], known propensities [logged show-probabilities] and no hidden confounder. Two traps fake a gain:

- **Hidden taste** [unlogged preference driving display and click]: IPW, SNIPS, DM and DR [inverse-propensity, self-normalised, direct-method, doubly robust estimators] report +0.154 to +0.158 lift in our simulator; truth is +0.100.
- **Fatigue** [click odds fall with repeats]: one-step estimates score round 0 only. For cubic fatigue they say +0.084; true 10-round lift is −0.019.

Users are independent; weights unclipped (capping worsened an Open Bandit Dataset [OBD] error).

## 3. Proposed approach

Intervals: two-sided 95% percentile of a user-level Poisson bootstrap, B = 30.

1. **Static layer.** IPW, SNIPS, DM, cross-fitted DR on round-0 logs.
2. **Targeted slice.** 3,000 users × 10 rounds, known propensities: round 0 uniform, later rounds repeat the previous item with probability 0.5, else uniform. Uniform serving costs 24% of OBD clicks, so slices cap at 8,000 users.
3. **Fatigue models.** logit(click) = base(context, item) + f(c) + round term, c = the user's earlier showings of the item. f: c; log(1+c); 0.7-discounted recency; c + max(c−2, 0). A fifth, free-form model fits one coefficient per count (1…6, ≥7). Both policies roll out 10 rounds, anchored to the old policy's logged reward.
4. **Tipping point.** Bisection finds κ*, the linear fatigue strength where forecast lift is 0; the margin Φ((κ̂ − κ*)/SE), SE = bootstrap SD of κ̂, is reported only.
5. **Verdict.** **APPROVE:** static and 10-round lower ends > 0 under all four shapes, a coverage guard (≤ 5% of forecast showings beyond repeat counts the slice shows 100 times) and a free-form veto (its lower ends > 0 too). **REJECT:** under all four shapes, a static or 10-round upper end ≤ 0. **NEED RANDOMIZED DATA:** otherwise, with n* = (2.8·SD/|lift|)², the slice size for 80% power to exclude zero lift. Logs-only audits never approve: hidden taste is untestable.

## 4. Minimum Viable

`python -m p3ope ope` scores all four against exact simulator truth. After a uniform 1.0 click-logit drop post-launch, before/after has the wrong sign in 200/200 runs; SNIPS and DR intervals cover truth in 187/200. OBD control: DR is 8.8% below the A/B click rate and its interval misses. Post hoc, against Bernoulli Thompson Sampling's realised mix the error is −6.7%, interval covering.

## 5. Stretch ambitions

Dropped last-first: (1) KuaiRand [3]: κ̂ on real repeats with a shuffled-round placebo. (2) Sensitivity bounds [8, 9] (written, not wired in).

## 6. Novelty / differentiation

Claim to test: a measured-fatigue verdict approves fewer worse policies than one-step OPE, before/after or the best single shape. Beyond IPW/DR [1, 2] and experimental grounding [10]: (a) a fatigue tipping point κ*, like E-value tipping [7] but for dynamics; (b) randomization targeted at repeat-heavy histories; (c) abstention via guard, veto and shape disagreement. Prior [4, 5, 11, 12] covers non-stationarity or fatigue, not launch verdicts.

## 7. Evaluation plan

**Truth:** 60,000-user simulator Monte Carlo; OBD A/B rates. **Metrics:** false approval [worse policy approved] with a one-sided 95% Clopper–Pearson bound, also near the boundary (|true lift| ≤ 0.01); false reject; correct approve. **Baselines:** before/after; one-step OPE [round-0 estimators as an approve gate]; best single shape.

**Preregistered criterion** (rule frozen, generators written after; counted per audit): false-approval bound ≤ 5%, near-boundary ≤ 10%, false reject ≤ 10%, correct approve ≥ 25%, else we report failure. Results follow this order.

- *Test 1, smooth shapes:* 0/144, 0/48, 0/48, 26/48; one-step gate 144/144 false approvals. Linear-only also scored 0/144, so no evidence here that guard or veto help.
- *Test 2, structurally different generator* (multiplicative, cross-category, recovering, taste-scaled fatigue). 40 worlds × 3 datasets: 0/36, 0/30, 0/75, 31/75; one-step gate 36/36. By world 0/21 truly-worse worlds had a false approval (bound 13%, above the 5% target).
- *Ablation (post hoc).* Test 2: single shapes falsely approve 0–6/36, four-shape agreement 0/36. Delayed-onset shapes: agreement alone 13/216, final rule 1/216.
- *Bootstrap size.* B = 200 on 48 Test 1 datasets: intervals 11% wider, 3 verdicts changed, 0 false approvals.

## 8. Feasibility and Risks

**Team.** Balakumar V [simulation, bootstrap inference]: estimators; built a hybrid-search RAG chatbot. Kishore Kumar J [pandas pipelines]: engineering, loaders; built an assistive app where false alerts are costly. K Asvitha [experiment design, plotting]: evaluation, demo UI; built a bug-reproduction agent. About 14 of 28 engineer-days remain.

**Plan.** *Exists:* rule, simulators, tests, OBD results (scripts lost). 10–16 Nov: KuaiRand mapping (riskiest; go/no-go 16 Nov; fallback OBD plus synthetic meets the MVP). 17–23 Nov: OBD loader. 24–30 Nov: sensitivity bounds; midway report 1 Dec. 2–6 Dec: ablations. 7–14 Dec: buffer, rehearsal. **Drop order:** demo UI (fallback: the self-contained dashboard with pre-computed audits), sensitivity bounds, KuaiRand placebo.

**Risks.** (1) Near the tipping point it abstains (16/16 at +0.005). (2) Hidden taste biases κ̂ low (−0.06, −0.16, −0.30 when taste strength is ×1, ×2, ×3), understating fatigue and so leaning toward false approval. Exposure is randomised: attenuation, not confounding. Safety rests on shape agreement, guard and veto (0/36 on Test 2); until sensitivity bounds are wired in, an APPROVE assumes taste is no stronger than tested. (3) Truth is simulated; KuaiRand may lack repeats.

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
