# Development notes

History of how the project responded to three rounds of dry-run review. The main README carries only the current state.

## Panel-review fixes (v44)

A dry-run judge panel on the abstract flagged: length, inconsistent counts, undefined terms, no compute budget or drop order, no ablation isolating four-shape agreement, no decision-loss metric. Done here: abstract cut and terms defined; `docs/COMPUTE_BUDGET.md`; `analysis/an_ablation.py` (four-shape agreement vs single shapes vs free-form alone, plus value per audit with false approvals weighted by lambda = 1, 5, 10). Finding: on the two generators seen during rule building, four-shape agreement gave 13/216 false approvals (tail-weighted shape alone also 13/216) while the free-form model alone and the final rule gave 1/216, so safety comes mainly from the free-form model and the guard. These are post hoc and descriptive; `docs/PREREGISTRATION.md` and `docs/RESULTS.md` were not edited.

Not done (needs data or time we do not have here): KuaiRand dynamics check, head-to-head with Chandak-style non-stationary OPE, comparison with an MSM-bound tipping value, held-out-pilot check of the n* winner's-curse bias, and one prior project per team member (only the team can supply that).

## Panel-review fixes (v46)

Third dry-run panel (4 ADVANCE, 1 REJECT at 3.90). Done: abstract cut to about 900 words with n*, the candidate policy and the interval method defined; slice-bias mechanism explained and verified (`experiments/r15_e3.py`); OBD miss diagnosed; timeline reconciled; `--boot` option and a B = 200 re-check (`experiments/r15_e2.py`); structurally different generator W7 with 40 independent worlds (`p3ope/r15_lib.py`, `experiments/r15_e1.py`), all pre-registered criteria met (Addendum 20, RESULTS Round 15). Not done: diagram/text alignment (skipped by request) and one real prior project per team member.

## Notes

- `docs/RESULTS.md` and `docs/PREREGISTRATION.md` are the historical record and still use the original flat script names; see [`docs/FILE_MAP.md`](docs/FILE_MAP.md). They were not edited.
- Round-1 scripts (E1-E5, P1-P19) are now included under `experiments/` and `analysis/` with their logs in `results/`; see `docs/FILE_MAP.md`. The OBD runs (`e5_obd.py`, `e5_full.py`, `e5_diag.py`) additionally need the OBP source (`ZR_OBP=/path/to/zr-obp`, v0.5.5 with torch/tqdm stubbed) and the full 'men' CSVs (`OBD_FULL=/path`, or the path argument for `e5_full.py`/`e5_obd.py`); their logged outputs are `results/round-01/e5_*.json|log`.
- The abstract's repository URL is filled in (this repository).
- Rounds 1-6 slice and R2-3 logs-only results used a three-shape rule (lin, log, mem7); the abstract's final rule has four shapes (adds tail2). Round 7 re-tests the headline claims under the final rule; see docs/RESULTS.md.
- Importing an experiment module sets a few module-level constants (for example `r2_lib.NF = 3000`) to match the logged runs. Do not mix experiment modules with different settings in one Python process.
