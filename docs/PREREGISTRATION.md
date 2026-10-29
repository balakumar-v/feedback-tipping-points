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

---
# ADDENDUM 11 (written 2026-10-21 ~17:00 IST, BEFORE any R7 audit). Motivated by the strict judge-panel read of abstract v37 + diagram. REAL world. Truth scan (no audits) done first: true 10-round lift, logs-only no taste: convex .6 -0.0093, .9 -0.0122; quad .2 -0.0041, .4 -0.0110, .8 -0.0135; lin .2 +0.0343, .4 +0.0100, .6 -0.0017, .8 -0.0073, 1.0 -0.0103. Slice (taste x1, lin): k0 +0.0367, .2 +0.0053, .3 -0.0054, .35 -0.0099, .4 -0.0132, .6 -0.0211, .8 -0.0240, 1.0 -0.0250, 1.5 -0.0246.
Findings that motivate this (re-reading code/logs, no runs): (i) abstract v37 says the verdict needs all FOUR shapes (lin, log, mem7, tail2) but the diagram's left panel (R2-3) and every SLICE result (R2-5, R3-1, R5, R6, R4-2) used THREE shapes (lin, log, mem7); only R3-3 and R4-1 used four. (ii) the one-sided CP95 upper bound of the reported out-of-family 1/80 is 0.058 > 0.05.
Rule v4 (frozen, = abstract): per shape in {lin, log, mem7, tail2}: APPROVE iff static and forecast 95% interval lower ends > 0; REJECT iff either upper end <= 0; else NEED. APPROVE iff all four APPROVE; REJECT iff all four REJECT; else NEED. Truly worse: true lift < -0.002; truly better: > +0.002.
## R7-1 out-of-family false approval, logs only, no taste, N=4000, B=30 (as R3-3), fresh seeds 1000-1031 (32/cell), cells convex .6 .9 | quad .2 .4 .8 (all truly worse; 160 runs).
- P45a: v4 false approvals <= 3/160 (CP95 upper <= 0.05).
- P45b: pooled with the earlier R3-3 real runs on the same cells (80 runs, 1 FA): <= 6/240 (upper <= 0.05; the 1/80 alone is 0.058, which would fail by itself).
- Descriptive: v3 (three-shape) false approvals on the same runs.
## R7-2 linear fatigue, logs only, no taste, v4 four-shape rule, kappa .2 .4 .6 .8 1.0, fresh seeds 1100-1119 (20/cell) = left panel of the diagram redrawn under the FINAL rule.
- P46a: v4 correct-approve at kappa .2 (+0.034) >= 0.50.
- P46b: v4 false approvals over truly-worse (.6 .8 1.0: 60 runs) = 0 (CP95 upper 0.049).
- P46c: v4 false rejects on truly-better (.2 .4) = 0.
- Descriptive: v3 on same runs; correct-approve at .4 (+0.010; R3-3 prior: 0.25).
## R7-3 SLICE audit under the final four-shape rule v4 (adds tail2 to the three-shape audit of r3_e1 unchanged otherwise): hidden taste x1, uniform slice 3000 users, bulk 4000, B=30, fresh seeds 1200-1215 (16/cell), kappa 0 .2 .3 .35 .4 .6 .8 1.0 1.5 (144 audits).
- P47a: false approvals over truly-worse (kappa .3 .35 .4 .6 .8 1.0 1.5 = 112 runs) = 0 (CP95 upper 0.026).
- P47b: near-boundary truly-worse (kappa .3 .35, 32 runs): 0 false approvals (CP95 upper 0.089 <= 0.10).
- P47c: false rejects on truly-better (kappa 0 .2; 32 runs) <= 1/32.
- P47d: correct-approve on strong-better (kappa 0, +0.037) >= 0.50. (Expect FAIL or borderline: earlier v3 results at the same setting 4/12, 10/16, 7/16 across three seed sets = 21/44 = 0.48.)
- Descriptive: abstention on truly-better and overall; v3 verdict on the same runs.
Any deviation from this design will be reported as a deviation. Claims that fail are reported as failures.

