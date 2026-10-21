# Pre-registration (written 2026-10-18, BEFORE any E3/E4 or new-E2 code was run)
Earlier-run (reproduction) scripts so far: test_msm, exp1b, exp12(original, 3 runs/cell), OBP cross-check. Nothing below has been run.

## Design (fixed)
- E3/E4 simulator = exp12 world (K=10, D=5), T_OBS=6 logged rounds, T_EVAL=10, ALPHA=.8, TAU_OLD=1, new-policy tau=.5, obs users N=4000, slice users 1500 unless varied, 20 seeds/cell, user-level bootstrap B=80.
- "True lift" = mean-per-round reward lift (new minus old) over T_EVAL=10 rounds under the TRUE mechanism, 60k users, common random numbers.
- Truly worse: true lift < -0.002. Truly better: > +0.002. In between = marginal (excluded from false-approval/false-reject rates, reported separately).
- Three-way rule (static CI = user-bootstrap 95% CI of SNIPS round-0 lift; kappa-hat CI = bootstrap 95%; kappa* = tipping kappa of the FITTED model):
  REJECT if static CI upper <= 0 or kappa-hat CI lower > kappa*; APPROVE if static CI lower > 0 and kappa-hat CI upper < kappa*; else NEED RANDOMIZED DATA.
- Comparator: one-step OPE alone = APPROVE iff static CI lower > 0, else REJECT.
- Slice size for NEED-DATA: n* = (1.96*c/|kappa-hat - kappa*|)^2 users, c = SD(kappa-hat_slice)*sqrt(n_slice) measured in E4.

## Claims (pass/fail, thresholds fixed now)
E3
- P1 no hidden taste, linear fatigue, logs-only, kappa in {0,.2,.4,.6,.8,1.0}: mean|kappa-hat - kappa| <= 0.05 in every cell; pooled bootstrap-CI coverage of kappa >= 0.88.
- P2 same setting: three-way false-approval rate <= 0.05 among truly-worse cells; one-step-OPE-alone false-approval >= 0.90 there; NEED-DATA rate <= 0.50 in cells with |kappa - kappa*_true| >= 0.2.
- P3 tipping point: fitted kappa* within +-0.10 of true kappa* in >= 80% of seeds (linear, no taste).
- P4 hidden taste (beta .5, gamma .8), logs-only: kappa-hat biased down by >= 0.10 in every cell and three-way false-approval >= 0.20. (Expected FAILURE of logs-only audit.)
- P5 hidden taste, whole-model-on-slice audit (n=1500): |kappa-hat bias| <= 0.08 in every cell and three-way false-approval <= 0.10.
- P6 misspecified fatigue form (fit linear-in-count; truth saturating / decaying-memory / 2-round window): in at least one form the three-way false-approval is >= 0.10 or forecast sign-error >= 0.20. (Expected negative result, scope limit.)
- P7 other mechanisms (preference drift toward shown items; logger retraining with fatigue): fatigue-only audit false-approval >= 0.10 in at least one cell. (Expected negative.)
E4
- P8 silent failure: bulk DR 95% CI coverage <= 0.10 at both hidden strengths m=1 and m=2 (bias ~.025, ~.076); best single label-free diagnostic AUC <= 0.70.
- P9 static-slice sizing: test power (bulk vs slice) <= 0.20 at m=1 for <=3000 rows; >= 0.80 at m=2 only with 3000 rows.
- P10 kappa sizing: slice-kappa SD <= 0.05 at <= 2000 users; bulk-vs-slice kappa-test power >= 0.80 at m=2 with <= 2000 users; false-alarm (m=0) <= 0.10.
- P11 whole-model-on-slice beats hybrid (bulk model + slice kappa) and bulk-only in |forecast error| in >= 70% of seeds at kappa .4, hidden taste.
- P12 closed loop: when the rule says NEED DATA and the slice is sized by n*, re-audit gives a decisive verdict in >= 70% of cases with no false approval.
E2
- P13 overlap dial: ESS/n falls monotonically as the logger sharpens; DR/SNIPS bootstrap coverage >= 0.85 while ESS/n >= 0.1.
- P14 false-approval (truly worse candidate approved) of CI rules <= 0.05 while ESS/n >= 0.1; naive before/after under drift has false-approval > 0.5.

