# File map

Original flat filenames (as cited in RESULTS.md / PREREGISTRATION.md) -> current location.
Where the records say `python3 r3_e3.py ...`, run `python -m experiments.r3_e3 ...` from the repo root; `out/` is now `results/`.

| Original | Now |
|---|---|
| `exp13_lib.py` | `p3ope/exp13_lib.py` |
| `ope_pilot.py` | `p3ope/ope_pilot.py` |
| `r2_lib.py` | `p3ope/r2_lib.py` |
| `r4_lib.py` | `p3ope/r4_lib.py` |
| `r5_lib.py` | `p3ope/r5_lib.py` |
| `r2_e1.py` | `experiments/r2_e1.py` |
| `r2_e3.py` | `experiments/r2_e3.py` |
| `r2_e4.py` | `experiments/r2_e4.py` |
| `r2_e5.py` | `experiments/r2_e5.py` |
| `r3_e1.py` | `experiments/r3_e1.py` |
| `r3_e3.py` | `experiments/r3_e3.py` |
| `r4_e1.py` | `experiments/r4_e1.py` |
| `r4_e2.py` | `experiments/r4_e2.py` |
| `r5_e1.py` | `experiments/r5_e1.py` |
| `r6_e1.py` | `experiments/r6_e1.py` |
| `an_percell.py` | `analysis/an_percell.py` |
| `an_r2_e1.py` | `analysis/an_r2_e1.py` |
| `an_r2_e3.py` | `analysis/an_r2_e3.py` |
| `an_r2_e4.py` | `analysis/an_r2_e4.py` |
| `an_r2_e5.py` | `analysis/an_r2_e5.py` |
| `an_r3_e1.py` | `analysis/an_r3_e1.py` |
| `an_r3_e3.py` | `analysis/an_r3_e3.py` |
| `an_r4.py` | `analysis/an_r4.py` |
| `an_r4_margin.py` | `analysis/an_r4_margin.py` |
| `an_r5.py` | `analysis/an_r5.py` |
| `an_r6.py` | `analysis/an_r6.py` |
| `cost_slice.py` | `analysis/cost_slice.py` |
| `scan2.py` | `analysis/scan2.py` |
| `scan_real.py` | `analysis/scan_real.py` |
| `scan_truth.py` | `analysis/scan_truth.py` |
| `diagram_template.html` | `figures/diagram_template.html` |
| `make_diagram.py` | `figures/make_diagram.py` |
| `abstract_v37.md` | `docs/abstract.md` |
| `perceptron_p3_diagram_v10.png` | `figures/measured-feedback-architecture.png` |
| `perceptron_p3_diagram_v9.png` | `figures/archive/p3_diagram_v9.png` |
| `reliability_tipping_margin.png` | `figures/reliability_tipping_margin.png` |
| `out/` | `results/` |
| `out/standin/` | `results/standin_superseded/` |
| `README.md (original)` | `README.md (rewritten)` |

| (new, Round 7) | `experiments/r7_e1.py` … `r7_e4.py`, `analysis/an_r7.py`, `results/r7_e*_{a,b}.jsonl`, `docs/archive/abstract_v37.md`, `figures/archive/p3_diagram_v10.png` |

| (new, Round 8-12 files, previously unlisted) | `p3ope/r8_lib.py`, `p3ope/r12_lib.py`, `experiments/r7_e*.py`, `experiments/r8_e*.py`, `experiments/r10_e1.py`, `experiments/r11_e1.py`, `experiments/r12_e1.py`, `analysis/an_r7.py`, `analysis/an_r8.py`, `analysis/an_r10.py`, `analysis/an_r11.py`, `analysis/an_r12.py` |
| (new, v40 improvement) | `p3ope/audit.py`, `p3ope/summary.py`, `p3ope/report.py`, `p3ope/cli.py`, `p3ope/__main__.py`, `tests/`, `docs/dashboard.html`, `docs/improvement/`, `requirements-tested.txt` |

| (new, R13 strict-panel round) | `experiments/r13_e1.py`, `experiments/mvp_drift.py`, `analysis/an_r13.py`, `results/r13_e1_{a,b}.jsonl`, `results/mvp_drift_*.jsonl`, `results/r13_summary.txt`, Addendum 18 in `docs/PREREGISTRATION.md`, R13 in `docs/RESULTS.md` |

| (new, R14 sealed-generator round) | `experiments/r14_e1.py`, `analysis/an_r14.py`, `results/r14_e1_{a,b}.jsonl`, `results/r14_summary.txt`, W6 shapes in `p3ope/r8_lib.py`, Addendum 19 in `docs/PREREGISTRATION.md`, R14 in `docs/RESULTS.md` |

| (new, v44 panel-2 fixes) | `analysis/an_ablation.py`, `docs/COMPUTE_BUDGET.md`, `docs/archive/abstract_v43_pre_panel2.md`, `TestAblation` in `tests/test_core.py` |

| (new, v46 panel-3 fixes) | `p3ope/r15_lib.py`, `experiments/r15_e1.py`, `experiments/r15_e2.py`, `experiments/r15_e3.py`, `analysis/an_r15.py`, `results/r15_e1.jsonl`, `results/r15_e2.jsonl`, `results/r15_e3.jsonl`, Addendum 20 in `docs/PREREGISTRATION.md`, R15 in `docs/RESULTS.md`, `--boot` option in `p3ope audit`, `docs/archive/abstract_v45_pre_panel3.md`, `Round15` in `tests/test_core.py` |

| (new, round-1 scripts restored from work.zip) | `experiments/{e1_table,e2_audit,exp13_e3,exp14_e4,e4_loop,e4_loop2,e5_obd,e5_full,e5_diag}.py`, pilots `experiments/exp{1b,2,2b,3,3b,4,5,6_gen,7,8,9,10,11,12}.py`, checks `experiments/{bench,t13,xcheck_gen,xcheck_obp,xcheck_obp_src}.py`; `analysis/{an_e2,an_e3,an_e4,an_loop,an_loop2,an_w2,exp6_an}.py`; helpers `p3ope/{khat,sharp,slice_util}.py`; `tests/test_msm.py` (run `python -m tests.test_msm`); logs `results/{e1,e2,e3_*,e4_*,e5_*,w2_AB,exp*,an_e3}.*`; old abstract `docs/archive/abstract_round1_final.md` |

Round-1 mapping: E1 = `e1_table`/`exp1b`; E2 = `e2_audit`; E3 = `exp13_e3` (groups A-G) + `an_e3`/`an_w2` (W2 world); E4 = `exp14_e4` + `an_e4`, closed loop `e4_loop` (P12) / `e4_loop2` (P15) + `an_loop`/`an_loop2`; E5 = `e5_obd`/`e5_full`/`e5_diag` (P17-P19). Run as `python -m experiments.<name> ...` from the repo root; outputs go to `results/` (was `out/`). `exp1b`-`exp12` are the early pilots (`out/exp*.txt` logs). Not rerun: E5 (needs OBD data + OBP). Checked: `python -m analysis.an_e3` output is identical to `results/an_e3.txt`; `exp13_e3 A 0 1` reproduces the logged records exactly.
