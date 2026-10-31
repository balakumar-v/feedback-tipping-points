# Reproducing the experiments

Every number in [`RESULTS.md`](RESULTS.md) comes from a script in `experiments/` (which writes a log to `results/round-NN/`) and a script in `analysis/` (which turns that log into the pass/fail tables). Run everything from the repository root.

Script names follow `rN_eM.py` = round N, experiment M. Round 1 scripts are named `e1`-`e5` and `exp*`. Logs are grouped by round; the mapping from the original flat names is in [`FILE_MAP.md`](FILE_MAP.md).

## 1. Running experiments

Each run appends to its output file and resumes if restarted. One audit takes about 3-12 s on one CPU core. Running a script with missing arguments prints its usage line.

```bash
python -m experiments.r3_e3 300 316 results/round-03/r3_e3.jsonl
python -m experiments.r4_e2 500 530 results/round-04/r4_e2.jsonl
python -m experiments.r4_e1 400 424 results/round-04/r4_e1.jsonl
python -m experiments.r5_e1 design results/round-05/r5_design.jsonl
python -m experiments.r5_e1 curve  results/round-05/r5_curve.jsonl
python -m experiments.r3_e1 200 214 results/round-03/r3_e1.jsonl
python -m experiments.r6_e1 results/round-06/r6.jsonl
# Round 8-9 (judge-panel fixes: logs-only under hidden taste; held-out generator W3; tail slice)
python -m experiments.r8_e1 3000 3016 results/round-08/r8_e1.jsonl
python -m experiments.r8_e2 4000 4016 results/round-08/r8_e2.jsonl
P3_SLICE=tail P3_CELLS=step,late python -m experiments.r8_e2 5000 5016 results/round-09/r9_e1.jsonl
# Round 7: final four-shape rule (about 60 min on two cores; each pair of commands can run in parallel)
python -m experiments.r7_e1 1000 1016 results/round-07/r7_e1_a.jsonl   # and: 1016 1032 results/round-07/r7_e1_b.jsonl
python -m experiments.r7_e2 1100 1110 results/round-07/r7_e2_a.jsonl   # and: 1110 1120 results/round-07/r7_e2_b.jsonl
python -m experiments.r7_e3 1200 1208 results/round-07/r7_e3_a.jsonl   # and: 1208 1216 results/round-07/r7_e3_b.jsonl
python -m experiments.r7_e4 1300 1308 results/round-07/r7_e4_a.jsonl   # and: 1308 1316 results/round-07/r7_e4_b.jsonl
```

Arguments are `SEED0 SEED1 OUT` (see each script's docstring for the exact usage).

## 2. Running the analysis

```bash
python -m analysis.an_r3_e3
python -m analysis.an_r4
python -m analysis.an_r5      # also regenerates figures/reliability_tipping_margin.png
python -m analysis.an_r6
python -m analysis.an_r3_e1
python -m analysis.an_percell
python -m analysis.an_r7
python -m experiments.r10_e1 6000 6032 results/round-10/r10_e1.jsonl   # n* with pilot band
python -m analysis.an_r8
python -m experiments.r11_e1 7000 7016 results/round-11/r11_e1.jsonl   # rule v6, fourth generator
python -m analysis.an_r10
python -m experiments.r12_e1 8000 8016 results/round-12/r12_e1.jsonl W5   # rule v7, free-form veto
python -m experiments.r12_e1 8000 8008 results/round-12/r12_e1_w4.jsonl W4
python -m analysis.an_r11
python -m analysis.an_r12
# Round 13 (strict-panel fixes): guard stress, drift MVP, ablation from saved logs
P3_TN=0.2 python -m experiments.r13_e1 9000 9004 results/round-13/r13_e1_a.jsonl   # and: 9004 9008 results/round-13/r13_e1_b.jsonl (about 5 min each)
python -m experiments.mvp_drift 0 200 results/round-13/mvp_drift_dir_d1.0.jsonl 1.0          # covariate drift along DRIFT_DIR (not adverse for the new policy)
P3_DRIFT_MODE=logit python -m experiments.mvp_drift 0 200 results/round-13/mvp_drift_logit_d1.0.jsonl 1.0   # uniform logit shift: before/after wrong sign 200/200
python -m analysis.an_r13   # also prints the ablation and the logs-only false-reject check
python -m analysis.an_ablation   # pooled shape ablation + decision-value metric (post hoc, from saved logs)
# Round 15 (third panel): structurally different generator W7, larger bootstrap, slice-bias mechanism
python -m experiments.r15_e1 20000 20003 results/round-15/r15_e1.jsonl   # 40 worlds x 3 datasets, about 13 min
python -m experiments.r15_e2 200 results/round-15/r15_e2.jsonl            # 48 R14 datasets re-run at B = 200, about 50 min
python -m experiments.r15_e3 results/round-15/r15_e3.jsonl                # hidden-taste bias of slice kappa-hat, about 15 s
python -m analysis.an_r15
```


## 3. Optional environment variables

There are no secrets, API keys or databases. The only settings are optional environment variables read by the simulator (defaults reproduce every logged run; do not change them when reproducing results):

| Variable | Default | Meaning |
|---|---|---|
| `P3_ALPHA` | `0.8` | How closely the old (logging) policy follows true click logits |
| `P3_TAUOLD` | `1.0` | Old policy softmax temperature |
| `P3_TN` | `0.5` | New policy softmax temperature |
| `P3_SLICE` | `slice` | `experiments/r8_e2` only: `slice` or `tail` slice design |
| `P3_CELLS` | `all` | `experiments/r8_e2` only: comma list such as `step,late` |

## 4. Gotcha

Importing an experiment module sets module-level constants (for example `r2_lib.NF = 3000`) to match the logged runs. Do not mix experiment modules with different settings in one Python process, and run `tests.test_core` and `tests.test_reproduce` as separate commands.