Any deviation from this design will be reported as a deviation. Claims that fail are reported as failures.

---
# ADDENDUM (written 2026-10-18 after the first full analysis, BEFORE the runs below). Motivated by the reviewer-style critique of the abstract; these are post-hoc follow-ups and are labelled as such.
- P15 (fix for P12): static lift from the slice uses DR (slice-fitted model DM + IPW residual) instead of pure IPW. Closed loop, same 80 audits (kappa 0,.2,.4,.6 x 20 seeds, hidden taste beta .5 gamma .8, 1500-user pilot slice, cap 8000): (a) among NEED cases below the cap, >=70% become decisive after re-audit at n*; (b) zero false approvals; (c) pilot-slice NEED rate on truly-better runs falls from 0.80 to <=0.50.
- P16 (second world, ALPHA=0.5 logger, TN=0.25 candidate, same code, cells A and B, 20 seeds): (a) no-taste three-way false approval <=0.05 and one-step OPE >=0.90 among truly-worse; (b) kappa-hat error <=0.05 per cell and pooled coverage >=0.85; (c) hidden taste logs-only false approval >=0.20 and 1500-user slice audit false approval <=0.10.

---
# ADDENDUM 2 (written 2026-10-18 18:4x IST, after the user uploaded the full OBD 'men' files (random 452,949 rows / 2,321 clicks; bts 4,077,727 rows / 27,495 clicks) and BEFORE any full-data E5 run; the earlier E5 run was only the 10k plumbing check)
Design: Random logs evaluate BTS; BTS logs evaluate Random; truth = on-policy A/B CTR of the evaluated policy (mean click over its own logs, as in OBP). Estimators IPW, SNIPS, DM, DR (per-position logistic reward model on user features + one-hot item). Row-level Poisson bootstrap, 300 reps (no user IDs in OBD -> rows, a deviation from the user-level rule). BTS evaluated as OBP's static zozotown-prior distribution (n_sim=100000).
- P17 coverage: the 95% bootstrap CI contains the A/B CTR for SNIPS and for DR in at least 3 of the 4 (direction x estimator) pairs.
- P18 accuracy: DR relative error vs A/B CTR <= 10% in the Random->BTS direction; naive "log-policy CTR as estimate" is >20% off in both directions (trivial contrast).
- P19 intervals: DR bootstrap CI narrower than SNIPS CI in both directions; ESS/n >= 0.10 in Random->BTS (BTS->Random is exploratory, no threshold).
Failures will be reported as failures. Truth's own sampling noise (Random 2,321 clicks, BTS 27,495) is also reported but P17 is judged on point containment.

