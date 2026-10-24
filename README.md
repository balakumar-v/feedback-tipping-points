# Measured Feedback Tipping Points

Pre-rollout audit for ranking policies (Perceptron Hackathon 2026, Problem 3: *"Did the Policy Actually Work, or Did It Just Look Like It?"*, off-policy evaluation).

The audit returns one of three verdicts: **APPROVE**, **REJECT**, or **NEED RANDOMIZED DATA** (with the size of the randomized slice required). It compares a measured user-fatigue coefficient (kappa-hat) against the *tipping point* kappa\*, the fatigue level at which the new policy's forecast lift becomes zero.

This repository holds the simulator, the audit code, every experiment, the raw run logs, and the pre-registered pass/fail record, including all failed targets.

![Pipeline diagram](figures/p3_diagram.png)

## Repository layout

```
.
├── docs/
│   ├── abstract.md            Round-1 abstract (v39; v37, v38 in docs/archive/)
│   ├── PREREGISTRATION.md     Thresholds fixed before each run (addenda 1-10)
│   ├── RESULTS.md             Pass/fail outcome for every claim, per round
│   └── FILE_MAP.md            Old flat filenames -> current paths
├── p3ope/                     Core library
│   ├── ope_pilot.py           Base world (K=10 items, D=5 features), IPW/SNIPS/DM/DR
│   ├── exp13_lib.py           Multi-mechanism feedback simulator, fitting, bootstrap, forecast, tipping point, verdict
│   ├── r2_lib.py              Fatigue shapes, slice kappa estimators
│   ├── r4_lib.py              Second held-out generator (probit link, heterogeneous fatigue)
│   ├── r5_lib.py              Tail-targeted slice design, tipping-margin audit
│   └── r8_lib.py              Third held-out generator W3 (step/expo/late fatigue, taste-coupled kappa)
├── experiments/               One script per experiment (rN_eM = round N, experiment M)
├── analysis/                  Scripts that turn results/ into the pass/fail tables
├── figures/                   Final figures + scripts that build them
├── results/                   Raw run logs (.jsonl / .log / .csv)
│   └── standin_superseded/    Earlier stand-in-world runs, kept for the record only
└── requirements.txt
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Tested with Python 3.12 and 3.13. Run everything from the repository root.

## Reproducing the runs

Each run appends to its output file and resumes if restarted. One audit takes about 3-6 s on one CPU core.

```bash
python -m experiments.r3_e3 300 316 results/r3_e3.jsonl
python -m experiments.r4_e2 500 530 results/r4_e2.jsonl
python -m experiments.r4_e1 400 424 results/r4_e1.jsonl
python -m experiments.r5_e1 design results/r5_design.jsonl
python -m experiments.r5_e1 curve  results/r5_curve.jsonl
python -m experiments.r3_e1 200 214 results/r3_e1.jsonl
python -m experiments.r6_e1 results/r6.jsonl
# Round 8-9 (judge-panel fixes: logs-only under hidden taste; held-out generator W3; tail slice)
python -m experiments.r8_e1 3000 3016 results/r8_e1.jsonl
python -m experiments.r8_e2 4000 4016 results/r8_e2.jsonl
P3_SLICE=tail P3_CELLS=step,late python -m experiments.r8_e2 5000 5016 results/r9_e1.jsonl
# Round 7: final four-shape rule (about 60 min on two cores; each pair of commands can run in parallel)
python -m experiments.r7_e1 1000 1016 results/r7_e1_a.jsonl   # and: 1016 1032 results/r7_e1_b.jsonl
python -m experiments.r7_e2 1100 1110 results/r7_e2_a.jsonl   # and: 1110 1120 results/r7_e2_b.jsonl
python -m experiments.r7_e3 1200 1208 results/r7_e3_a.jsonl   # and: 1208 1216 results/r7_e3_b.jsonl
python -m experiments.r7_e4 1300 1308 results/r7_e4_a.jsonl   # and: 1308 1316 results/r7_e4_b.jsonl
```

Arguments are `SEED0 SEED1 OUT` (see each script's docstring for the exact usage).

## Reproducing the analysis

```bash
python -m analysis.an_r3_e3
python -m analysis.an_r4
python -m analysis.an_r5      # also regenerates figures/reliability_tipping_margin.png
python -m analysis.an_r6
python -m analysis.an_r3_e1
python -m analysis.an_percell
python -m analysis.an_r7
python -m experiments.r10_e1 6000 6032 results/r10_e1.jsonl   # n* with pilot band
python -m analysis.an_r8
python -m experiments.r11_e1 7000 7016 results/r11_e1.jsonl   # rule v6, fourth generator
python -m analysis.an_r10
python -m experiments.r12_e1 8000 8016 results/r12_e1.jsonl W5   # rule v7, free-form veto
python -m experiments.r12_e1 8000 8008 results/r12_e1_w4.jsonl W4
python -m analysis.an_r11
python -m analysis.an_r12
```

Figures: `python figures/make_diagram.py` renders `figures/diagram.html` from the results.

## Results

[`docs/RESULTS.md`](docs/RESULTS.md) lists each pre-registered claim with its pass/fail outcome, and [`docs/PREREGISTRATION.md`](docs/PREREGISTRATION.md) holds the thresholds as written before the runs. Failed targets are reported in full.

## Not done

Fatigue that starts only at the third or later repeat is not covered (R8-2, R9-1 failed their targets). n* band covers the oracle in 85% of pilots (target 90%), see Round 10. Rule v6 (repeat-heavy 10-round slice + coverage guard) still gives 18/144 false approvals on delayed-onset fatigue (target 5%), see Round 11; the v7 free-form veto brings that to 0/144 on a fresh generator (Round 12). 
KuaiRand (stretch goal), sequential slice sizing, sensitivity bounds. Closed-loop slice sizing was dropped because it fails in the real-world setting.

## Notes

- `docs/RESULTS.md` and `docs/PREREGISTRATION.md` are the historical record and still use the original flat script names; see [`docs/FILE_MAP.md`](docs/FILE_MAP.md).
- `e5_full.py` / `e5_diag.py` (the full Open Bandit Dataset runs in the P17-P19 section) were not in the supplied archive, so they are not included here.
- The abstract's repository URL is filled in (this repository).
- Rounds 1-6 slice and R2-3 logs-only results used a three-shape rule (lin, log, mem7); the abstract's final rule has four shapes (adds tail2). Round 7 re-tests the headline claims under the final rule; see docs/RESULTS.md.
