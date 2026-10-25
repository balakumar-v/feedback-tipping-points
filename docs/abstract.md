# Measured Feedback Tipping Points

## Problem & Theme chosen
Theme 2 (Cause and Effect), Problem 3. We build a pre-rollout audit returning APPROVE, REJECT, or NEED RANDOMIZED DATA plus its data size.

## Understanding of the challenge
A policy can look good via static bias [the old policy used information the logs miss], dynamics [repeated showings tire users], or before/after comparison [mixes both]. One-step off-policy evaluation (OPE) [value of a new policy from old logs] fixes only the first, and only if the logged propensity [probability the logger showed that item] is true. In our simulator a latent taste drives both the old policy's choices and clicks; at kappa = 0.4 [drop in click log-odds per earlier showing], one-step OPE reports +0.084, the true 10-round lift is -0.013.

## Proposed approach
- **Static layer [MVP].** Needs unconfoundedness [no unlogged driver of both choice and click], positivity [every item has logging probability above 0], SUTVA [no interference]; taste breaks the first. IPW [inverse propensity weighting], SNIPS [self-normalised IPW], DR [doubly robust] [refs 6-8, 11-13] with user-level bootstrap (OBD [Open Bandit Dataset; 4]: row-level).
- **Slice [Core].** Repeat-heavy design: round 1 uniform (propensity 1/10), later rounds repeat the last item with probability 0.5, else uniform (propensities known), 10 rounds (= H), so repeat counts the new policy produces are observed. Kappa-hat is population-averaged (taste shrinks it), so kappa* [kappa where forecast lift is 0] is solved in the same model. Uniform serving lost 24% of OBD clicks: cap 8,000 users. Logs alone cannot test hidden taste, so a logs-only audit never APPROVEs; and APPROVE also needs a fifth model with a free fatigue coefficient per prior-count bin [1 to 6, 7 or more] to approve, so unguessed fatigue shapes cannot slip through.
- **Dynamic layer [Core].** logit(click) = base(context, item) - kappa x g(history) + round-index term; c = the user's earlier showings of the item; g = c, log(1+c), 0.7-discounted recency, or tail guard c + max(c-2, 0) [fatigue that speeds up after two showings]. Horizon H = 10 rounds. The new policy repeats far more than the slice, so we act only when all four g agree.
- **Verdict [Core].** Intervals are two-sided 95% joint user-bootstrap. APPROVE (slice required) iff static and forecast lower ends exceed 0 under all four g; REJECT iff, under all four, either upper end is at most 0; else NEED RANDOMIZED DATA with n* = max over g of ((1.96 + 0.84) s / |estimate|)^2 [80% power; s = bootstrap SD x sqrt(pilot users)], reported with a pilot band [estimate moved 1.96 SE either way]. A 3,000-user pilot only sizes n*; verdicts use fresh users; above 8,000 we abstain.

## Minimum Viable
(1) One command runs IPW, SNIPS, DR on simulator and OBD. (2) Under adverse drift [covariate shift lowering every item's click rate], before/after has the wrong sign in 82% of 200 runs, while OPE's interval covers the true round-one lift. (3) OBD Random vs BTS [Bernoulli Thompson sampling] logs as a control: when ESS/n [effective sample size over n] is at least 0.10, the DR interval must cover the A/B rate.

## Stretch ambitions
(1) KuaiRand [5]: kappa-hat, shuffled-round placebo. (2) Marginal-sensitivity bounds [9, 10] for unobserved confounding.

## Novelty / differentiation
Beyond IPW or DR on OBD (static bias only) we add (a) feedback strength with an interval beside its tipping point; (b) a randomised slice sized by the verdict's statistics; (c) a four-shape agreement rule. Experimental grounding [15] debiases a static effect; we identify feedback strength and size the next slice. Other ingredients have precedent [2, 3, 9, 10, 14-20]; closest paper [1] gives a launch-readiness class only.

## Evaluation plan
Baselines: before/after, one-step OPE, state-augmented fitted-Q [regression of long-run reward on action and history], logs-only kappa-hat. Ablations: no slice; one fatigue shape; no round term. Tests: a second generator unlike the fitted model (probit link [click probability from the normal CDF], per-user kappa); a negative control (truth g = c^2); three more generators built after freezing the rule (late-onset, step, exponential, polynomial fatigue). Always abstaining passes the false-approval targets, so correct-approve is a target too; failures are reported.

Targets, fixed in advance: false approval [truly worse policy approved] at most 5% (one-sided 95% Clopper-Pearson bound [exact binomial upper limit] over 59+ runs), 10% near the boundary [|true lift| at most 0.01, 29+ runs]; false reject at most 10%; correct-approve at least 0.50 at lift +0.02; the n* band covers the true-effect n* in 90% of pilots.

Prototype (simulator). Logs only with hidden taste, the rule approved 17/80 truly worse policies, hence never-approve. On a fresh generator, 0/144 false approvals with the free-form veto (6/144 without it), at 26/48 correct-approves; on the earlier delayed-onset generator it leaves 1/72. Misses: that 1/72, lower correct-approve (8/24 vs 13/24), n* band coverage 85% (target 90%).

## Feasibility and Risks
Team (a third of core work each): Balakumar V [simulation, bootstrap inference]: simulator, dynamic layer, fitted-Q (Kishore reviews each module). Kishore Kumar J [pandas pipelines]: IPW/SNIPS/DR, OBD control, harness; stretch (1). K Asvitha [experiment design, plotting, demo UI]: slice, verdict and n*, ablations, demo; stretch (2).

Plan: 10-16 Nov MVP freeze; 17-23 Nov OBD control, fitted-Q, demo; 24-30 Nov Core freeze; 1 Dec midway; 2-6 Dec stretch; 7-8 Dec buffer. MVP plus Core is about 14 of 28 engineer-days.

Risks: (1) near the tipping point n* exceeds the cap: report the band, abstain; (2) unmodelled fatigue: tail guard, c^2 control, free-form veto (limited to repeat counts the slice shows, up to 7); (3) OBD adaptive logging breaks intervals (ESS/n warns); (4) sparse KuaiRand repeats (fallback: author as item); (5) dynamics are validated only on our simulators; KuaiRand (stretch) is the only real dynamics data. If Core slips: MVP plus the linear-shape slice audit.

Code and run log: https://github.com/balakumar-v/feedback-tipping-points

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
