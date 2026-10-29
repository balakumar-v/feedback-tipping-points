# Perceptron P3 round-1 runs (2026-10-18). Pass/fail. P1-P14 pre-registered before E3/E4/new-E2 were run; P15-P16 (addendum 1) written after the first analysis; P17-P19 (addendum 2) written after the full OBD files arrived, before the full run.
| # | Claim | Result |
|---|---|---|
| P1 | kappa-hat error <=0.05 per cell; coverage >=0.88 | PASS: max cell error 0.028; coverage 0.90 (108/120); cell k=0.4 only 0.75 |
| P2 | 3-way false approval <=0.05; one-step >=0.90; NEED<=0.5 far from tipping | PASS: 0/40 vs 40/40; NEED 0/80 when |k-k*|>=0.2 (50% at k=0.6) |
| P3 | kappa* within 0.10 of true in >=80% | PASS: 96% (115/120) |
| P4 | hidden taste, logs-only: kappa-hat >=0.10 low; false approval >=0.20 (expected failure) | PASS: bias -0.160..-0.223; 40/80 (20/20 at k=0.4 and 0.6, 0/20 at 0.8, 1.0) |
| P5 | slice (1500 users) |bias|<=0.08, false approval <=0.10 | PASS: max bias 0.066, 0/80 (72 REJECT, 8 NEED); but 80% of truly-better runs abstain. At strongest taste (E4 sweep m=2) slice bias -0.10 and coverage 22-57%: would fail |
| P6 | misspecified fatigue (sat/decay/window): false approval>=0.10 or sign error>=0.20 | PASS via sign-error branch: saturating k=0.9 sign wrong 20/20 (false rejects 80%). Zero false approvals in 180 truly-worse runs (extended grid F). Exploratory 'convex' (accelerating) form: false approval 30% at k=0.4 (true lift -0.0039) |
| P7 | drift / logger-retraining mechanisms: false approval >=0.10 in some cell | FAIL (good news): 0 false approvals (retrain 0/20 truly-worse; toward-drift cells all truly better; exploratory reverse-drift 0/40). kappa-hat is misattributed under drift (-0.16..-0.43) but verdicts still right |
| P8 | silent failure: bulk 95% coverage <=0.10; best diagnostic AUC <=0.70 | PASS (reproduced): coverage 0.00-0.01 at bias 0.025 and 0.076; best AUC 0.66 (k-hat, hidden-confounding family; 1600 tasks) |
| P9 | static slice test power <=0.20 at m=1; >=0.80 at m=2 only with 3000 rows | PASS (reproduced): 0.12-0.16; 0.21/0.53/0.92 at 300/1000/3000 |
| P10 | slice-kappa SD<=0.05 at <=2000 users; kappa-test power>=0.80 at m=2 with <=2000; false alarm<=0.10 | PARTIAL FAIL: SD*sqrt(n)=2.79 so SD 0.05 needs ~3100 users (SD 0.063-0.069 at 2000); power 0.95 at 1000 (m=2) ok; false alarm 0-0.025 ok |
| P11 | whole-slice model beats hybrid (bulk model + slice kappa) in >=70% of seeds at k=0.4 | FAIL: 14/20 in E3 cell (n=1500) but 0.45-0.60 across E4 sweep at same strength; passes at m=2 (0.73-1.0). Beats bulk-only 100%. Sign-error: slice 0-2.5% (>=2000 users) vs hybrid 30-48% vs bulk 100% |
| P12 | closed loop: slice sized by n* resolves >=70% of NEED cases, no false approval | FAIL: 44/80 audits NEED; after n* (cap 8000) 29.5% decisive; 4/23 (17%) among uncapped; median n* 7,242; 48% over cap. No false approvals. Static-lift IPW variance on the slice dominates |
| P13 | ESS/n monotone in logger sharpness; coverage>=0.85 while ESS/n>=0.1 | PARTIAL FAIL: ESS/n not monotone (peaks 0.60 at tau_old 1.0 / 0.96 in exp2 when logger~candidate); coverage DR 0.91-0.94, SNIPS 0.78-0.93 for ESS/n>=0.05 (0.81-0.83 below 0.05) |
| P14 | CI-rule false approval <=0.05 while ESS/n>=0.1; naive before/after false approval >0.5 | PARTIAL FAIL: CI rules 0/691 truly-worse; naive under favourable drift 27% pooled (20-44% by overlap level). Caveat: truly-worse candidates were mostly far worse, so this is a weak test |
## Deviations
- PyPI blocked by sandbox network policy: no py3.10 + obp==0.5.7. Estimator cross-check used OBP source v0.5.5 from GitHub (torch/tqdm stubbed, one pandas-3 patch); IPW/SNIPS/DM/DR match to 6 dp.
- No "no-ai-slop" skill exists on this account (ListSkills/SearchSkills): used an explicit checklist instead.
- Grid extension after seeing results: groups F (sat/decay/window at kappa 1.5/2.5/4.0; the preregistered grid never crossed zero) and G (reverse drift) were added; 'convex' form was exploratory. All labelled as such.
- Forecast baseline calibration (old-policy observed rewards offset) is a design choice added in E3; exp12's original numbers were reproduced separately.
- E3 per-cell truth: 60k-user Monte Carlo; "truly worse" = true 10-round lift < -0.002.
- E5: the bundled 10k OBD sample was plumbing only; the full 'men' files (random 452,949 rows, bts 4,077,727) were uploaded later and run via e5_full.py (out/e5_full.json). Row-level Poisson bootstrap because OBD has no user IDs. KuaiRand not started.
## Addendum runs (pre-registered after first analysis; see PREREGISTRATION.md addendum)
| P15 | DR static lift on slice fixes closed loop (>=70% decisive uncapped; 0 false approvals; pilot NEED on truly-better <=0.50) | FAIL: 8/26 (31%) decisive uncapped; pilot NEED on truly-better 0.875; 0 false approvals but 3 false rejects (kappa 0.2). n* ignores uncertainty in kappa* |
| P16 | second world (ALPHA .5, TN .25) replicates A and B | PASS: A: FA 0/60 vs one-step 60/60, kappa-hat err<=0.035, coverage 0.925, kappa* within .1 120/120; B: logs-only FA 30/80, slice 0/80, slice abstains 57.5% of truly-better |
| P17 | OBD full 'men': SNIPS and DR 95% CI contain A/B CTR in >=3 of 4 pairs | FAIL: 0 of 4 (Random->BTS truth .00674: SNIPS .00613, DR .00615; BTS->Random truth .00512: SNIPS .00477, DR .00451; IPW .00525 inside) |
| P18 | DR rel err <=10% Random->BTS; naive >20% off both ways | PASS: DR -8.8%; naive -24.0% and +31.6% (trivial contrast) |
| P19 | DR CI narrower than SNIPS CI both ways; ESS/n>=0.10 Random->BTS | FAIL in part: ESS/n .247 ok; DR narrower Random->BTS (.00098 vs .00101) but wider BTS->Random (.00095 vs .00065) |
Tally: 19 thresholds, 10 held (P1-P6, P8, P9, P16, P18), 9 failed in whole or part (P7, P10-P15, P17, P19). P17-P19 deviation: row-level Poisson bootstrap (OBD has no user IDs); BTS evaluated as OBP's fixed zozotown-prior distribution; reward model fit on <=1M rows.