---
# ADDENDUM 3 (written 2026-10-20, BEFORE any R2 code was run). Motivated by the round-1 judge-panel critique (W1,W3,W4,W5, ablation). New library r2_lib.py; same world as exp13_lib (K=10, D=5, T_OBS=6, ALPHA .8, TAU_OLD 1, TN .5).
Findings from re-reading the round-1 code/results before these runs (not experiments): (i) the fitted model had NO round-index term although abstract v26 said it did; (ii) abstract v26's "+0.074 vs +0.010 at kappa=0.4" is the NO-taste cell (A_lin_k0.4: one-step SNIPS +0.075, true +0.010); with hidden taste (B_taste_lin_k0.4) one-step is +0.084 and true is -0.013; (iii) the "85%" before/after wrong-sign figure came from exp1b; the MVP script e1_table.py gives 82% (200 runs); (iv) slice kappa bias in round 1 was negative and grew with kappa (-0.017 .. -0.066) = toward APPROVE.
Estimators on the slice: E_pool (current pooled logit), E_ri (pooled + user random intercept, variance 1), E_fe (within-(user,item) first-vs-second-exposure conditional contrast: kappa1 = log(n10/n01) over discordant pairs).
## R2-1 slice kappa estimators (slice mode, lin truth, hidden taste m in {1,2,3} with beta=.5m, gamma=.8m, kappa in {.4,.8}, n_slice in {1500,3000}, 100 seeds/cell)
- P20: E_pool bias <= -0.05 at m=2, kappa=.8, n=3000; |bias| increases monotonically with m at kappa=.8.
- P21: E_fe |bias| <= 0.03 in every cell at n=3000.
- P22: E_fe SD <= 0.10 at n=3000 (every cell).
- P23: E_ri reduces |bias| vs E_pool by >=50% at m=2, kappa=.8, n=3000.
## R2-2 ablation: randomise every impression vs last impression only (old policy w/ taste m=1 for rounds 1-5, uniform at round 6; kappa in {.4,.8}; n=1500; 100 seeds)
- P24: last-only pooled-logit kappa bias <= -0.10 at kappa=.8 AND |bias_last| >= 2 x |bias_every| at both kappa values.
## R2-4 round-index term and horizon (no taste, logs-only, N=4000, lin truth + generic per-round logit decay delta in {0,.1,.2} per round continuing to round 10, kappa in {.2,.6}, 30 seeds)
- P25: model without round term: |kappa-hat bias| >= 0.05 at delta=.2 in at least one kappa; with round term: |bias| <= 0.05 in all cells.
- P26: with round term, trend held flat after round 6: forecast-lift sign correct in >=90% of non-marginal runs, median |error| <= 0.01 (H=10).
## R2-3 three-shape guard (logs-only, no taste, N=4000, B=60; fit shapes: lin g=c; log g=log(1+c); mem g=sum_{s<t} 0.7^(t-1-s)1[a_s=a_t]; truths lin(.2,.4,.6,.8,1), sat(.4,.9,1.5,2.5,4), decay(.4,.9,1.5,2.5), window(.4,.9,1.5,2.5), convex(.2,.4,.6,.9); 20 seeds)
Rule: per shape, APPROVE iff static (SNIPS round-0) CI lower>0 and forecast-lift 95% joint-bootstrap CI lower>0; REJECT iff either upper<=0; else NEED. Three-shape rule: APPROVE only if all 3 APPROVE; REJECT only if all 3 REJECT; else NEED. Linear-only rule = the lin shape alone.
- P27: three-shape pooled false approval (truly-worse, true 10-round lift < -0.002) <= 0.05 including convex.
- P28: three-shape NEED rate on truly-better runs <= 0.50 pooled.
- P29: at sat kappa=.9 (round 1: linear-fit sign error 100%, false rejects 80%) three-shape false-reject rate <= 0.20.
- Descriptive (no threshold): share of new-policy impressions in rounds 7-10 whose prior same-item count exceeds the 99th percentile of the logged count.
Failures will be reported as failures.

## R2 RESULTS of first block (analysis after run; thresholds above were fixed before): P20 PASS (pooled bias -0.049/-0.182/-0.321 at m=1/2/3, kappa .8, n 3000); P21 PASS (E_fe max |bias| 0.011); P22 FAIL by 0.001 (E_fe max SD 0.101 at n=3000); P23 FAIL (E_ri removes only 16% of bias); P24 PASS (last-only bias -0.27..-0.33 vs every-impression -0.02..-0.06); P25 PASS (no round term: kappa bias +0.23/+0.25 at delta .2; with it <=0.006); P26 PASS (flat: sign-correct 0.947, median |err| 0.0025; without round term sign-correct 0.60 at H=10). Side finding: true lift horizon matters (kappa .6, delta 0: H=6 +0.017, H=10 -0.002).
# ADDENDUM 4 (written 2026-10-20 BEFORE R2-5 run, after E1/E4 results, while R2-3 is still running). Rationale: pooled-slice kappa is a MARGINAL (population-averaged) coefficient, attenuated by hidden heterogeneity, but kappa* and the forecast are computed in the same marginal model, so the forecast verdict need not inherit the attenuation. R2-5 tests that directly.
Frozen rule v2 (no further changes): fit on the slice with the shapes lin/log/mem7 PLUS a linear round-index term; static lift = slice DR (shape-fitted DM + IPW residual) minus bulk round-0 old mean; forecast lift H=10, round term held at its round-6 value; joint user bootstrap B=40 (slice and bulk users); per-shape verdict as in R2-3; v3 = unanimity. Held-out seeds 100-111 (development seeds were 0-99). World: hidden taste m in {1,2,3}, kappa in {0,.2,.4,.6,.8,1.0,1.5}, slice 3000 users, bulk 4000 logged users, truth = 60k-user 10-round lift ('worse' < -0.002, 'better' > +0.002).
- P30: pooled over all truly-worse runs, v3 false approvals = 0 (so one-sided 95% Clopper-Pearson upper bound <= 0.05 needs n >= 59).
- P31: v3 correct-approve rate >= 0.50 among truly-better runs with true lift >= +0.02.
- P32: v3 false approval <= v1 (linear-only) false approval.
- P33: v3 false-approval 0 at m=3 separately.