## R7 RESULTS (analysis after run; thresholds above fixed before): P45a PASS (v4 0/160 false approvals, CP95 upper 0.0185; v3 20/160); P45b PASS (pooled with earlier real R3-3: 1/240, upper 0.0196; quad .2 cell 0/32, so the earlier 1/80 was sampling noise at the 5.8% bound, not a bias); P46a PASS (20/20 at +0.034); P46b PASS on count (0/40 truly-worse; NOTE prereg error: kappa .6 true lift -0.0017 is 'marginal' under the -0.002 cutoff so only 40 runs are truly worse, CP95 upper 0.072, not the 0.049 written for 60 runs); P46c PASS (0 false rejects). Descriptive: v4 correct-approve at +0.010 (kappa .4) is 2/20 (v3 20/20): the tail guard removes the in-family correct-approvals at small lifts. P47a PASS (0/112, upper 0.026); P47b PASS (0/32 near-boundary, upper 0.089); P47c PASS (0 false rejects); P47d FAIL: v4 correct-approve at +0.037 is 4/16 = 0.25 (v3 on the same runs 7/16); abstention on truly-better 0.875 (v3 0.78); pooled v3 over four seed sets at kappa 0 = 28/60 = 0.47.

---
# ADDENDUM 12 (written 2026-10-21, BEFORE the run; after R7). Slice audit at the 8,000-user cap under the final four-shape rule v4 (the abstract quotes a cap figure that so far exists only for the three-shape rule).
R7-4: as R7-3 but NS = 8000, kappa 0 (+0.0367) and .2 (+0.0053), fresh seeds 1300-1315 (16/cell, 32 audits).
- P48a: v4 correct-approve at kappa 0 >= 0.50.
- P48b: v4 abstention on truly-better (both kappas pooled, 32 runs) <= 0.50 (expected FAIL because of kappa .2).
- Descriptive: v3 on the same runs.

## R7-4 RESULTS: P48a PASS (v4 correct-approve at +0.037, 8,000 users: 13/16 = 0.81; v3 identical on these runs); P48b FAIL as expected (abstention on truly-better 19/32 = 0.594; kappa .2 (+0.005) abstains 16/16). 0/16 approvals at +0.005 even at the cap.

