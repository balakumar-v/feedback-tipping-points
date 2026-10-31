# Measured Feedback Tipping Points

**A pre-rollout audit that tells you whether a new ranking policy will really beat the old one, or only looks better in old logs.**

Built for the Perceptron Hackathon 2026, Problem 3: *"Did the Policy Actually Work, or Did It Just Look Like It?"* (off-policy evaluation).

![Pipeline diagram](figures/measured-feedback-architecture.png)

## The problem

A new ranking policy can score higher on old logs and still be worse after launch, because users tire of seeing the same item again and again (**fatigue**). A standard one-step estimate cannot see that, since it only scores the first round.

## The idea

1. Measure the fatigue coefficient (**κ̂**, kappa-hat) from a small randomised slice of traffic.
2. Find the **tipping point κ\***: the fatigue level at which the new policy's forecast lift drops to zero.
3. Compare κ̂ with κ\* and return one of three verdicts:

| Verdict | Meaning |
|---|---|
| **APPROVE** | Every fatigue model agrees the new policy wins, and the data covers the repeat counts it will produce. |
| **REJECT** | The models agree the new policy is not better. |
| **NEED RANDOMIZED DATA** | The evidence is not enough either way. The audit abstains and says how much slice data would settle it. |

> Everything runs on our own simulators. No production or personal data is used, and no external service or credential is required.

## Quick start

Needs Python 3.12 (also tested on 3.13). Run every command from the repository root.

```bash
git clone https://github.com/balakumar-v/feedback-tipping-points.git
cd feedback-tipping-points
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m p3ope demo        # two live audits, a harmful policy and a good one (~30 s)
python -m p3ope ope         # one-step IPW / SNIPS / DM / DR baseline vs truth (instant)
python -m p3ope summary     # headline numbers from the 288 logged audits (instant)
python -m p3ope report      # builds docs/dashboard.html, open it in any browser
```

### What the demo shows

For the `cubic` fatigue shape at κ = 0.5, the one-step estimate says the new policy lifts clicks by **+0.084**. The true 10-round lift is **−0.019**. The audit does not approve it: the final rule returns NEED RANDOMIZED DATA because the four fatigue models disagree, and the free-form model on its own already rejects.

## Command reference

| Command | What it does |
|---|---|
| `python -m p3ope demo` | Audits two simulated policies and prints each verdict next to the simulator's ground truth. |
| `python -m p3ope audit --kind cubic --kappa 0.2 --seed 1` | Audits one scenario (~12 s). Add `--json` for machine-readable output, `--no-truth` to skip the ground-truth step, `--boot 200` for a steadier bootstrap (~40 s; the default 30 reproduces the logged runs). |
| `python -m p3ope ope --beta 0.5 --gamma 0.8` | One-step IPW / SNIPS / DM / DR baseline next to the exact truth. With `--beta 0 --gamma 0` it is accurate; with hidden taste it is biased. |
| `python -m p3ope kinds` | Lists the 25 fatigue shapes the simulator can generate. |
| `python -m p3ope summary` | Prints false-approval and correct-approve counts (with 95% bounds) from `results/`. |
| `python -m p3ope report` | Writes the self-contained results dashboard `docs/dashboard.html` (no JavaScript, no network). |

An audit with the same `--kind`, `--kappa` and `--seed` as a logged run reproduces that record exactly (checked by `tests/test_reproduce.py`).

## Headline results

All numbers come from simulators and are computed from the raw logs by `python -m p3ope summary`. The final rule is **v7**; **v6** is the earlier rule without the free-form veto.

| Generator | Rule | False approvals | Correct approvals |
|---|---|---|---|
| W5, fresh held-out (pre-registered, 192 audits) | v6 | 6 / 144 | 29 / 48 |
| W5, fresh held-out (pre-registered, 192 audits) | **v7** | **0 / 144** (95% upper bound 2.1%) | 26 / 48 |
| W4, earlier generator (retro, descriptive, 96 audits) | v7 | 1 / 72 | 8 / 24 |

Failed targets are reported in full in [`docs/RESULTS.md`](docs/RESULTS.md); thresholds as written before each run are in [`docs/PREREGISTRATION.md`](docs/PREREGISTRATION.md).

## Repository layout