---
# ADDENDUM 5 (written 2026-10-20, BEFORE any R3 run). Motivated by the round-1 judge panel (J1 n* lacks power; J2 out-of-family stress; J3 ablation). 
WORLD CAVEAT: exp13_lib.py was NOT in p3_round2_code_and_runs.zip. R3 runs use a STAND-IN exp13_lib (same API; constants fitted so 11 logged true-lifts match to RMSE ~0.004; logs-only kappa-hat .399 at .4, slice pooled bias -.054/-.207/-.332 at taste x1/2/3 vs logged -.049/-.182/-.321, one-step SNIPS +.074 vs +.075). It is NOT the original world: every R3 number must be re-run on the real exp13_lib before it is quoted as a result. r2_lib.py gained shapes quad (g=c^2), kink (g=max(c-2,0)), tail2 (g=c+max(c-2,0)).
Deviation recorded before running: kink was planned as an out-of-family truth but true 10-round lift stays +0.0007..+0.0012 for every kappa 4..40, so it can never be 'truly worse' and cannot test false approval; dropped. Out-of-family truths used: convex (round 2) and quad (new).
## R3-1 closed-loop sizing (hidden taste x1, slice pilot 3000 users, bulk 4000, rule v3 = frozen v2 three-shape unanimity, B=30, kappa in {0,.2,.4,.6,.8,1.0}, seeds 200-213, cap 8000)
Variants sized from the same pilot, each re-audited on a FRESH slice of n* users (bulk reused):
 V0 round-1 rule: n*=(1.96 c/|kappa-hat - kappa*|)^2 (lin shape, c=SD(kappa-hat)*sqrt(n_pilot)).
 V1 verdict-based, no power: per shape n=(1.96 sd*sqrt(n_pilot)/|est|)^2 for the statistics the verdict uses (static slice-DR lift, forecast lift); APPROVE route needs both, REJECT route the cheapest negative one; n*=max over shapes.
 V2 as V1 with power 0.80: (1.96+0.84).
- P34: V2 decisive rate >= 0.70 among NEED pilots with n*<=cap, and V2 > V0 by >= 0.20 (same pilots).
- P35: zero false approvals over all second stages (all variants); false rejects <= 0.10 among truly-better runs.
- P36: V2 median n* <= cap (8000) in at least 50% of NEED pilots (otherwise report the feasible regime).
## R3-3 out-of-family stress + tail guard (logs only, no taste, N=4000, B=30, seeds 300-315). Truths: lin .4,.8,1.0 (in-family control); convex .2,.6,.9; quad .05,.2,.4,.8 (out of family). Rule v3 = lin/log/mem7 unanimity; v4 = v3 plus tail2 (slope doubles beyond count 2) must also agree.
- P37: v3 false approval pooled over out-of-family truly-worse runs (convex+quad, true lift < -0.002) <= 0.05 (n>=59 for the bound).
- P38: v4 false approval <= v3 on the same runs; v4 correct-approve on in-family truly-better (lin .4) >= 0.50.
Failures will be reported as failures.