---
# ADDENDUM 13 (written 2026-10-22, BEFORE any R8 audit run). Motivated by the strict judge-panel read of abstract v38 + diagram v11 (two major findings). REAL world.
Findings (from re-reading code and logs, not new experiments): (i) EVERY logs-only result so far (R2-3, R3-3, R4-1, R7-1, R7-2: the 0/40, 0/160, 0/192 false-approval counts) was run with NO hidden taste (beta = gamma = 0); the only hidden-taste results are slice audits. The abstract's own motivating example (taste breaks unconfoundedness) therefore was never tested on the logs-only path. (ii) The tail guard (tail2) was added after seeing 32/240 out-of-family false approvals on convex and quad truths, so those cells (and the c^2 control) are design cells, not held-out cells.
Disclosure: one smoke-test audit (r8_e1.audit(m=1, kappa=.4, seed=1), outside the run seeds) was executed to check timing before this addendum was written. It returned APPROVE with true lift -0.0132, i.e. a false approval.
Rule v5 (frozen here) = v4 per-shape rule and four-shape agreement, plus: a LOGS-ONLY audit (no randomised slice) may return REJECT or NEED RANDOMIZED DATA but never APPROVE, because hidden taste cannot be tested from logs. With a slice, v5 = v4 unchanged.
## R8-1 logs-only under hidden taste, v4, linear fatigue, taste x1 (beta .5, gamma .8) and x2 (1.0, 1.6), kappa 0 .2 .4 .6 .8 1.0 1.5, N=4000, B=30, fresh seeds 3000-3015 (16/cell, 224 audits). Truly worse: true 10-round lift < -0.002; truly better: > +0.002.
- P49a: v4 logs-only false approvals on truly-worse at taste x1: CP95 upper <= 0.05. (Expected FAIL, given the smoke test.)
- P49b: v5 false rejects on truly-better, taste x1 and x2 pooled: <= 10%.
- Descriptive: v4 false approvals at taste x2; v4 correct-approve on truly-better (the cost of the v5 cap); one-step SNIPS estimate vs truth.
## R8-2 held-out generator W3 (p3ope/r8_lib.py), slice audit at 3,000 users, taste x1, four shapes lin/log/mem7/tail2 (rule v5 = v4 with a slice), B=30, bulk logs 4000, fresh seeds 4000-4015 (16/cell, 192 audits). W3 truths are shapes the guard was not tuned on (step 2*1[c>=3], expo (e^{.35c}-1)/.35, late 1.5*max(c-3,0)) with per-item and per-user kappa, the per-user kappa coupled to the hidden taste (kappa_i = kappa*exp(.5U-.125)). Cells chosen from a TRUTH scan (no audits looked at): step .3 (+0.0225) | step 1.2 (-0.0046) 1.6 (-0.0112) 2.0 (-0.0159) | expo .04 (+0.0203) | expo .15 (-0.0042) .2 (-0.0099) .4 (-0.0200) | late .3 (+0.0153) | late .8 (-0.0031) 1.2 (-0.0098) 2.0 (-0.0159). Truly worse = 9 cells (144 runs); near-boundary truly worse (|true| <= 0.01) = step 1.2, expo .15, expo .2, late .8, late 1.2 (80 runs); truly better = 3 cells (48 runs).
- P50a: false approvals on truly-worse (144 runs): CP95 upper <= 0.05.
- P50b: near-boundary truly-worse (80 runs): CP95 upper <= 0.10.
- P50c: false rejects on truly-better (48 runs): <= 10%.
- Descriptive: abstention and correct-approve on truly-better; per-shape table.
The rule is frozen: whatever R8-2 shows, no rule change is made afterwards; failures are reported with their counts and the abstract states the measured rate instead of the target.

---
# ADDENDUM 14 (written 2026-10-22, AFTER R8 results, BEFORE any R9 audit). R8 RESULTS: P49a FAIL (v4 logs-only under taste: 17/80 false approvals at x1, 64/112 at x2; v5 caps logs-only at REJECT/NEED, 0/32 false rejects, P49b PASS). P50a FAIL: held-out W3 uniform slice, 3,000 users: 37/144 false approvals (CP95 upper 0.324), all on the delayed-onset truths (late 19/48, step 18/48; expo 0/48); P50b FAIL 15/80; P50c PASS 0/48. Diagnosis (not yet tested): a uniform slice almost never shows an item three times in six rounds, so onset at the third repeat is invisible while the new policy repeats heavily.
## R9-1 (only remedy tested, fixed now, no tuning): the same audit with the tail-targeted slice of r5_lib (round 0 uniform; later rounds repeat previous item w.p. 0.5, propensity known), W3 cells step 1.2 1.6 2.0 | late .8 1.2 2.0 (96 truly-worse) and step .3 | late .3 (32 truly-better), fresh seeds 5000-5015, rule v5 unchanged.
- P51a: false approvals on truly-worse: CP95 upper <= 0.10 (<= 5/96); P51b: false rejects <= 10%. Descriptive: correct-approve, abstention.
If P51a fails the abstract states that delayed-onset fatigue is NOT covered by the verdict.

