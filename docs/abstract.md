# Measured Feedback Tipping Points

## Problem & Theme chosen
Theme 2 (Cause and Effect), Problem 3. A ranking policy is judged on outcomes it helped create, so metrics can mislead. We build a pre-rollout audit returning APPROVE, REJECT, or NEED RANDOMIZED DATA plus its data size.

## Understanding of the challenge
A policy can look good via static bias [the old policy used information the logs miss], dynamics [repeated showings tire users], or before/after comparison [mixes both]. One-step off-policy evaluation (OPE) [value of a new policy from old logs] fixes only the first, and only if the logged propensity is true. In our simulator a latent taste drives both the old policy's choices and clicks; at kappa = 0.4 [drop in click log-odds per earlier showing], one-step OPE reports a lift of +0.084 while the true 10-round lift is -0.013.

## Proposed approach
- **Static layer [MVP].** Needs unconfoundedness, positivity, SUTVA [no interference]; taste breaks the first. IPW [inverse propensity weighting], SNIPS [self-normalised IPW], DR [doubly robust] [refs 6-8, 11-13] with user-level bootstrap (OBD [Open Bandit Dataset; 4]: row-level).
- **Slice [Core].** Uniform random item on every impression (propensity 1/10), so chance repeats identify kappa. Kappa-hat is population-averaged (taste shrinks it); kappa* [kappa where forecast lift is 0] is solved in the same model. Uniform serving lost 24% of OBD clicks: slices capped at 8,000 users.
- **Dynamic layer [Core].** logit(click) = base(context, item) - kappa x g(history) + round-index term; c = earlier showings of the item to that user; g = c, log(1+c), 0.7-discounted recency, or tail guard c + max(c-2, 0). Forecast horizon H = 10 rounds, fixed in advance. The new policy repeats items far more than the slice (mean prior count 3.0 vs 0.25), so the forecast extrapolates: we act only when all four agree.
- **Verdict [Core].** Intervals are two-sided 95% joint user-bootstrap. APPROVE iff static and forecast lower ends exceed 0 under all four g; REJECT iff, under all four, either upper end is at most 0; else NEED RANDOMIZED DATA with n* = max over g of ((1.96 + 0.84) s / |estimate|)^2 [80% power; s = bootstrap SD x sqrt(pilot users)]. The 3,000-user pilot only sizes n*; verdicts use fresh users; n* above 8,000 abstains. Reports tipping margin (kappa-hat minus kappa*, in standard errors). At the cap only lifts near +0.04 are certifiable (+0.005 needs ~86,000).

## Minimum Viable
(1) One command runs IPW, SNIPS, DR on simulator and OBD. (2) Under adverse drift, before/after has the wrong sign in 82% of 200 runs; OPE's 95% interval covers the true round-one lift. (3) OBD Random and BTS logs score each other against the A/B rate; if ESS/n [effective sample size over n] is at least 0.10 the DR interval must cover it, else the audit warns.

## Stretch ambitions
(1) KuaiRand [5]: kappa-hat, shuffled-round placebo. (2) Marginal-sensitivity bounds [9, 10] for unobserved confounding. (3) Sequential slice with early stopping.

## Novelty / differentiation
IPW or DR on OBD fixes static bias only. We add (a) feedback strength with an interval beside its tipping point; (b) a randomised slice sized by the verdict's statistics; (c) a four-shape agreement rule. Ingredients have precedent [2, 3, 9, 10, 14-19]; high-confidence OPE [20] bounds value but ignores feedback; closest paper [1] gives only a launch-readiness class.

## Evaluation plan
Baselines: before/after, one-step OPE, state-augmented fitted-Q, logs-only kappa-hat. Ablations, with expected effects: no slice (logs-only kappa-hat reads 0.21, not 0.40); last-impression-only randomisation (kappa-hat low); one fatigue shape (up to 90% false rejects); no round term (drift read as fatigue); no power term (n* too small). Tests: a second generator unlike the fitted model (probit link, per-user kappa) and a negative control (truth g = c^2).