---
# ADDENDUM 6 (written 2026-10-20, BEFORE any R4 audit was run). Motivated by the round-1 panel follow-ups: (J1/J3) simulator = fitted model; (J2) no per-cell / near-boundary false-approval target, no abstention-rate or false-reject target.
WORLD CAVEAT: still the STAND-IN exp13_lib (real file missing). Every R4 number is a stand-in number and must be re-run on the real exp13_lib before it is quoted as a result. True-lift scans (truth only, no audits) were looked at to choose cells: W2 lin 1.0 is +0.0012, 1.5 is -0.0065; quad .4 is -0.0027; convex .9 is -0.0053; stand-in taste x1 lin .35 is -0.0045, .4 is -0.0086.
Post-hoc (NOT pre-registered, analysis of existing REAL logs only): an_percell.py per-cell tables for R2-3 and R2-5.
## R4-1 second generator W2 (r4_lib.py): probit click link (fitted model stays logit) + per-user lognormal kappa_i (sigma .75, mean kappa). Logs only, no taste, N=4000, B=30, seeds 400-423 (24/cell). Rule v4 = lin/log/mem7/tail2 unanimity (v3 = first three; lin-only reported).
Cells: lin .4 .8 1.0 1.5 2.0 | convex .4 .9 1.5 | quad .2 .4 .8. Truly worse = true 10-round lift < -0.002, better > +0.002.
- P39a: v4 pooled false approval over truly-worse, one-sided 95% Clopper-Pearson upper bound <= 0.05 (needs >=59 runs).
- P39b: near-boundary truly-worse stratum (|true lift| <= 0.01): v4 false-approval CP95 upper <= 0.10 (needs >=29 runs).
- P39c: v4 false-reject on truly-better <= 0.10 AND abstention rate on truly-better <= 0.50.
- P39d: v4 correct-approve on truly-better with true lift >= +0.02 (lin .4 only) >= 0.50.
- Descriptive, no threshold: v3 and linear-only false approval on convex+quad.
## R4-2 slice audit near the boundary (stand-in, hidden taste x1, 3000 slice users, 4000 bulk, rule v3 = frozen v2 unanimity, B=40, seeds 500-529 (30/cell), lin kappa .2 .3 .35 .4 .5). Near-boundary stratum = truly-worse with |true lift| <= 0.01 (kappa .35, .4: 60 runs).
- P40a: false approvals over all truly-worse runs = 0, and near-boundary stratum CP95 upper <= 0.10.
- P40b: false-reject on truly-better <= 0.10.
- Descriptive: abstention rate on truly-better and on near-boundary runs.
## R4-3 cost of the randomised slice (descriptive, no threshold): (a) OBD real A/B CTRs Random 0.005124 vs BTS 0.006743 (from e5_diag, already in RESULTS); (b) stand-in simulator: expected clicks per user-round under uniform vs old policy, 6 rounds.
Failures will be reported as failures.

---
# ADDENDUM 7 (written 2026-10-20, AFTER R4 results, for the REAL-world re-run; nothing below has been run)
- P41: v5 = v4 with APPROVE requiring every lower end > +0.002 (REJECT unchanged). On the W2 generator (r4_e1.py, seeds 600-623, real exp13_lib): false approval CP95 upper <= 0.05 pooled over truly-worse, <= 0.10 in the near-boundary stratum; correct-approve >= 0.50 on truly-better with lift >= +0.02. Note: the margin equals the 'truly worse' cutoff, so also report the same table with the cutoff moved to -0.004.

---
# ADDENDUM 8 (written 2026-10-20, BEFORE any real-world R3/R4 audit). The real exp13_lib.py + ope_pilot.py were found in p3_round2_runs.zip (work/). The real library reproduces the logged truths exactly (taste x1 lin .4 -0.0132, .2 +0.0053; no-taste lin .6 -0.0017, convex .4 -0.0039), so earlier stand-in runs are superseded: R3-1 (P34-P36), R3-3 (P37-P38), R4-1 (P39) and R4-2 (P40) are re-run unchanged on the REAL world (same thresholds, same seeds for R3: 200-213 and 300-315; R4: 400-423 and 500-529). Stand-in results stay in the record as 'stand-in'.
Only change: R4 cells are re-chosen from a real-world TRUTH scan (no audits looked at): R4-1 cells lin .4 .8 1.0 1.2 1.5 2.0 | convex .4 .9 1.5 | quad .1 .3 .4 .8 (real true10: +.022 +.0044 -.0001 -.0031 -.0061 -.0089 | +.0063 -.0060 -.0099 | +.0182 -.0021 -.0052 -.0099); R4-2 slice kappa .2 .25 .3 .35 .4 (real true10: +.0053 -.0004 -.0054 -.0099 -.0132); near-boundary truly-worse stratum there = kappa .3, .35 (60 runs). P39d uses lin .4 (+.022) as the only lift >= +0.02 cell.
P41 (v5 APPROVE margin +0.002; addendum 7) is run on fresh seeds 600-623 only if P39a or P39b fails on the real world.