---
# ADDENDUM 15 (written 2026-10-22, BEFORE any R10 audit). Panel item: report n* with a pilot-uncertainty band (the pilot estimate in |estimate| is noisy, and n* explodes near zero).
Band (frozen): from a 3,000-user pilot, forecast-lift estimate e with bootstrap SE se (= sd_f / sqrt(3000)); n*(e) = ((1.96+0.84) * sd_f / |e|)^2. Band = [n*(|e|+1.96 se), n*(|e|-1.96 se)]; upper end = infinity if |e| <= 1.96 se (cannot rule out zero lift). Shown as "n* about X (band lo-hi)". Linear fatigue shape, forecast component only (the binding term in earlier rounds), taste x1, kappa 0, .2, .3, .4, .6 (true 10-round lift +0.037, +0.005, -0.005, -0.013, -0.021), fresh seeds 6000-6031 (32 per kappa, 160 pilots). Oracle n* = ((1.96+0.84) * mean pilot sd_f of that kappa / |true10|)^2.
- P52a: the band contains the oracle n* in >= 90% of pilots (infinite upper end counts as containing).
- P52b: point n* is within a factor 2 of the oracle in >= 50% of pilots (expected to fail near the tipping point).
- P52c: among pilots whose band upper end <= 8,000 (declared affordable), oracle n* <= 8,000 in >= 90%.
- Descriptive: share of pilots with infinite upper end per kappa; median band width.

---
# ADDENDUM 16 (written 2026-10-22, AFTER R10, BEFORE any R11 audit). Panel items: coverage guard (J1), freeze a fourth generator before testing a remedy (J2), four-shape vs best single shape (J1/J3, free from saved R8-2 data).
Diagnosis of the R8/R9 misses: the new policy's exposure reaches prior counts of 9, but a 6-round slice supports counts only up to 2 (uniform) or 5 (repeat-heavy, q=.5). Fatigue that starts at the 3rd-4th repeat lives in the unsupported range.
Rule v6 (frozen here) = v5 plus: (a) slice = repeat-heavy design (q=.5, propensity known), horizon 10 rounds (= H); (b) COVERAGE GUARD: APPROVE only if the share of the new policy's forecast impressions (10 rounds, 20,000 simulated users, outcome-independent) with prior count c above c_sup is at most 5%, where c_sup = the largest c with at least 100 slice impressions; otherwise the audit returns NEED RANDOMIZED DATA (REJECT unaffected). Design calculation done before writing this (no audit outcomes): uniform 10-round slice c_sup=3, unsupported share about 19% (blocked); repeat-heavy 10-round slice c_sup=7, unsupported about 2% (passes). The 5% threshold is the false-approval tolerance, chosen before any run.
Fourth generator W4 (p3ope/r8_lib.py, shapes never used in any design): cliff4 3*1[c>=4]; late4 2*max(c-4,0); quadlate .6*max(c-3,0)^2; per-item kappa and taste-coupled per-user kappa as in W3. Cells from a TRUTH scan only (no audits): cliff4 .3 (+0.0199) | 1.2 (-0.0065) 1.6 (-0.0116) 2.0 (-0.0149); late4 .3 (+0.0189) | 1.6 (-0.0038) 3.0 (-0.0075) 5.0 (-0.0087); quadlate .1 (+0.0259) | .8 (-0.0023) 1.2 (-0.0072) 2.0 (-0.0121). Truly worse (< -0.002): 9 cells, 144 runs; near-boundary (|true| <= .01): cliff4 1.2, late4 x3, quadlate .8, 1.2 = 96 runs; truly better 3 cells, 48 runs. Taste x1, slice 3,000 users, 16 fresh seeds per cell (7000-7015), four shapes, B=30. Also (descriptive, W3 is no longer held out): v6 on W3 step 1.2 1.6 2.0 and late .8 1.2 2.0 (96 runs, seeds 7000-7015).
- P53a: v6 false approvals on W4 truly-worse: CP95 upper <= 0.05.
- P53b: near-boundary truly-worse: CP95 upper <= 0.10.
- P53c: false rejects on truly-better <= 10%.
- P53d: correct-approve on truly-better >= 0.25 (the cost of the guard; no target above that is claimed).
- Descriptive: the same runs WITHOUT the guard (v5 on the 10-round repeat-heavy slice) to isolate the guard; guard pass rate; W3 retro.
- P54 (saved data, no new runs): on R8-2 uniform-slice audits, false approvals of each single shape (lin, log, mem7, tail2) vs the four-shape agreement, to test that agreement helps. Pre-registered expectation: agreement <= every single shape.
If P53a fails the abstract says delayed-onset fatigue is still not covered even with the guard.