Targets, fixed in advance: false approval [truly worse policy approved] at most 5% (one-sided 95% Clopper-Pearson bound, 59+ held-out truly-worse runs), at most 10% near the boundary [|true lift| at most 0.01, 29+ runs]; false reject at most 10%; abstention on truly-better at most 50%; correct-approve at least 0.50 at true lift of +0.02 or more. The tipping margin fails if its Brier score is no better than a constant guess or its calibration gap exceeds 0.15.

Prototype: false approvals 0/240 (logs), 0/228 (slice), 0/192 (second generator). Missed: abstention on truly-better 0.52 (logs) and 0.60 (slice at the 8,000 cap); slice correct-approve 0.33 (4/12) and 0.62 (10/16) in two separate seed sets. Tail guard: out-of-family false approvals 12/80 to 1/80, correct-approve at +0.010 lift 16/16 to 4/16. Tipping-margin Brier 0.082 vs 0.25.

## Feasibility and Risks
Team (each: a third of core work, one stretch item, one review): Balakumar V [simulation, bootstrap inference]: simulator, dynamic layer, fitted-Q; stretch (3); reviews verdict code. Kishore Kumar J [pandas pipelines]: IPW/SNIPS/DR, OBD control, harness, evaluation tables; stretch (1); reviews simulator. K Asvitha [experiment design, plotting, demo UI]: slice, verdict and n*, ablations, demo; stretch (2); reviews estimators. Prior work: this prototype and its log; Balakumar built a RAG chatbot; Kishore a no-code assistive app (sign-language translation, OCR, object/obstacle detection, SOS); Asvitha an AI agent that reproduces bugs from vague reports in a cloud browser.

Plan: 10-16 Nov MVP freeze; 17-23 Nov OBD control (Kishore), fitted-Q (Balakumar), demo (Asvitha); 24-30 Nov Core freeze; 1 Dec midway; 2-6 Dec stretch; 7-8 Dec buffer; 9-18 Dec rehearsal, finals. Effort: MVP plus Core about 14 engineer-days, stretch 9, capacity 28; one audit takes about 6 s on a CPU core.

Risks: (1) near the tipping point n* exceeds the cap: report n*, abstain; (2) unmodelled fatigue shape: tail guard plus c^2 control; (3) OBD adaptive logging breaks intervals (ESS/n warns); (4) sparse KuaiRand repeats (fallback: author as item); (5) fatigue shapes validated on simulators only.

Code and run log: [add repository URL before submitting]

## References
1. Shekhar, Howard (2026). Decision Support for Marketplace Policies under Incomplete Evidence. arXiv:2605.12840.
2. Chandak et al. (2022). OPEN. NeurIPS.
3. Jagerman et al. (2019). When People Change their Mind. WSDM.
4. Saito et al. (2021). Open Bandit Dataset. NeurIPS D&B.
5. Gao et al. (2022). KuaiRand. CIKM.
6. Horvitz, Thompson (1952). JASA.
7. Swaminathan, Joachims (2015). NeurIPS.
8. Dudik et al. (2011). ICML.
9. Tan (2006). JASA.
10. Zhao et al. (2019). JRSS-B.
11. Thomas, Brunskill (2016). ICML.
12. Jiang, Li (2016). ICML.
13. Kallus, Uehara (2020). JMLR.
14. VanderWeele, Ding (2017). Ann. Intern. Med.
15. Kallus, Puli, Shalit (2018). Removing Hidden Confounding by Experimental Grounding. NeurIPS.
16. Namkoong et al. (2020). NeurIPS.
17. Kallus, Zhou (2018). NeurIPS.
18. Levine et al. (2017). Rotting Bandits. NeurIPS.
19. Pike-Burke, Grunewalder (2019). Recovering Bandits. NeurIPS.
20. Thomas, Theocharous, Ghavamzadeh (2015). High Confidence Off-Policy Evaluation. AAAI.