## Post-hoc diagnostic of the P17 misses (NOT pre-registered; e5_diag.py, out/e5_diag.json)
- A/B truth with exact 95% CI: BTS 0.006743 [0.006664, 0.006823]; Random 0.005124 [0.004918, 0.005336].
- Random logs scoring BTS, DR error vs truth: OBP static BTS distribution -8.8% (CI misses); BTS realised weekly action mix -6.7% (CI covers); BTS realised daily mix -1.8% (CI covers). SNIPS: -9.1%, -6.9%, -2.0% (covers only for daily). The daily mix uses hindsight from the BTS A/B logs, so it explains the gap but is not a deployable fix.
- BTS logs scoring Random: ESS/n 0.0004, max weight 29,412 (min logged pscore 1e-6). SNIPS with weights capped at 100/50/20/10/5 gives +7.0/+8.7/+10.2/+11.4/+12.0% error vs -7.0% uncapped: no cap fixes it; the estimate is dominated by the tail, so the right output is an ESS/n warning, not a tight interval.

## ROUND 2 (2026-10-20). P20-P26 pre-registered in addendum 3, P27-P33 in addenda 3-4, all before the corresponding runs.
| # | Claim | Result |
|---|---|---|
| P20 | pooled slice kappa bias <= -0.05 at taste x2 (kappa .8, n 3000), growing with taste | PASS: -0.049 / -0.182 / -0.321 at x1/x2/x3 |
| P21 | within-(user,item) first-repeat contrast |bias| <= 0.03 at n=3000 | PASS: max 0.011 |
| P22 | same contrast SD <= 0.10 at n=3000 | FAIL by 0.001: max SD 0.101 (0.085-0.101) |
| P23 | random-intercept pooled fit removes >= 50% of the bias at x2 | FAIL: 16% (-0.182 -> -0.153) |
| P24 | last-impression-only slice kappa bias <= -0.10 and >= 2x every-impression | PASS: -0.27..-0.33 vs -0.02..-0.06 |
| P25 | no round term: kappa bias >= 0.05 under generic decay .2/round; with it <= 0.05 | PASS: +0.233/+0.249; with term max 0.006 |
| P26 | round term held flat: forecast sign right >= 90%, median error <= 0.01 (H=10) | PASS: 0.947, 0.0025 (no round term: sign right 0.60) |
| P27 | three-shape rule: false approval <= 0.05 pooled incl. accelerating fatigue | PASS: 0/240 (CP95 upper 0.012); linear-only also 0/240 here |
| P28 | three-shape NEED rate on truly-better <= 0.50 | PASS: 0.183; correct-approve 0.817 |
| P29 | saturating kappa .9: three-shape false-reject <= 0.20 | PASS: 0.00 (linear-only 0.90; three-shape abstains 100%); false rejects over all truly-better: 0/180 vs 18/180 |
| P30 | held-out slice audit, hidden taste x1-3: 0 false approvals over truly-worse | PASS: 0/228 (CP95 upper 0.013); informative taste-x1 cells 0/60 (0.049); taste x2,x3 cells are all truly worse even at kappa 0 |
| P31 | slice audit correct-approve >= 0.50 on truly-better with lift >= +0.02 | FAIL: 0.33 (4/12); all truly-better 0.17; 83% abstain at 3000 slice users |
| P32 | three-shape false approval <= linear-only | PASS, tie 0 vs 0 |
| P33 | zero false approvals at taste x3 | PASS: 0/84 (trivial: new policy worse at every kappa) |
R2 tally: 14 thresholds, 11 held, 3 failed. Cumulative with round 1: 33 thresholds, 21 held, 12 failed in whole or part.
Descriptive (not thresholds): slice mean prior count 0.25 (2.9% of impressions >= 2), max 4; new policy rounds 7-10 mean prior count 3.02, 28.9% above the slice max, 39.2% above the logged p99 (3). True lift sign flips between H=6 and H=10 in 8 of 22 R2-3 cells (e.g. lin kappa .6: +0.0173 vs -0.0017).
Deviations R2: B=40 bootstrap (R2-3, R2-5) after the container restarted mid-run and cost time; NF=3000 forecast users; 12 held-out seeds per R2-5 cell (not 20); R2-3 fits no round term (its world has none); R2-5 includes it. R2-3 uses a forecast-lift CI rule, not the round-1 kappa-hat-vs-kappa* rule.
# ROUND 3 (2026-10-20): RUNS ON A STAND-IN WORLD. exp13_lib.py was missing from the zip.
All R3 numbers below come from standin/exp13_lib.py (constants fitted to 11 logged true-lifts, RMSE ~0.004; also reproduces logs-only kappa-hat .399, slice pooled bias -.054/-.207/-.332 at taste x1/2/3 (logged -.049/-.182/-.321), FE bias ~0). Differences seen: last-only bias -0.20 (logged -.27..-.33), one-step SNIPS under taste +.076 (logged +.084), FE SD .076 (logged .085-.101), true lift at lin kappa .6 is +.003 (logged -.0017). Re-run on the real exp13_lib before quoting any R3 number. P34-P38 pre-registered in Addendum 5 before running.
| # | Claim | Result (stand-in) |
|---|---|---|
| P34 | V2 (power, verdict-based n*) decisive >= 0.70 among NEED pilots with n* <= cap, and > V0 by >= 0.20 | PASS ON PAPER, UNINFORMATIVE: 2/2 decisive vs V0 7/30 (0.23); only 2 of 48 NEED pilots had V2 n* <= 8,000 |
| P35 | zero false approvals after re-audit; false rejects <= 0.10 among truly-better | PASS: 0 false approvals (pilot 0/56 truly-worse; V0 0/25, V1 0/3, V2 0/0 uncapped); 0 false rejects |
| P36 | V2 median n* <= cap in >= 50% of NEED pilots | FAIL: 4% (2/48). Median n*: V0 3,379; V1 38,809; V2 79,201 users. Only kappa=0 (far from tipping point) is affordable: V1 median 6,156 |
| P37 | three-shape (lin/log/mem7) false approval <= 0.05 pooled over out-of-family truly-worse (convex+quad) | FAIL: 19/64 = 0.30 (CP95 upper 0.405): convex .6 7/16, quad .4 12/16. Real-world R2-3 had 0/240 for convex, so this is a stand-in finding until re-run |
| P38 | adding tail guard tail2: false approval <= three-shape; correct-approve on lin .4 >= 0.50 | PASS: tail guard 0/64 (CP95 upper 0.046); correct-approve 16/16 on lin .4, 16/16 convex .2, 16/16 quad .05; linear-only also 19/64 |
Pilot (3000-user slice, taste x1, 14 seeds/kappa): APPROVE 12, NEED 48, REJECT 24 of 84; 0 false approvals. Deviations: kink truth dropped (true lift stays > 0 for every kappa); B=30; 14 seeds (200-213) in R3-1, 16 (300-315) in R3-3; the first background launch died and was resumed (resume logic skips finished cells).
Finding: kappa-only n* (round 1) under-sizes (V0 decisive 0.23 of uncapped); sizing on the verdict's own statistics with power is far larger and mostly beyond any realistic cap near the tipping point, so the honest output there is 'abstain, needs ~n*'.
Definitions reconciled from the REAL round-2 logs (no new runs): correct-approve 0.82 = 147/180 truly-better runs pooled over five fatigue shapes (R2-3, N=4000, logs only); linear shape alone = 39/40 (0.975, the diagram's left panel); slice m=1: 4/12 = 0.33 on strong-better (lift >= +0.02, only kappa=0) and 4/24 = 0.17 over all truly-better (kappa=0 and .2); the '59+ runs' are the 60 held-out (seeds 100-111) truly-worse runs at taste x1 pooled over kappa .4-1.5 (228 over taste x1-3).

# ROUND 4 (2026-10-20): panel-follow-up fixes. ALL NEW RUNS BELOW USE THE STAND-IN WORLD (exp13_lib.py still missing); re-run on the real exp13_lib before quoting any R4 number. P39-P40 pre-registered in Addendum 6 before running.
Post-hoc (not pre-registered), REAL logs, analysis only (an_percell.py): per-kappa-cell verdict tables. R2-3 logs only: truly-worse 0/240 false approvals (CP95 <= 0.012), near-boundary stratum (truly worse, |true lift| <= 0.01) 0/120 (CP95 <= 0.025); truly-better false reject 0/180 (linear-only 18/180); abstention on truly-better 0.183. R2-5 slice audit taste x1: truly-worse 0/60 (CP95 <= 0.049) but NO truly-worse cell within 0.01 of zero (nearest -0.013), so the near-boundary slice stratum had zero real runs; abstention on truly-better 0.833.
| # | Claim | Result (stand-in) |
|---|---|---|
| P39a | W2 generator (probit link + per-user lognormal kappa, sigma .75), logs only, v4 four-shape rule: pooled false approval CP95 upper <= 0.05 | FAIL: 8/144 (CP95 upper 0.098); all 8 in one cell, quad kappa .4 (true lift -0.0027, 8/24 approved); v3 24/144, linear-only 24/144 |
| P39b | near-boundary stratum CP95 upper <= 0.10 | FAIL: 8/72 (0.192) |
| P39c | false reject <= 0.10 and abstention on truly-better <= 0.50 | PASS: 0/96 false rejects; abstention 0.24 |
| P39d | correct-approve >= 0.50 at lift >= +0.02 (lin .4) | PASS: 24/24 |
| P40a | slice audit, taste x1, 3000 users, near boundary: 0 false approvals, near-boundary CP95 upper <= 0.10 | PASS: 0/90 truly-worse, 0/60 near-boundary (CP95 upper 0.049) |
| P40b | slice false reject <= 0.10 | PASS: 0/30 |
Descriptive: slice audit abstains on 100% of runs with |true lift| <= 0.01 (90/90) and on 80% of truly-better runs (kappa .2, +0.010): near the tipping point the audit mostly returns NEED RANDOMIZED DATA. Tail guard cut out-of-family false approvals from 24 to 8 (of 96 truly-worse convex+quad), not to <= 5%.
Post-hoc exploratory (NOT pre-registered; an_r4_margin.py): requiring all interval lower ends > +0.002 instead of > 0 gives 1/144 false approvals (CP95 upper 0.033), correct-approve 0.73 (0.76 at margin 0), 1.00 at lift >= +0.02. The margin equals the 'truly worse' cutoff, so this is circular; it is registered below as the next test, not adopted.
Cost of the randomised slice (descriptive, out/r4_cost.txt): OBD real A/B CTR Random 0.005124 vs BTS 0.006743 = 24.0% fewer clicks; stand-in simulator 27-33% fewer clicks (about 400-590 clicks lost per 1,000 slice users over 6 rounds). Timing: one audit about 3 s (logs, B=30, four shapes) and 2.5 s (slice, B=40) on one CPU core; the 264-audit W2 grid took 13.5 min.
Wording fix (no code change): the code already used two-sided 95% percentile intervals (quantiles .025/.975) with z = 1.96 in n*, so "95% lower bound" was a wording mismatch, not a numerical one; abstract and diagram now say two-sided 95% intervals, lower/upper ends.
Not done: panel's optional twists (non-uniform slice exposure design, tipping-margin metric, verdict reliability diagram) and a prior-work statement for the team (cannot be invented). Repository URL left as an explicit placeholder in abstract_v29.md.
Re-run on the real world: PYTHONPATH=. python3 r4_e1.py 400 424 out/r4_e1.jsonl && python3 r4_e2.py 500 530 out/r4_e2.jsonl && python3 an_r4.py   (with the real exp13_lib.py next to the scripts, not standin/).

# ROUND 4 REAL-WORLD RE-RUN (2026-10-20; real exp13_lib.py + ope_pilot.py from p3_round2_runs.zip; Addendum 8). SUPERSEDES the stand-in Round 3/4 numbers above, which stay in the record as stand-in only (out/standin/).
Real library reproduces logged truths exactly (taste x1 lin .4 -0.0132, .2 +0.0053). Post-hoc per-cell tables on real round-2 logs: see an_percell.py (logs-only 0/240 false approvals, 0/120 near-boundary, CP95 upper .025; slice 0/60).
| # | Claim | Real result |
|---|---|---|
| P37 | three-shape rule false approval <= 5% on out-of-family truly-worse (convex+quad) | FAIL: 12/80 = 0.15 (CP95 upper 0.232); all 12 in quad kappa .2 (true -0.0041): 12/16 approved |
| P38 | tail guard cuts it; in-family correct-approve (lin .4, +0.010) >= 0.50 | PARTIAL: FA 12 -> 1/80 (CP95 upper 0.058) PASS; correct-approve 16/16 -> 4/16 = 0.25 FAIL (stand-in wrongly predicted 16/16) |
| P39a | second generator (probit + per-user kappa), four shapes, logs: pooled FA CP95 upper <= 0.05 | PASS: 0/192 (upper 0.015). v3 4/192, linear-only 4/192 |
| P39b | near-boundary stratum <= 0.10 | PASS: 0/192 (all truly-worse cells within 0.01) |
| P39c | false reject <= 0.10 and abstention on truly-better <= 0.50 | FAIL on abstention: 0/96 false rejects, abstention 0.521 (v3 0.302; linear-only false-rejects 11/96) |
| P39d | correct-approve >= 0.50 at lift >= +0.02 (lin .4, +0.022) | PASS: 22/24 = 0.917 |
| P40a/b | slice audit near boundary (kappa .3, .35: 60 runs): 0 false approvals, bound <= 0.10; false reject <= 0.10 | PASS: 0/90 truly-worse, 0/60 near-boundary (upper 0.049); 0/30 false rejects |
| P41 | APPROVE margin +0.002 | NOT TRIGGERED (P39a/b passed). Post-hoc: margin only lowers correct-approve (0.48 -> 0.38) with 0 false approvals to remove. |
| P34-P36 | closed-loop sizing (R3-1) | NOT RUN on the real world (stretch item); stand-in result (n* above cap in 46/48 pilots) is stand-in only |
Descriptive: slice audit abstains on 98.7% of runs (150: 148 NEED, 2 REJECT, 0 APPROVE) and on 100% of truly-better runs at kappa .2 (+0.0053): safe but nearly always asks for more data near the tipping point. The stand-in's second-generator failure (8/144) did NOT reproduce on the real world.
Wording fix, cost of slice (OBD 24%, stand-in sim 27-33%), runtime (about 6 s per audit on one CPU core in the real world; 312-audit grid 32 min): as in the stand-in block.

# ROUND 5 (2026-10-21, REAL world; Addendum 9 pre-registered before any R5 audit; r5_lib.py, r5_e1.py, an_r5.py; logs out/r5_*.jsonl, out/r5_all.csv)
| # | Claim | Result |
|---|---|---|
| P42a | tail-targeted slice (repeat previous item w.p. .5) lowers abstention on truly-better by >= 20 pts vs uniform, NS=3000 | FAIL: abstention tail 0.72 vs uniform 0.59 (kappa 0 and .2, 32 runs each); correct-approve 0.28 vs 0.38 |
| P42b | tail false approvals on truly-worse = 0/48 | PASS (CP95 upper 0.061); uniform also 0/48 |
| P42c | cost | tail clicks per user-round 0.114 vs uniform 0.125 (8.3% fewer; 50.9% below old policy vs 46.5%). Median SE of kappa-hat halves (0.026 vs 0.048) yet abstention does not fall: the one-step (round-0) lift interval, not kappa, probably binds (hypothesis, layers not separated) |
| P43a | abstention on truly-better at the 8,000 cap <= 0.50 | FAIL: 0.60 (kappa 0 +0.037: approve 0/.62/.70/.80 at NS 1.5k/3k/6k/8k; kappa .2 +0.005: approve 0/.12/.10/0; median n* about 86,000) |
| P43b | 0 false approvals on truly-worse across all designs/NS | PASS: 0/126 (CP95 upper 0.023) |
| P44 | tipping margin Phi((k-hat - k*)/SE) calibrated: Brier < constant, mean gap <= 0.15 | PASS: Brier 0.082 vs 0.250; n-weighted gap 0.059. Over-predicts 'worse' for slightly-better policies (bin .1-.3: pred .20, obs 0, n=22; bin .3-.5: pred .42, obs .24, n=21): safe direction; only 5 true-lift values (reliability_tipping_margin.png) |
Real-world closed-loop sizing (R3-1, seeds 200-213, 84 pilots; 51 NEED): P34 FAIL (V2: 1 of 51 uncapped, 0 decisive; V0 decisive 5/35 uncapped, 0.10 overall), P35 PASS (0 false approvals after re-audit, 0 false rejects; pilot 0/56 truly-worse), P36 FAIL (V2 n* <= cap in 2% of NEED pilots; median n* V0 3,571 / V1 65,288 / V2 133,240). Closed-loop sizing is dropped from the plan.
Consequences carried into abstract_v32.md: KuaiRand moved from stretch to plan (Core); stretch = variance-reduced static layer, sensitivity bounds, sequential slice with early stopping; 'minimum certifiable lift at the cap' (about +0.04) and the tipping margin added; effort now ~17 core + 9 stretch engineer-days.

# ROUND 6 (2026-10-21, REAL world; Addendum 10 pre-registered): which layer causes abstention? (r6_e1.py, an_r6.py, out/r6.jsonl; 64 slice audits, kappa 0 (+0.037) and .2 (+0.005), NS 3000/8000, 16 seeds)
H1 FAIL: static (one-step) lower end <= 0 in only 43% of NEED runs (needed >= 70%). H2 FAIL: some shape's forecast lower end <= 0 in 82% of NEED runs (needed <= 50%). So the hypothesis 'the one-step lift interval limits approval' is REJECTED and removed from the abstract.
What actually happens: at +0.037 lift (kappa 0) NEED runs are static-bound 75% (forecast 33%); at +0.005 (kappa .2) the forecast interval binds in 100% (static 31%): forecast point estimates there are 0.002-0.005 against SD 0.007-0.012 (static SD 0.013-0.018; median static/forecast SD ratio 1.37). Abstention near the tipping point is mostly the small forecast lift itself (power), not one layer's variance. At kappa 0: approve 7/16 at 3000, 13/16 at 8000; kappa .2: 0/32.

# ROUND 7 (2026-10-21, REAL world; Addendum 11-12 pre-registered before the runs). Re-tests the claims under the FINAL four-shape rule v4 (lin, log, mem7, tail2), which the abstract states but earlier slice runs (R2-5, R3-1, R4-2, R5, R6) and the R2-3 logs-only runs did NOT use (they used three shapes).
| # | Claim | Result |
|---|---|---|
| P45a | out-of-family (convex .6 .9, quad .2 .4 .8), logs only, fresh seeds 1000-1031 (160 truly-worse): v4 false approvals <= 3/160 (CP95 upper <= 0.05) | PASS: 0/160 (upper 0.0185). Three-shape rule on the same runs: 20/160 |
| P45b | pooled with earlier real R3-3 (80 runs, 1 FA): <= 0.05 | PASS: 1/240 (upper 0.0196). Quad .2 cell 0/32 in the new runs, so the earlier 1/80 was sampling noise against a 5.8% bound. Tail guard effect: three-shape 12/80 + 20/160 = 32/240 -> four-shape 1/240 |
| P46a | linear logs, v4 correct-approve at +0.034 >= 0.50 | PASS: 20/20 |
| P46b | v4 false approvals over truly-worse = 0 | PASS on count: 0/40 (kappa .8, 1.0), CP95 upper 0.072. Prereg error: kappa .6 (true -0.0017) is 'marginal' under the -0.002 cutoff, so only 40 runs (not 60) are truly worse; with kappa .6 as worse 0/60 (0.049) |
| P46c | v4 false rejects on truly-better = 0 | PASS: 0/40 |
| P47a | slice (taste x1, 3,000 users, v4), truly-worse 112 runs: 0 false approvals | PASS: 0/112 (upper 0.026) |
| P47b | near-boundary slice (kappa .3, .35; 32 runs): 0 FA, bound <= 0.10 | PASS: 0/32 (upper 0.089) |
| P47c | slice false rejects on truly-better <= 1/32 | PASS: 0/32 |
| P47d | slice correct-approve at +0.037 (3,000 users) >= 0.50 | FAIL: 4/16 = 0.25 (three-shape rule on the same runs 7/16; pooled three-shape over four seed sets 28/60 = 0.47). Abstention on truly-better 0.875 |
| P48a | slice correct-approve at +0.037 at the 8,000 cap >= 0.50 | PASS: 13/16 = 0.81 |
| P48b | abstention on truly-better at the cap <= 0.50 | FAIL: 19/32 = 0.594 (kappa .2, +0.005: 16/16 abstain; 0/16 approvals) |
Descriptive: four-shape correct-approve at +0.010 (logs, linear) is 2/20 vs 20/20 for three shapes: the tail guard removes small-lift approvals. The diagram's left panel previously showed the three-shape rule (kappa .4: 95% approve); it now shows the final rule (10%). Earlier prototype figures quoted as 0/240 (logs) and 0/228 (slice) were three-shape results; the four-shape counts are in this table and in R4-1 (0/192 second generator).
Reproduce: python -m experiments.r7_e1 1000 1016 results/r7_e1_a.jsonl (and 1016 1032 -> _b); r7_e2 1100 1110 / 1110 1120; r7_e3 1200 1208 / 1208 1216; r7_e4 1300 1308 / 1308 1316; then python -m analysis.an_r7. About 60 minutes on two CPU cores for all 436 audits (4-9 s each).

# ROUND 8-9 (2026-10-22, REAL world; Addenda 13-14 pre-registered before the runs). Motivated by the judge-panel read of abstract v38.
| # | Claim | Result |
|---|---|---|
| P49a | four-shape rule v4, LOGS ONLY under hidden taste x1: false approvals CP95 upper <= 0.05 | FAIL: 17/80 truly-worse approved (kappa .4 16/16, kappa .6 1/16); upper 0.302. At taste x2: 64/112. Every earlier logs-only result had no hidden taste. |
| P49b | rule v5 (logs-only may not APPROVE): false rejects on truly-better <= 10% | PASS: 0/32 (taste x1; no truly-better cell exists at x2). v5 cap adopted. |
| P50a | held-out generator W3 (step / exponential / late-onset fatigue, per-item kappa, kappa coupled to taste), uniform slice, 3,000 users: false approvals CP95 upper <= 0.05 | FAIL: 37/144 (upper 0.324): step 18/48, late 19/48, exponential 0/48 |
| P50b | near-boundary truly-worse <= 0.10 | FAIL: 15/80 (upper 0.274) |
| P50c | false rejects <= 10% | PASS: 0/48. Correct-approve 12/48, abstention 0.75 |
| P51a | tail-targeted slice (R9-1, fresh seeds 5000-5015) false approvals CP95 upper <= 0.10 | FAIL: 12/96 (upper 0.195): step 0/48, late-onset 12/48 |
| P51b | false rejects <= 10% | PASS: 0/32; correct-approve 15/32 |
Consequence: fatigue that only starts at the third or later repeat is not covered by the verdict; the abstract says so. The tail guard's earlier 1/240 is on its own design shapes (convex, quad). Reproduce: python -m experiments.r8_e1 3000 3016 results/r8_e1.jsonl; python -m experiments.r8_e2 4000 4016 results/r8_e2.jsonl; P3_SLICE=tail P3_CELLS=step,late python -m experiments.r8_e2 5000 5016 results/r9_e1.jsonl; python -m analysis.an_r8.

# ROUND 10 (2026-10-22, Addendum 15 pre-registered): n* with a pilot-uncertainty band. 3,000-user slice pilots, linear fatigue, taste x1, kappa 0/.2/.3/.4/.6, 32 pilots each (seeds 6000-6031).
| # | Claim | Result |
|---|---|---|
| P52a | band [n*(|e|+1.96 se), n*(|e|-1.96 se)] contains the oracle n* in >= 90% of pilots | FAIL: 0.85 (kappa 0: .94, .2: .97, .3: .88, .4: .81, .6: .66) |
| P52b | point n* within 2x of the oracle in >= 50% | FAIL: 0.34 (point n* is too small: kappa .4 median 4,259 vs oracle 12,769) |
| P52c | band upper end <= 8,000 => oracle <= 8,000 in >= 90% | FAIL: 27/32 = 0.84 (32 pilots declared affordable) |
Descriptive: upper end infinite in 28% (kappa 0), 97% (.2), 84% (.3), 38% (.4), 0% (.6) of pilots. Consequence: n* is reported as a band, labelled indicative; the point value under-sizes, and the band under-covers when the true effect is clearly nonzero (kappa .6). Reproduce: python -m experiments.r10_e1 6000 6032 results/r10_e1.jsonl; python -m analysis.an_r10.

# ROUND 11 (2026-10-22, Addendum 16 pre-registered before any run): rule v6 = repeat-heavy 10-round slice + coverage guard (APPROVE only if <= 5% of the new policy's forecast impressions have prior counts above the slice's support), fourth generator W4 (cliff4 / late4 / quadlate, taste-coupled kappa), 16 fresh seeds per cell (7000-7015).
| # | Claim | Result |
|---|---|---|
| P53a | false approvals on truly-worse (144 runs) CP95 upper <= 0.05 | FAIL: 18/144, upper 0.180 (cliff4 1, late4 10, quadlate 7) |
| P53b | near-boundary (|true lift| <= 0.01, 96 runs) upper <= 0.10 | FAIL: 16/96, upper 0.242 (the other 2 false approvals have true lift -0.012) |
| P53c | false rejects <= 10% | PASS: 0/48 |
| P53d | correct-approve on truly-better >= 0.25 | PASS: 25/48 = 0.52 |
Guard: unsupported share 2-4%, so the guard passed in all 288 audits and changed no verdict (v5 = v6). The repeat-heavy 10-round slice itself lowered false approvals on W3 from 12/96 (6 rounds) to 5/96 (descriptive: W3 is no longer held out). P54 (saved R8-2 data): single-shape false approvals lin 56, log 78, mem7 69, tail2 37, four-shape agreement 37 of 144, so agreement ties the tail guard alone. Consequence: fatigue that starts after the third repeat is not reliably covered, and the abstract states the measured rates. Reproduce: python -m experiments.r11_e1 7000 7016 results/r11_e1.jsonl; python -m analysis.an_r11.

# ROUND 12 (2026-10-22, Addendum 17 pre-registered before the run): rule v7 = v6 + free-form count-curve veto (coefficient per prior-count bin 1..6, >=7; APPROVE also needs its static and forecast lower ends > 0). Fifth generator W5 (cubic, q2, expl3; taste-coupled kappa), 10-round repeat-heavy slice, 3,000 users, 16 fresh seeds per cell (8000-8015).
| # | Claim | Result |
|---|---|---|
| P55a | false approvals on truly-worse (144 runs) CP95 upper <= 0.05 | PASS: v7 0/144, upper 0.021 (v6 on the same runs: 6/144, upper 0.081) |
| P55b | near-boundary (48 runs) upper <= 0.10 | PASS: v7 0/48, upper 0.061 (v6: 6/48) |
| P55c | false rejects <= 10% | PASS: 0/48 |
| P55d | correct-approve >= 0.25 | PASS: 26/48 = 0.54 (v6: 29/48) |
Descriptive W4 retro (12 cells, 8 seeds, seeds 8000-8007; W4 was seen by R11): v7 false approvals 1/72 (upper 0.064; late4 kappa 1.6, true lift -0.0038), near-boundary 1/48 (upper 0.095), false rejects 0/24, correct-approve 8/24 (v6: 7/72 false approvals, 13/24 correct-approve). Cost: the veto trades about 0.2 correct-approve (W4) or 0.06 (W5) for removing the delayed-onset false approvals. Limits: one fresh generator family; the free-form curve is estimated only for repeat counts the slice shows (up to 7). Reproduce: python -m experiments.r12_e1 8000 8016 results/r12_e1.jsonl W5; python -m experiments.r12_e1 8000 8008 results/r12_e1_w4.jsonl W4; python -m analysis.an_r12.

# ROUND 13 (2026-10-27, REAL world; Addendum 18 pre-registered before any R13 audit). Motivated by the strict judge-panel read of abstract v39 + diagram. Output: results/r13_summary.txt (python -m analysis.an_r13).
| # | Claim | Result |
|---|---|---|
| P56a | guard (unsupported share > 5%) fires in >= 90% of 96 audits when the new policy is sharper (TN 0.2) | PASS: 96/96 (unsupported share 0.088-0.090) |
| P56b | v7 false approvals on truly-worse <= 1/72 | PASS: 0/72 (CP95 upper 0.041). Without the guard (v5) also 0/72 on these runs, so the stress test shows the guard fires, not that it prevents a false approval |
| P56c | v7 false rejects on truly-better <= 10% | PASS: 0/24 |
| P56 desc | v5 (no guard) correct-approve 23/24; v6 and v7 0/24 | the guard converts every approval into NEED RANDOMIZED DATA when the new policy repeats beyond the slice's support (abstention by design) |
| P57a | before/after wrong sign in >= 50% of 200 runs, preregistered drift d = 1.0 along DRIFT_DIR | FAIL: 0/200 (mean before/after +0.049 vs truth +0.075). d = 2.0, 3.0: 0/200, before/after rises (+0.068, +0.106): that direction lowers the average logit over items, not every item's |
| P57b | SNIPS and DR 95% intervals cover the truth round-one lift in >= 90% of runs | PASS: 187/200 = 0.935 for both (mean widths 0.017 / 0.019) |
| P57 amend | uniform logit shift (every item's logit lowered by delta; amendment fixed before running), delta 0.5 and 1.0, same claims | delta 0.5: wrong sign 96/200 = 0.48 (P57a FAIL by 2 points); delta 1.0: 200/200 = 1.00 (PASS); P57b PASS in both (0.935) |
Descriptive R13-2 (saved W5 logs, 192 audits, post hoc): single shapes false approvals lin 19/144, log 68, mem7 74, tail2 6; the free-form model alone 0/144 (correct-approve 26/48), identical to the full rule v7. Four-shape agreement alone = tail2 alone = 6/144; dropping tail2 gives 19/144, dropping any other shape gives 6/144. So on W5 the free-form veto does the work and the four-shape agreement adds nothing beyond tail2; the four-shape rule was designed on W3/W4, which informed it.
Logs-only under hidden taste (saved R8-1, 224 audits): v4 REJECT on truly-better 0/32 (taste x1; no truly-better cell at x2); the mean one-step SNIPS lift exceeds the true 10-round lift by 0.092, i.e. hidden taste biases toward APPROVE in this simulator, so logs-only REJECT is conservative here; taste that biases the other way is untested.
Cost: 6.1 s per audit on one CPU core (96 audits; 4,000 logged + 3,000 slice users, B = 30, five models).
Smoke test and amendment disclosures: see Addendum 18.
Reproduce: P3_TN=0.2 python -m experiments.r13_e1 9000 9004 results/r13_e1_a.jsonl (and 9004 9008 -> _b); python -m experiments.mvp_drift 0 200 results/mvp_drift_dir_d1.0.jsonl 1.0; P3_DRIFT_MODE=logit python -m experiments.mvp_drift 0 200 results/mvp_drift_logit_d1.0.jsonl 1.0; python -m analysis.an_r13.

# ROUND 14 (2026-10-28, REAL world; Addendum 19 pre-registered before the 192 audits). Sealed generator W6 (sigm, hump, logsq; added after rule v7 froze) + tipping margin vs CI-only score. Output: results/r14_summary.txt (python -m analysis.an_r14).
| # | Claim | Result |
|---|---|---|
| P58a | v7 false approvals on W6 truly-worse (144 runs): CP95 upper <= 0.05 | PASS: 0/144 (upper 0.021) |
| P58b | near-boundary (48 runs) upper <= 0.10 | PASS: 0/48 (upper 0.061) |
| P58c | false rejects on truly-better <= 10% | PASS: 0/48 |
| P58d | correct-approve on truly-better >= 0.25 | PASS: 26/48 = 0.54 (22 abstain) |
| P59a | Brier(Phi(margin)) < constant | PASS: 0.0035 vs 0.1875 (CI-only score 0.0049) |
| P59b | AUC(margin) >= AUC(CI-only) - 0.02 | PASS, TIE: 1.000 vs 1.000 (both separate every worse run from every better run) |
| P59c | saved R5 runs with verdict NEED: margin AUC >= 0.70 | PASS: 0.939 (n = 211, worse 125; only 5 distinct true lifts, correct-shape generator, so a favourable test) |
Descriptive, same 192 W6 runs: single shapes false-approve lin 0, log 1, mem7 3 (CP95 upper 0.053, would miss the 5% target), tail2 0; free-form alone 0; v5, v6, v7 all 0; a one-step logs-only gate (SNIPS lower end > 0) approves 144/144 truly-worse. Guard passed in all 192 audits (unsupported share <= 5%).
Reading (honest): W6 is smooth and nearly monotone, so the linear and tail2 models alone also reach 0/144; W6 shows that v7 does not fail on fresh shapes and that a one-step gate always fails, but it does NOT show that the guard or the veto earn anything (that evidence is W3-W5: delayed onset, linear 19/144 and four-shape 6/144 on W5). The margin ties the plain interval-based score; it is an interpretable unit (fatigue strength at which lift flips), not extra discrimination. W6 was authored by the rule's authors: sealed from the rule, not independent of the team.
Reproduce: python -m experiments.r14_e1 10000 10016 results/r14_e1_a.jsonl 0 (and ... _b.jsonl 1); python -m analysis.an_r14.

# ROUND 15 (2026-10-29, Addendum 20 pre-registered before the W7 and larger-B runs). Third judge panel: 4 x ADVANCE at 4.00-4.20, 1 x REJECT at 3.90.
| # | Claim | Result |
|---|---|---|
| P60a | W7 (40 random worlds x 3 datasets, 120 audits): v7 false approvals <= 5% of truly-worse audits | PASS: 0/36 (limit 1), CP95 upper 0.080 |
| P60b | near-boundary truly-worse false approvals <= 10% | PASS: 0/30 |
| P60c | false rejects on truly-better <= 10% | PASS: 0/75 |
| P60d | correct approve on truly-better >= 25% | PASS: 31/75 = 0.41 (44 abstain) |
| P60e | at most 1 truly-worse world with any false approval | PASS: 0/12 worlds, world-level CP95 upper 0.221 |
| P61a | B = 200 changes the v7 verdict in <= 4/48 R14 audits | PASS: 3/48 (2 APPROVE->NEED, 1 NEED->APPROVE) |
| P61b | no false approval at B = 200 | PASS: 0/36 |
Descriptive, W7: single shapes false-approve lin 0, log 2, mem7 6, tail2 0 of 36; free-form alone 1; v5, v6, v7 all 0; one-step logs gate 36/36. Guard passed in all 120 audits, so guard and veto added nothing here. 31 of 36 truly-worse audits are near-boundary (|lift| <= 0.01) and the rule mostly abstains rather than rejects (3 REJECT), so this is a hard but mild-harm test. W7 was written by the rule's authors after the rule froze (sealed from the rule, not independent of the team).
Independent worlds: R14's 192 audits are 12 worlds (shape x kappa cells) x 16 fresh datasets, 9 truly-worse. World-level, 0/9 (CP95 upper 0.283). W7 adds 12 truly-worse worlds; combined 0/21 worlds, CP95 upper 0.133 (audit-level 0/180, 0.017, overstates because audits in a world share structure).
B = 200 vs 30 (same datasets): forecast-interval width ratio 1.08-1.12, mean |change| in the lower end 0.0018-0.0023, always shifted down (B = 30 intervals are about 10% too narrow, as expected from a 30-draw percentile). Verdict table: APPROVE 5->5, 2->NEED; NEED 21->21, 1->APPROVE; REJECT 19->19.
Post hoc R15-3 (not pre-registered): slice kappa-hat bias at kappa 0.8, taste x0/x1/x2/x3: pooled +0.007/-0.055/-0.163/-0.298; with the true hidden term supplied +0.007/-0.009/+0.010/+0.006; logit-attenuation formula kappa/sqrt(1+0.346 gamma^2) gives 0/-0.076/-0.217/-0.338. Exposure is randomised, so the bias is attenuation (non-collapsibility), not confounding. Matches the logged R2 values (-0.049/-0.182/-0.321).
Reproduce: python -m experiments.r15_e1 20000 20003 results/r15_e1.jsonl; python -m experiments.r15_e2 200 results/r15_e2.jsonl; python -m experiments.r15_e3 results/r15_e3.jsonl; python -m analysis.an_r15.
Deviations: the B = 200 run was interrupted twice (sandbox restarts) and resumed from its saved records; no record was changed.