---
# ADDENDUM 17 (written 2026-10-22, AFTER R11, BEFORE any R12 audit). R11 showed the support guard never fires and 18/144 delayed-onset false approvals remain, because every fitted shape (lin/log/mem7/tail2) is a parametric guess outside what the slice shows. New idea: stop guessing the shape inside the range the 10-round repeat-heavy slice supports.
Rule v7 (frozen here) = v6 plus a fifth model, the FREE-FORM COUNT CURVE: logit(click) = base(context, item) + f(c) + round term, where f is a free coefficient for each prior-count bin c = 1, 2, 3, 4, 5, 6, >=7 (f(0) = 0), fitted on the slice by the same penalised logit; forecast and bootstrap exactly as for the other shapes (counts above 7 use the >=7 coefficient). It acts as a VETO on approval: APPROVE needs the free-form model's own static and forecast lower ends > 0 as well; REJECT and NEED rules are unchanged (it cannot create a REJECT). Hypothesis: when the four parametric shapes are optimistic about delayed-onset fatigue, the free-form interval includes or lies below 0, so the false approval turns into NEED RANDOMIZED DATA; cost: a wider interval and fewer correct approvals.
Fifth generator W5 (p3ope/r8_lib.py, shapes new to every design and test so far): cubic .08 c^3; q2 .3 max(c-2,0)^2; expl3 exp(.5 max(c-3,0))-1; per-item and taste-coupled kappa as in W3/W4. (bump and late5 were scanned first and dropped: their truth lift never goes negative, so they cannot test false approvals.) Cells from a TRUTH scan only: cubic .05 (+0.0200) | .2 (-0.0043) .3 (-0.0116) .5 (-0.0188); q2 .1 (+0.0271) | 1.0 (-0.0081) 1.5 (-0.0139) 2.5 (-0.0197); expl3 .3 (+0.0170) | 1.5 (-0.0068) 2.5 (-0.0125) 4.0 (-0.0164). Truly worse = 9 cells, 144 runs; near-boundary (|true| <= .01): cubic .2, q2 1.0, expl3 1.5 = 48 runs; truly better 3 cells, 48 runs. Taste x1, 10-round repeat-heavy slice with 3,000 users, 16 fresh seeds per cell (8000-8015), B=30. Also descriptive: W4 retro with v7 (12 cells, 8 seeds each, 8000-8007).
- P55a: v7 false approvals on W5 truly-worse: CP95 upper <= 0.05 (<= 3/144 gives 0.054, so 2/144 or fewer).
- P55b: near-boundary truly-worse (48 runs): CP95 upper <= 0.10 (<= 1/48).
- P55c: false rejects on truly-better <= 10%.
- P55d: correct-approve on truly-better >= 0.25.
- Descriptive: v6 vs v7 on the same runs (isolates the veto); W4 retro; recorded lower ends (for a post-hoc practical-margin analysis, which is NOT a claim).
Disclosure: one smoke-test audit (cubic .3, seed 1) is run for timing before the full run. If P55a fails the abstract states that delayed-onset fatigue is still not reliably covered and reports the measured rate.

