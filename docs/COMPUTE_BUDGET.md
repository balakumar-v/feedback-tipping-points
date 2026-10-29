# Compute budget

Measured on the review machine: 1 CPU core, Python 3.12.3, numpy 2.4.4, scipy 1.17.1. No GPU is used anywhere.

| Item | Cost | Source |
|---|---|---|
| One full audit (simulate 4,000 logged users + 3,000-user slice, fit 4 shapes + free-form model, bootstrap, 60,000-user ground truth) | 8.5 s wall, about 196 MB peak memory | `python -m p3ope audit --kind cubic --kappa 0.2 --seed 1`, measured |
| One audit in the guard-stress runs (`P3_TN=0.2`) | 6.1 s mean (5.6-6.5 s) | `sec` field in `results/r13_e1_*.jsonl` |
| 192-audit sealed-generator grid (Round 14) | about 20 min on one core | 192 x about 6 s |
| 120-audit W7 grid, 40 random worlds (Round 15) | about 13 min on one core | `results/r15_e1.log` |
| One audit with B = 200 instead of 30 | about 40 s on one core (B = 100: 19.5 s; B = 30: 6.5 s), about 0.19 s per extra bootstrap draw | measured; 48-audit re-run in Round 15-2 |
| Round 7 four-shape re-test | about 60 min on two cores | README, original authors |
| Unit tests | about 80 s | `python -m unittest discover -s tests` |

## Parallelism

Every audit depends only on `(kind, kappa, seed)`, so a seed range can be split across cores or machines with no shared state. Experiment scripts take `SEED0 SEED1 OUT`; run two halves into `*_a.jsonl` and `*_b.jsonl` (as the README does). With 2 cores, the 192-audit grid takes about 10 min.

## What dominates

Fitting the five models on the slice and the user-level bootstrap dominate (cost is about 0.8 s plus 0.19 s per draw, so B = 30 is about 6.5 s and B = 500 would be about 100 s per audit); the 60,000-user ground-truth simulation is only for evaluation and is skipped with `--no-truth`. In a real rollout the audit would not need the ground-truth step.

## Drop order if the schedule slips

1. Demo UI
2. Marginal-sensitivity bounds
3. KuaiRand shuffled-round placebo

Never dropped: the MVP (IPW/SNIPS/DM/DR vs truth, before/after contrast, OBD control) and the randomised-slice audit.
