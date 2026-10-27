# Measured Feedback Tipping Points

## Problem & Theme chosen
Theme 2 (Cause and Effect), Problem 3. A pre-rollout audit returning APPROVE, REJECT, or NEED RANDOMIZED DATA, plus the data size that would settle it.

## Understanding of the challenge
A policy can look good via static bias [the old policy used information the logs miss], dynamics [repeated showings tire users], or before/after comparison [mixes both with outside drift]. One-step off-policy evaluation (OPE) [value of a new policy from old logs] fixes only the first, and only with true logged propensities [probability the logger showed that item]. In our simulator a latent taste drives both the old policy's choices and clicks; at kappa = 0.4 [drop in click log-odds per earlier showing], one-step OPE reports +0.084, the true lift is -0.013.

## Proposed approach
- **Static layer [MVP].** IPW [inverse propensity weighting], SNIPS [self-normalised IPW], DR [doubly robust] [refs 6-8, 11-13], user-level bootstrap (OBD [Open Bandit Dataset; 4]: row-level). Taste breaks unconfoundedness [no unlogged driver of choice and click].
- **Dynamic layer [Core].** logit(click) = base(context, item) - kappa x g(c) + round term, c = the user's earlier showings of the item. Four shapes g: c; log(1+c); 0.7-discounted recency; tail guard c + max(c-2, 0) [extra penalty after the second showing]. A fifth, free-form model gives each prior-count bin (1 to 6, 7 or more) its own coefficient. Forecast over 10 rounds; kappa* = kappa where forecast lift is 0.
- **Slice [Core].** Round 1 uniform (propensity 1/10); later rounds repeat the last item with probability 0.5, else uniform (propensities known), so the new policy's repeat counts are observed. Kappa-hat is population-averaged, so kappa* is solved in the same model. Uniform serving lost 24% of OBD clicks: cap 8,000 users.
- **Verdict [Core].** Two-sided 95% joint user-bootstrap intervals. APPROVE needs a slice; static and forecast lower ends above 0 under all four shapes and the free-form model; and a coverage guard (at most 5% of the new policy's forecast showings beyond repeat counts the slice saw 100 times). REJECT: under all four shapes an upper end is at most 0. Otherwise NEED RANDOMIZED DATA with n* = max over shapes of ((1.96 + 0.84) s / |estimate|)^2 [80% power; s = bootstrap SD x sqrt(pilot users)] and a pilot band [n* if the estimate moves 1.96 SE]. A 3,000-user pilot only sizes n*; above 8,000 users we abstain. Logs alone cannot test hidden taste, so a logs-only audit may REJECT or ask for a slice, never APPROVE (taste inflates the one-step lift here, so REJECT is conservative: 0/32 false rejects).

## Minimum Viable
(1) One command runs IPW, SNIPS, DR on the simulator; the OBD loader is being added.
(2) Under adverse drift [every item's click logit lowered by 1.0], before/after has the wrong sign in 200/200 runs (96/200 at 0.5); SNIPS and DR intervals cover the true round-one lift in 187/200.
(3) OBD control: Random logs scoring BTS [Bernoulli Thompson sampling]: ESS/n [effective sample size over n] 0.247, DR error -8.8%, but the 95% interval misses the A/B rate; OBD intervals are reported as optimistic.

## Stretch ambitions
(1) KuaiRand [5]: kappa-hat, shuffled-round placebo. (2) Marginal-sensitivity bounds [9, 10].

## Novelty / differentiation
Beyond IPW or DR on OBD (static bias only) we add (a) feedback strength (kappa-hat [estimate of kappa]) with an interval beside its tipping point, and a tipping margin (kappa-hat - kappa*)/SE (Brier 0.082 vs 0.25 for a constant forecast); (b) a randomised slice sized by the verdict's statistics; (c) a count-curve veto and coverage guard that turn unmodelled fatigue into a data request. Experimental grounding [15] debiases a static effect, not feedback strength. Other ingredients have precedent [2, 3, 9, 10, 14-20]; closest paper [1] gives a launch-readiness class only.

## Evaluation plan
Baselines: before/after, one-step OPE, state-augmented fitted-Q [regression of long-run reward on action and history], logs-only kappa-hat. Ablations: no slice, shapes, veto or guard. Simulators: W2 (probit link [click probability from the normal CDF], per-user kappa); negative control (truth g = c^2); W3, W4 (late-onset fatigue) shaped the final rule, so are development sets; W5 (cubic, quadratic, exponential fatigue) is fresh.
Targets, preregistered: false approval [truly worse policy approved] at most 5% (one-sided 95% Clopper-Pearson bound [exact binomial upper limit], 59+ runs), 10% near the boundary [|true lift| at most 0.01]; false reject at most 10%; correct-approve at least 25% (always abstaining passes otherwise); n* band covers the oracle in 90% of pilots.
Prototype, simulator. Logs only, hidden taste: 17/80 truly worse approved, hence never-approve. Fresh W5: 0/144 false approvals (6/144 without the veto; the free-form model alone also 0/144), 26/48 correct-approve. Sharper new policy (8.8% of showings beyond the slice): guard fires 96/96, 0/72 false approvals. n* band covers the oracle in 85% of pilots (target 90%).

## Feasibility and Risks
Team (a third of core work each): Balakumar V [simulation, bootstrap inference]: simulator, dynamic layer, fitted-Q. Kishore Kumar J [pandas pipelines]: IPW/SNIPS/DR, OBD control, harness; stretch (1). K Asvitha [experiment design, plotting, demo UI]: slice, verdict, n*, ablations, demo; stretch (2).
Plan (about 6 s per audit per CPU core): 10-16 Nov MVP; 17-23 Nov OBD control, fitted-Q, demo; 24-30 Nov Core freeze; 2-6 Dec stretch; 7-8 Dec buffer. MVP plus Core is about 14 of 28 engineer-days.
Risks: (1) near the tipping point n* exceeds the cap: report the band, abstain. (2) Intervals cover sampling error only; unmodelled fatigue relies on shapes, veto, guard (1/72 false approvals on W4). (3) OBD adaptive logging breaks intervals; ESS/n warns, yet DR missed at 0.247. (4) Sparse KuaiRand repeats. (5) Dynamics validated only on simulators; opposite-signed taste untested. Cut order if late: stretch, demo UI, non-linear shapes.

Code and run log: https://github.com/balakumar-v/feedback-tipping-points (public before submission)

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