---
# ADDENDUM 18 (written 2026-10-27, BEFORE any R13 audit). Strict judge-panel read of abstract v39 + diagram (two majors per judge). REAL world.
Findings from re-reading code, logs and abstract (no new runs): (i) the abstract never stated rule v6's COVERAGE GUARD, so a reader sees no rule for a new policy that repeats beyond what the slice shows; the guard has never fired (unsupported share 2-4%, R11/R12). (ii) The abstract said "three more generators built after freezing the rule"; in fact W3 and W4 informed v6/v7 (not held out), W2 is the probit generator, and only W5 (cubic, q2, expl3) is fresh for v7. (iii) MVP check (3) was written as a forward target but the OBD control already ran (P17-P19): Random->BTS DR error -8.8%, CI misses at ESS/n 0.247. (iv) the abstract's correct-approve target (>= 0.50 at +0.02) differs from the preregistered P55d (>= 0.25). (v) logs-only REJECT false-reject rate (0/32, P49b) was not in the abstract. (vi) e1_table.py (the 82% before/after figure) is not in the archive, so MVP (2) is not reproducible from the repo.
## R13-1 GUARD STRESS: a new policy that repeats beyond the slice's support. Same audit as R12-1 (rule v7, W5 cells, 3,000-user repeat-heavy slice, 4,000 logged users, B=30) but new-policy softmax temperature TN = 0.2 (env P3_TN=0.2; default 0.5) so the new policy repeats more. Design calculation before any audit: new-policy exposure with prior count >= 8 is 8.8% (2.0% at TN 0.5); the slice supports counts up to 7, so the guard (threshold 5%) should fire. Truth scan at TN 0.2 (no audits): cubic .05 +0.0262 | .2 -0.0245 .3 -0.0366 .5 -0.0483; q2 .1 +0.0446 | 1.0 -0.0318 1.5 -0.0414 2.5 -0.0507; expl3 .3 +0.0163 | 1.5 -0.0301 2.5 -0.0396 4.0 -0.0459. Truly worse 9 cells; truly better 3 cells; no near-boundary cell exists at this TN. Fresh seeds 9000-9007 (8 per cell: 72 truly-worse, 24 truly-better audits).
- P56a: guard fires (unsupported share > 0.05) in >= 90% of the 96 audits.
- P56b: v7 false approvals on truly-worse: <= 1/72 (CP95 upper <= 0.075).
- P56c: v7 false rejects on truly-better <= 10%.
- Descriptive: v5 (no guard) false approvals and correct-approve on the same runs, to isolate the guard; v7 correct-approve (expected 0 when the guard fires: abstention by design).
Rule v7 is not changed whatever this shows; failures are reported.
## R13-2 ABLATION from saved W5 logs (results/r12_e1.jsonl; NO new runs; descriptive, post hoc, not a claim): false approvals and correct-approve for each single shape, for every leave-one-shape-out agreement of the four shapes (with and without the free-form veto, guard applied).
## R13-3 MVP (2) REPRODUCTION (experiments/mvp_drift.py; replaces the missing e1_table.py): base world (K=10, D=5), logs from the old policy (no hidden taste), 4,000 users before and 4,000 after; adverse covariate drift d = 1.0 along DRIFT_DIR applies to the after period only; the new policy runs in the after period. Before/after lift = after mean click rate (new policy, drifted) minus before mean click rate (old policy). Truth round-one lift = new minus old at drift 0 (300,000-user Monte Carlo). OPE = SNIPS and DR on the BEFORE logs with 95% row-bootstrap interval (B=300), compared with the truth round-one lift. 200 independent runs (seeds 0-199). Single drift value fixed here, no tuning.
- P57a: before/after has the wrong sign (negative while truth > 0) in >= 50% of runs.
- P57b: the SNIPS interval and the DR interval each cover the truth round-one lift in >= 90% of runs.
- Descriptive: the exact fractions, DR/SNIPS interval widths, truth value.
Disclosure (R13-3, before the 200-run sets): one plumbing check (seed 99999, outside run seeds) at d = 1.0 gave before/after +0.048 against truth +0.075, i.e. the sign is NOT wrong at d = 1.0, so P57a is expected to FAIL at d = 1.0. Added after that check and labelled as such: the same 200 runs at d = 2.0 and d = 3.0 (descriptive, P57a/P57b evaluated per d; the preregistered claim is d = 1.0). Drift is a CLI argument (4th).
Disclosure (R13-1): no smoke audit was run at TN 0.2 before the full run.
## R13-3 RESULT AND AMENDMENT (written 2026-10-27 after the DRIFT_DIR runs, before any logit-shift run). Preregistered d = 1.0 along DRIFT_DIR: P57a FAIL (before/after wrong sign 0/200; mean before/after +0.0486 vs truth +0.0751); P57b PASS (SNIPS and DR intervals cover truth in 187/200 = 0.935). d = 2.0 and 3.0 along DRIFT_DIR: wrong sign 0/200 each, and before/after RISES (+0.068, +0.106): that direction lowers the average logit across items but not every item's click rate; the sharper new policy moves to items whose logit rises, so it is not "adverse" for the new policy. The abstract's "adverse drift = lowers every item's click rate" therefore needs a different drift. Amendment (fixed now, before any run): uniform logit shift, after-period logit of every item lowered by delta (env P3_DRIFT_MODE=logit), delta = 0.5 and 1.0, same 200 seeds, same claims P57a (wrong sign >= 50%) and P57b (both intervals cover >= 90%) evaluated per delta. No other delta will be tried.