```
.
├── p3ope/                 Core library and CLI (python -m p3ope ...)
│   ├── audit.py             run_audit(kind, kappa, seed): the final rule in one call
│   ├── cli.py, __main__.py  Command-line entry point
│   ├── summary.py, report.py  Headline statistics and the HTML dashboard
│   ├── ope_pilot.py         Base world (10 items, 5 features) and IPW/SNIPS/DM/DR
│   ├── exp13_lib.py         Feedback simulator, fitting, bootstrap, forecast, tipping point, verdict
│   ├── r2_lib.py, r4_lib.py, r5_lib.py, r8_lib.py, r12_lib.py, r15_lib.py
│   │                        Fatigue shapes, held-out generators (W2-W7), slice design, free-form model
│   └── khat.py, sharp.py, slice_util.py   Small helpers
├── experiments/           One script per experiment (rN_eM.py = round N, experiment M)
├── analysis/              Scripts that turn logs into the pass/fail tables (an_rN.py)
├── results/               Raw run logs, one folder per round: round-01/ ... round-15/
├── tests/                 unittest suite (fast checks + exact-reproduction checks)
├── figures/               Final figures
├── docs/
│   ├── abstract.md          Hackathon abstract
│   ├── PREREGISTRATION.md   Thresholds fixed before each run (addenda 1-20)
│   ├── RESULTS.md           Pass/fail outcome for every claim, per round
│   ├── REPRODUCING.md       Commands to re-run every experiment and analysis
│   ├── COMPUTE_BUDGET.md    Measured time and memory per audit
│   ├── FILE_MAP.md          Old file names -> current paths
│   ├── DEVELOPMENT_NOTES.md Review feedback and how it was addressed
│   └── dashboard.html       Generated results dashboard
├── LICENSE                  MIT license
├── requirements.txt         Minimal dependencies
└── requirements-tested.txt  Exact versions used to verify this release
```

## Testing

```bash
python -m unittest tests.test_core          # imports, verdict logic, log integrity, headline numbers
python -m unittest tests.test_reproduce     # fresh audits must match the logged records exactly
```

Run these as two separate commands: importing experiment modules changes module-level settings, so mixing them in one process can break the exact-reproduction checks. `tests.test_core` prints some tables while it imports the `analysis/` scripts; that is expected.

## Reproducing the experiments

Every audit depends only on `(kind, kappa, seed)`, so seed ranges can be split across cores. One audit takes about 3-12 s on one CPU core. The only settings are a few optional environment variables, and their defaults reproduce every logged run. Full commands, round by round, are in [`docs/REPRODUCING.md`](docs/REPRODUCING.md). Time and memory per audit are in [`docs/COMPUTE_BUDGET.md`](docs/COMPUTE_BUDGET.md).

## Known limitations

- Fatigue that starts only at the third or later repeat is not covered (R8-2 and R9-1 missed their targets).
- The n\* slice-size band covers the oracle in 85% of pilots (target 90%), see Round 10.
- With a much sharper new policy, the coverage guard fires in 96/96 audits, so the audit abstains instead of approving (0/24 correct approvals, Round 13).
- The drift check at half strength (logit shift 0.5) misses its 50% target (96/200 wrong sign).
- On fresh generators the free-form model alone matches the full rule (0/144 false approvals), so four-shape agreement is partly redundant (post hoc ablation: `analysis/an_ablation.py`).
- `python -m p3ope audit` runs the verdict rule only; it does not print the n\* slice size, which lives in `experiments/r3_e1.py` and `experiments/r10_e1.py`.
- The Open Bandit Dataset control (`experiments/e5_*.py`) needs external data and the OBP source; only its logged outputs (`results/round-01/e5_*`) are available from this repository.
- Not attempted: KuaiRand dynamics check, head-to-head with non-stationary OPE methods, marginal-sensitivity-bound comparison.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: p3ope` or `result log not found: results/...` | Run from the repository root; the code reads `results/` and `figures/` with relative paths. |
| `unknown fatigue shape` | Run `python -m p3ope kinds` for the valid names. |
| An experiment prints only a usage line | It needs positional arguments, see [`docs/REPRODUCING.md`](docs/REPRODUCING.md). |
| `analysis.an_r5` changes `figures/reliability_tipping_margin.png` | Expected: it regenerates that figure. |
| Numbers differ slightly after upgrading numpy/scipy | Logged runs used the versions in `requirements-tested.txt`; verdict counts should match, last decimals may not. |

## Authors

Balakumar V, Kishore Kumar J, K Asvitha (Perceptron Hackathon 2026, Problem 3).

## License

Released under the [MIT License](LICENSE).