---
# ADDENDUM 9 (written 2026-10-21, BEFORE any R5 audit). Real exp13_lib. Targets the largest weakness left after R4: the slice audit abstains on ~99% of runs near the tipping point.
Assumptions: (i) a slice design that depends only on PAST ACTIONS (not outcomes, not hidden taste) has known propensities and keeps the audit valid; (ii) same slice audit as r3_e1.audit (three shapes lin/log/mem7, B=30, rule v3, hidden taste x1, bulk logs N=4000); (iii) 'truly worse' = true 10-round lift < 0, 'truly better' > 0 (cells chosen so none is within 0.002 of 0).
## R5-1 tail-targeted slice (r5_lib.py): round 0 uniform; rounds 1-5: with prob q=0.5 repeat the previous round's item, else uniform over the 10 items (propensity (1-q)/K + q*1[k = previous item], known). q is fixed here and NOT tuned. Uniform vs tail, same bulk logs and seeds (700-715, 16/cell), NS=3000, kappa 0 (+.037), .2 (+.005), .3 (-.005), .35 (-.010), .4 (-.013).
- P42a: abstention on truly-better (kappa 0, .2; 32 runs) is >= 20 percentage points lower under tail than under uniform.
- P42b: tail false approvals on truly-worse (kappa .3 .35 .4; 48 runs) = 0 (CP95 upper 0.061).
- P42c (descriptive): clicks per user-round lost vs uniform slice and vs the old policy.
## R5-2 abstention vs slice size (uniform design, seeds 800-809, 10/cell, NS 1500, 6000, 8000; kappa 0, .2, .35; NS=3000 point comes from the P42 uniform arm).
- P43a: abstention on truly-better (kappa 0, .2) at NS=8000 (the cap) is <= 50%.
- P43b: 0 false approvals at kappa .35 across all NS (all designs/NS pooled, 0/N, report N).
## R5-3 tipping margin = (kappa-hat_lin - kappa*) / SE(kappa-hat_lin), SE = bootstrap SD of the logged audit; kappa* solved in the same lin model. Predicted P(worse) = Phi(margin). Pooled over all R5-1/R5-2 runs:
- P44: Brier score of Phi(margin) vs 'truly worse' is lower than the constant base-rate Brier; AND mean |predicted - observed| over reliability bins with n >= 10 is <= 0.15. (If it fails the margin is reported as an uncalibrated score, not a probability.)
## R3-1 closed-loop sizing real-world re-run: thresholds P34-P36 (above), seeds 200-213, run unchanged AFTER R5-1/R5-2.

---
# ADDENDUM 10 (written 2026-10-21, BEFORE any R6 audit). Tests the untested hypothesis in abstract_v32 stretch (1): 'the one-step lift interval limits approval'.
R6 (r6_e1.py): slice audit as r3_e1.audit (hidden taste x1, uniform slice, three shapes lin/log/mem7, rule v3), real world, truly-better cells kappa 0 (+0.0367) and .2 (+0.0053), NS 3000 and 8000, seeds 900-915 (16/cell). For every audit the static (one-step DR) interval and each shape's forecast interval are recorded; a NEED run is 'static-bound' if the static lower end <= 0, 'forecast-bound' if any shape's forecast lower end <= 0.
- H1: among NEED runs (pooled over cells and NS), the static lower end <= 0 in >= 70% of runs.
- H2: forecast lower end <= 0 for at least one shape in <= 50% of NEED runs.
- Descriptive: sd_s vs sd_f per shape; how often both bind. If H1 or H2 fails the stretch-(1) hypothesis is rejected and the abstract must drop it.