---
# ADDENDUM 19 (written 2026-10-28, BEFORE any R14 audit). Strict judge-panel read of the two latest abstracts (2/5 ADVANCE). Open items: (i) no sealed generator authored after the rule froze; (ii) no pre-stated success criterion in the abstract; (iii) the tipping margin has never been compared with a CI-only score; (iv) strong single-model baseline not reported beside the rule on a fresh family. REAL world.
Rule v7 is FROZEN (no change whatever R14 shows): per shape REJECT iff static OR forecast upper end <= 0, APPROVE iff static AND forecast lower ends > 0, else NEED; four shapes must all agree; coverage guard (<= 5% unsupported exposure); free-form count-curve veto; logs-only never APPROVE.
## R14-1 SEALED GENERATOR W6 (p3ope/r8_lib.py, shapes added today, never used in any design or test): sigm 3*(sigmoid(c-3.5) - sigmoid(-3.5)) (smooth onset); hump 1.2*c*exp(-c/3) (fatigue that RECOVERS after the third repeat: non-monotone); logsq 0.9*log(1+c)^2. Same per-item and taste-coupled per-user kappa as W3-W5. Authored by the rule's own authors, so it is sealed from the rule, not independent of the team. Cells from a TRUTH-only scan (60,000-user Monte Carlo, no audit run): sigm .3 (+0.0215) | 1.2 (-0.0059) 2.0 (-0.0166) 3.0 (-0.0225); hump .3 (+0.0301) | 3.0 (-0.0026) 5.0 (-0.0110) 8.0 (-0.0166); logsq .1 (+0.0296) | .8 (-0.0030) 1.2 (-0.0115) 2.0 (-0.0196). Truly worse (< -0.002) = 9 cells, 144 runs; near-boundary (|true| <= 0.01) = sigm 1.2, hump 3.0, logsq .8 = 3 cells, 48 runs; truly better = 3 cells, 48 runs. Taste x1, 10-round repeat-heavy slice, 3,000 users, 4,000 logged users, B = 30, 16 fresh seeds per cell (10000-10015), 192 audits.
- P58a: v7 false approvals on truly-worse (144 runs): CP95 upper <= 0.05 (2/144 or fewer).
- P58b: near-boundary truly-worse (48 runs): CP95 upper <= 0.10 (1/48 or fewer).
- P58c: false rejects on truly-better (48 runs) <= 10%.
- P58d: correct-approve on truly-better >= 0.25.
- Descriptive, same runs: false approvals / correct-approve of each single shape (lin, log, mem7, tail2), of the free-form model alone, of v5 (four-shape), v6 (+guard), v7; a one-step logs-only gate (approve iff SNIPS lower end on logs > 0).
- Success criterion stated in the abstract: if P58a fails, the abstract reports v7 as not reliable on fresh shapes and gives the measured rate.
## R14-2 TIPPING MARGIN vs CI-ONLY SCORE (ablation of the margin, on the R14-1 runs, linear-model quantities; margin = (kappa-hat - kappa*) / SD of bootstrap kappa-hat; CI-only score = forecast point / bootstrap SD of the linear forecast, P(worse) = Phi(-point/SD)). Target event: truly worse (< -0.002) among all 192 runs.
- P59a: Brier(Phi(margin)) < Brier(constant base rate).
- P59b: AUC(margin) >= AUC(CI-only score) - 0.02 (margin loses nothing against the plain interval).
- P59c (saved data, no new runs; results/r5_all.csv design runs where the 3-shape verdict is NEED): AUC of the margin for truly-worse vs truly-better >= 0.70 (does the margin say something where the CI verdict abstains?).
- Expectation written before running: P59a uncertain (the linear margin is misspecified on W6), P59b about a tie. A margin that does not beat the CI-only score is reported as an interpretation aid, not as extra evidence.
Disclosure: a smoke run (the six even-indexed cells, one audit each, seed 99999, outside the run seeds; 30 s total, verdicts not inspected) was executed for timing and plumbing before the 192 audits.

# ADDENDUM 20 (written 2026-10-29, BEFORE any W7 audit and before any larger-B re-run). Third judge-panel read of the v45 abstract (4 x ADVANCE at exactly 4.00-4.20, 1 x REJECT at 3.90). Open items: (i) every generator so far is logit-additive with same-item fatigue (J2: "truth comes from simulators sharing the logit-additive structure"); (ii) the 144 audits are 9 truly-worse worlds x 16 datasets, so 0/144 overstates the independent evidence; (iii) B = 30 bootstrap draws (J1); (iv) slice kappa-hat bias under hidden taste is stated but unexplained (J1). Rule v7, the guard limit (5%), B = 30 and all thresholds below are FROZEN; nothing in this addendum may change them.
## R15-1 STRUCTURALLY DIFFERENT GENERATOR W7 (p3ope/r15_lib.py): multiplicative probability-scale fatigue, category satiation (an omitted state), recovery, hidden per-(user,item) taste x fatigue interaction. 40 independent WORLDS (wid 0-39), each with its own category map, spillover weight, recovery rate, interaction sign and item multipliers; kappa per world log-uniform on [0.03, 0.6] (drawn from the world id). 3 fresh datasets per world (seeds 20000-20002), 120 audits, the frozen v7 audit (4,000 logged users, 3,000-user repeat-heavy slice, B = 30). Truth = 60,000-user Monte Carlo lift. Classes as in R14: truly worse < -0.002, truly better > +0.002, near-boundary |true| <= 0.01.
- Disclosure: the kappa range was chosen from a truth-only scan of worlds 0-7 on 20,000 users (no audit was run) so that true lifts cross zero; the rule was not touched.
- P60a: v7 false approvals on truly-worse audits <= 5% of them (rounded down), with the one-sided CP95 bound reported.
- P60b: near-boundary truly-worse false approvals <= 10%.
- P60c: false rejects on truly-better <= 10%.
- P60d: correct-approve on truly-better >= 0.25.
- P60e (world level, because audits within a world are not independent): at most 1 truly-worse world contains any false approval; the world-level CP95 bound is reported.
- Descriptive, same runs: single shapes, free-form alone, v5, v6, v7, and the one-step logs-only gate (SNIPS lower end > 0).
- Stated expectation before running: this is the hardest test so far (the true mechanism is outside every fitted model). If P60a or P60e fails, the abstract reports v7 as not reliable under structural misspecification and gives the measured rate.
## R15-2 BOOTSTRAP SIZE: the same datasets and seeds as 48 of the R14 audits (seeds 10000-10003 x all 12 cells), re-run with B = 200 instead of 30 (nothing else changes; truth taken from the R14 records). Interval method unchanged: two-sided percentile intervals, quantiles .025 and .975 of the bootstrap draws.
- P61a: the v7 verdict differs from the B = 30 verdict in <= 4/48 audits (<= 10%).
- P61b: no false approval at B = 200 on truly-worse audits.
- Descriptive: mean absolute change in the lower end of the linear 10-round forecast interval; ratio of interval widths B = 200 / B = 30.
## R15-3 (POST HOC, NOT PRE-REGISTERED; the run was made before this addendum was written, while diagnosing J1's question): why a randomised slice's pooled kappa-hat is biased low under hidden taste. 3,000-user repeat-heavy slice, linear fatigue kappa = 0.8, hidden taste x0/x1/x2/x3, 12 seeds each; pooled fit vs the same fit with the true hidden term supplied as an offset. Reported as a diagnosis, not as a pass/fail claim.
