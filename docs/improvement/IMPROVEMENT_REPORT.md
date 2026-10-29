# Improvement Report: p3-tipping-ope v39 -> v40

Everything in this report was checked against the actual code. Commands and results in section 7 were really executed; section 8 lists what was **not** verified.

---

## 1. Summary

| | |
|---|---|
| Project | *Measured Feedback Tipping Points*, a pre-rollout audit for ranking policies (off-policy evaluation, Perceptron Hackathon 2026, Problem 3) |
| Nature of the project | A **Python research codebase** (simulators, statistical audit rules, 19 experiments, 20 analysis scripts, raw run logs, pre-registered pass/fail record). It is **not a web app**: it has no frontend, backend, database, login or API. |
| Main gap found | Nothing a person could *run and show*. The abstract promises "one command runs IPW, SNIPS, DR" and a "demo UI", but neither existed. The final audit rule was only reachable by editing experiment scripts. |
| Main bugs found | 2 scripts crashed on import; 1 of them could no longer reproduce its own logged results. |
| What I did | Added a one-command demo, an audit API, a baseline command, a results dashboard, 23 automated tests, a rewritten README and this documentation. Fixed the 2 broken scripts. **Did not touch any science code, result log or pre-registration record.** |
| Files changed / added | 5 existing files modified, 11 files added (list in section 5). |
| Test status | 23/23 automated tests pass; 20/20 analysis scripts run; fresh audits reproduce the logged records to 9 decimal places. |

### Why the master prompt was adapted

The master prompt describes a web app (landing page, responsive layout, forms, database, authentication, browser console). This project has none of those, and inventing them would break two of the prompt's own rules ("do not replace the application with a generic template", "do not fake backend integrations"). I applied the prompt's *intent* instead:

| Prompt asks for | What it became here |
|---|---|
| Attractive landing page that explains problem and solution | `docs/dashboard.html` (self-contained results page) + rewritten README opening |
| Loading / empty / error / success states | CLI progress messages, clear one-line errors, no tracebacks for bad input |
| Responsive, accessible, dark-mode UI | Dashboard: responsive grid, scrollable tables with captions, text labels (not colour alone), keyboard-focusable regions, light and dark themes |
| Backend, database, API validation | `run_audit` validates input and raises clear errors; no database exists or is needed |
| `.env.example` | **Not created on purpose**: the code reads no `.env` file and has no secrets. The 5 optional environment variables are documented in the README instead. A `.env.example` would suggest a mechanism that does not exist. |
| Screenshots | Not generated (see section 8) |

---

## 2. Analysis of the original project (Phase 1)

**Purpose.** A policy can look better in old logs but be worse after launch because users tire of repeated items. The audit estimates a fatigue coefficient (kappa-hat) from a randomised slice, finds the tipping point kappa\* where the forecast lift reaches zero, and returns APPROVE, REJECT or NEED RANDOMIZED DATA. In the simulator, a one-step estimate reports a gain of +0.084 where the truth is -0.019.

**Stack.** Python 3.12, numpy, scipy, scikit-learn, pandas, matplotlib. Kept unchanged; no dependency added.

**Structure (1,631 lines of code, 5 MB).**

| Folder | Content |
|---|---|
| `p3ope/` | simulators, fatigue shapes, bootstrap, forecast, tipping point, verdict |
| `experiments/` | 19 scripts, one per experiment, resumable, append to `results/*.jsonl` |
| `analysis/` | 20 scripts that turn logs into pass/fail tables |
| `results/` | 70+ raw logs, including failed targets and superseded stand-in runs |
| `docs/` | abstract (v37-v39), pre-registration (36 KB), results record (29 KB) |

**Feature status found in the original.**

| Feature | Status in v39 |
|---|---|
| Simulator + fatigue shapes + 5 held-out generators | Fully implemented |
| Fatigue estimation, bootstrap, forecast, tipping point | Fully implemented |
| Final audit rule v7 (4 shapes + coverage guard + free-form veto) | Implemented, but only inside `experiments/r12_e1.py` |
| 20 analysis scripts | All run (20/20, baseline measured) |
| Raw logs and pre-registration | Complete; failures documented honestly |
| "One command runs IPW, SNIPS, DR" (abstract, MVP item 1) | **Missing**: functions existed, no command |
| "Demo UI" (abstract, team plan) | **Missing** |
| n\* slice size in the verdict | Exists in `r3_e1` / `r10_e1`, not part of the v7 entry point |
| Open Bandit Dataset runs (`e5_full.py`, `e5_diag.py`) | Added later from the round-1 work archive; need OBP source + full OBD files (not bundled) |
| KuaiRand real-data stretch goal | Not done (documented by the authors) |
| Tests | **None** |
| `python -m experiments.r2_e1` / `r2_e4` | **Broken** (see below) |

**Defects found.**

1. `experiments/r2_e1.py` and `r2_e4.py` ran their whole experiment at import time with no `if __name__ == "__main__"` guard. Importing them raised `IndexError` (and would silently create output files if arguments were present).
2. `experiments/r2_e1.py` additionally **could not be re-run**: `R.fit()` was later changed to return a sparse matrix for speed, but `newton_ri()` still expects a dense one, so the script crashed with a `ValueError`. The logged results in `results/r2_e1.jsonl` could therefore not be reproduced from the shipped code.
3. README listed `r8_lib` but omitted `r12_lib`; `FILE_MAP.md` did not list the Round 7-12 files.
4. Dependencies unpinned with no record of tested versions.
5. Several modules set module-level constants on import (for example `R.NF = 3000`). This is intentional (it matches the logged runs) but was undocumented and is a trap when mixing modules.
6. No security issues: no secrets, no network code, no `eval`/`exec`/`pickle`/`subprocess`.

---

## 3. Design principle: protect the scientific record

This project's value is its **pre-registered, honestly reported results**. Therefore:

* No file in `p3ope/` that existed before, nothing in `results/`, `analysis/`, `docs/PREREGISTRATION.md`, `docs/RESULTS.md` or `docs/abstract.md` was modified. (Proven by `diff -rq`, section 7.)
* New code only *wraps* the frozen rule; it does not re-implement or tune it. A fresh run reproduces the logged records, which is the evidence that the wrapper is faithful.
* The two repaired scripts produce numerically identical output to what was logged.

---

## 4. What was improved

### 4.1 One-command demo and audit entry point (new)

`python -m p3ope demo` runs the final audit on two simulated policies, one harmful and one good, and prints per-model verdicts, the three rule stages (v5, v6, v7), what a one-step estimate would have said, and the simulator's ground truth.

Example (actual output, harmful policy `cubic`, kappa 0.5):

```
 A one-step (static) estimate would say : lift +0.0840
 Simulator ground truth (10 rounds)     : lift -0.0188  (worse than the old policy)
 VERDICT: NEED RANDOMIZED DATA   [abstained]
```

`p3ope/audit.py` exposes the same thing as a Python API (`run_audit(kind, kappa, seed)` returning a typed `AuditReport` with per-shape results, guard status, one-step estimate, truth and a correct / abstained / WRONG outcome), with input validation.

### 4.2 One-step baseline command (new, completes abstract MVP item 1)

`python -m p3ope ope [--beta B --gamma G]` runs IPW, SNIPS, DM and DR beside the exact Monte-Carlo truth. Measured: with no hidden taste SNIPS is 0.3065 vs truth 0.3042; with hidden taste the lift is overstated (+0.158 vs +0.100). This is the "looked like it worked" half of the project's story, and it is now demonstrable in one line.

### 4.3 Results dashboard (new)

`python -m p3ope report` builds `docs/dashboard.html` (548 KB, one file, no JavaScript, no network requests). Headline cards and per-scenario verdict tables are **computed from `results/*.jsonl`** at build time, not typed in. It shows failures as clearly as successes (for example rule v6's 6/144 false approvals and the earlier generator's 1/72).

### 4.4 Headline statistics module (new)

`p3ope/summary.py` computes false approvals, false rejects, correct approvals and the exact one-sided Clopper-Pearson bound without pandas. It matches `analysis/an_r12.py` exactly (for example 0/144 with upper bound 0.021).

### 4.5 Automated tests (new): 23 tests

| Group | What it checks |
|---|---|
| Import smoke | all 50 modules import; importing creates no files; scripts print usage instead of a traceback |
| Verdict logic | `vs`, `comb`, `verdict` truth tables |
| Estimators | `ess`, marginal-sensitivity bounds bracket SNIPS and collapse as lambda -> 1, Newton logistic fit recovers known coefficients |
| One-step baseline | unbiased without hidden taste, biased upward with it |
| Log integrity | every `.jsonl` line parses; r12 log has 192 unique records; v7 is never more permissive than v6 |
| Headline numbers | golden values equal to what `an_r12.py` prints (0/144, 26/48, 6/144, 1/72 ...) |
| Reproduction | fresh audits equal logged records (verdicts, guard share, bootstrap bound, ground truth) |
| Bad input | unknown shape, negative or NaN kappa, negative seed, tiny `--n` give a clean error |
| Dashboard | builds from logs, contains the headline numbers, makes no external requests |

### 4.6 Bug fixes

| File | Fix | Evidence |
|---|---|---|
| `experiments/r2_e4.py` | Wrapped in `main()` + `__main__` guard; prints usage when arguments are missing | Output byte-identical to the original (`cmp`); 6 records match the logged `r2_e4.jsonl` to 1.1e-16 |
| `experiments/r2_e1.py` | Same guard; plus `newton_ri(Xs.toarray(), ...)` to fix the sparse/dense crash | Original crashed; fixed version produces 16 records matching the logged `r2_e1.jsonl` to 1.7e-16 |

### 4.7 Documentation

* **README** rewritten: plain-language idea, 2-minute quick start, command table, layout (now includes `r12_lib` and the new files), testing, environment-variable table, troubleshooting. The original reproduction commands, "Not done" and "Notes" sections are kept verbatim.
* `docs/FILE_MAP.md`: rows appended for the previously unlisted Round 7-12 files and the new files (nothing removed).
* `requirements-tested.txt`: exact versions verified in this release. `requirements.txt` left unpinned as before.
* `.gitignore`: added `.pytest_cache/`, `.env`, `*.egg-info/`, `.DS_Store`.

### 4.8 Security and reliability review

| Check | Result |
|---|---|
| Hard-coded secrets, keys, tokens | None found (grep) |
| `eval`, `exec`, `pickle`, `subprocess`, `os.system`, sockets, HTTP | None in any `.py` file |
| Network access / databases / authentication | None exist; nothing to configure or leak |
| Untrusted input | Only CLI arguments: validated (type, range, allowed names); errors are one line, exit code 2, no traceback |
| Dashboard HTML | Static text escaped with `html.escape`; no JavaScript; no external requests (tested) |
| Destructive operations | None. Experiment scripts append to a path the user supplies; the original ZIP is untouched |
| Dependency vulnerability scan | **Not possible offline** (see section 8) |

---

## 5. Complete file list

**Modified (5):**
`README.md`, `.gitignore`, `docs/FILE_MAP.md`, `experiments/r2_e1.py`, `experiments/r2_e4.py`

**Added (11 files; the `tests/` folder holds 3 of them):**
`p3ope/audit.py`, `p3ope/summary.py`, `p3ope/report.py`, `p3ope/cli.py`, `p3ope/__main__.py`,
`tests/__init__.py`, `tests/test_core.py`, `tests/test_reproduce.py`,
`docs/dashboard.html`, `docs/improvement/IMPROVEMENT_REPORT.md`,
`requirements-tested.txt`, plus the `tests/` folder.

**Untouched:** all other files, including all of `results/`, `analysis/`, `figures/`, `docs/PREREGISTRATION.md`, `docs/RESULTS.md`, `docs/abstract.md`, and the other `p3ope/` and `experiments/` modules.

---

## 6. Feature status

| Feature | Status |
|---|---|
| Simulator, fatigue shapes, 5 generators | Fully working (pre-existing) |
| Final audit rule v7 | Fully working; now one command / one function; reproduces logs |
| Demo (`demo`, `audit`, `ope`, `summary`, `kinds`) | Fully working, verified |
| Results dashboard | Working; structure and content verified, **visual rendering not checked in a modern browser** |
| Tests | 23 pass |
| 20 analysis scripts | Fully working |
| n\* slice-size output in `audit` | **Not implemented** in the new entry point (exists in `r3_e1` / `r10_e1`) |
| Auditing *your own* log file (CSV/JSON of real impressions) | **Not implemented.** The audit runs on simulated data only. The simulators generate the logs, so supporting external data would need a data-schema design and is a new project, not a fix. |
| Open Bandit Dataset runs | Not included in the archive |
| KuaiRand real-dynamics validation | Not done (stretch goal, as the authors state) |
| Web UI / server | Does not exist and was deliberately not invented |

The research results themselves still carry the authors' documented limits: delayed-onset fatigue (third or later repeat) is only partly covered; the n\* band covers 85% (target 90%); on the earlier generator W4 the final rule leaves 1/72 false approvals (upper bound 0.064 vs target 0.05).

---

## 7. Test report (all commands were actually executed)

Environment: Python 3.12.3, numpy 2.4.4, scipy 1.17.1, scikit-learn 1.8.0, pandas 3.0.2, matplotlib 3.10.8, offline.

| # | Command / check | Result |
|---|---|---|
| 1 | `python -m compileall p3ope experiments analysis figures` | OK |
| 2 | Import every module (original, 46 modules) | 44 OK, **2 FAIL** (`r2_e1`, `r2_e4`) |
| 3 | Import every module (improved, 50 modules incl. the 4 new ones) | all OK (also asserted by the test suite) |
| 4 | Run all 20 `analysis.*` scripts on the original | 20/20 exit 0 |
| 5 | Re-run `an_r12`, `an_r11`, `an_r7` after my changes, `cmp` with step 4 | byte-identical |
| 6 | `r2_e4 1 out` before vs after fix, `cmp` | byte-identical |
| 7 | `r2_e4` fresh output vs `results/r2_e4.jsonl` | 6 records, max difference 1.1e-16 |
| 8 | `r2_e1` original | crashed (`ValueError`, sparse/dense) |
| 9 | `r2_e1 1 out` after fix vs `results/r2_e1.jsonl` | 16 records, 0 unmatched, max difference 1.7e-16 |
| 10 | Fresh audit (`cubic`, 0.05, seed 8001) vs `results/r12_e1.jsonl` | identical verdicts, `ff_flo` identical |
| 11 | `python -W error::ResourceWarning -m unittest discover -s tests` | **Ran 23 tests, OK** (about 86 s) |
| 12 | `python -m p3ope demo`, `audit`, `ope`, `summary`, `kinds`, `report` | all run; bad input exits 2 with one-line message |
| 13 | `diff -rq original improved` | only the 5 files in section 5 differ; new files only added |
| 14 | HTML structure check of dashboard | tags balanced, headline cards show 0/144, 6/144, 26/48, 1/72 |

---

## 8. Not verified / limitations

* **Full experiment re-runs** were not repeated (Round 7 alone is about 60 minutes on two cores). I verified reproduction on a sample of logged cells (steps 7, 9, 10) and by fresh audits in the test suite, not on every log.
* **Dashboard appearance**: only an old rendering engine was available (no CSS-variable support), so I did not claim a visual check. Open `docs/dashboard.html` in Chrome/Edge/Firefox once before presenting. No screenshots were produced.
* **Python 3.13** was not tested (3.12.3 only). The original authors report both.
* **No linter** (flake8/ruff/pytest not installed, no network) and **no dependency vulnerability audit**; I used `compileall`, imports, tests and a manual grep instead.
* Importing `analysis.*` modules runs them (they are scripts); the import smoke test therefore prints tables. Harmless.
* The audit works on **simulated** data only, as stated in the README.

---

## 9. Demo guide (5 minutes)

1. **Setup (before the audience arrives):**
   `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. **The problem (30 s):** open `figures/measured-feedback-architecture.png` or the dashboard top.
3. **Why one-step evaluation fails (30 s):**
   `python -m p3ope ope --beta 0.5 --gamma 0.8`
   Point at the gap: estimators say about +0.158, truth is +0.100, because hidden taste biases the logs.
4. **The audit on a harmful policy (90 s):**
   `python -m p3ope audit --kind cubic --kappa 0.5 --seed 1`
   Point at: one-step says +0.084, truth is -0.019, the audit refuses to approve (about 12 s; talk while it runs).
5. **The audit on a good policy (60 s):**
   `python -m p3ope audit --kind q2 --kappa 0.1 --seed 1` -> APPROVE, correct.
6. **Evidence at scale (60 s):** `python -m p3ope summary` and open `docs/dashboard.html`: 0/144 false approvals on a fresh generator, 26/48 correct approvals, and the honest misses.
7. **Reproducibility (30 s):** `python -m unittest tests.test_reproduce`.

**Honest talking points for judges:** failed targets are reported, always abstaining would also pass the false-approval target (so correct-approve is reported), results are simulator-only, KuaiRand real-data validation was not done.

---

## 10. Remaining requirements

* No credentials, databases or external services are needed for anything delivered.
* Optional future work (not done): real-data adapter (CSV schema), n\* size in the `audit` output, KuaiRand validation, Python 3.13 check, visual check of the dashboard.


## v44: second judge-panel fixes

| Judge point | Change | Where |
|---|---|---|
| J5/J2: abstract too long (about 1,070 words), dense | Cut to about 980 words (excluding references), terms defined once, free-form model and tail-weighted shape explained in plain words | `docs/abstract.md` |
| J5: diagram not mentioned | Abstract cites Figure 1 (`figures/measured-feedback-architecture.png`, checked: matches the current rule) | `docs/abstract.md` |
| J1: extrapolation beyond slice support | Stated that the coverage guard abstains instead of extrapolating | `docs/abstract.md` |
| J1: IPW clipping | Stated: static layer is round-0 only, no trajectory weights; weights unclipped by design, ESS/n warns | `docs/abstract.md` |
| J3: ablation of four-shape agreement | New pooled ablation; four-shape agreement is no better than the tail-weighted shape alone (13/216); free-form alone and final rule 1/216 | `analysis/an_ablation.py` |
| J2: decision-loss metric | Value per audit with harm weight lambda = 1, 5, 10; sealed generator, lambda = 1: final rule +0.0037, oracle +0.0068, one-step gate -0.0023 | `analysis/an_ablation.py` |
| J4: compute budget | Measured 8.5 s and 196 MB per audit, one core; 192-audit grid about 20 min | `docs/COMPUTE_BUDGET.md` |
| J4: drop order | Demo UI, then sensitivity bounds, then KuaiRand placebo | abstract section 8, `docs/COMPUTE_BUDGET.md` |
| Tests | Two new tests lock the ablation counts and the value ordering; full suite: 28 tests, OK | `tests/test_core.py` |

Not done: KuaiRand dynamics check, head-to-head with non-stationary OPE, MSM-bound tipping comparison, held-out pilot for n* winner's curse, prior projects per member. The last needs the team's input; the abstract keeps its placeholder.

## v46: third judge-panel fixes (panel fix 7, diagram alignment, deliberately not done)
| Panel fix | Change | Where |
|---|---|---|
| 1 Cut to about 900 words | Abstract rewritten (about 900 words excluding references); detail moved to RESULTS | `docs/abstract.md` |
| 2 Define n*, candidate policy; remove jargon; cite Shekhar and Howard | n* defined (80% power sizing), candidate policy defined, "Addendum 19", "anchor", "sealed generator" removed, [13] cited with a one-line difference | `docs/abstract.md` |
| 3 Interval method, larger B | Method stated (two-sided percentile); `--boot` option; 48 audits re-run at B = 200: 3 verdicts changed, 0 false approvals, B = 30 intervals about 10% narrower | `p3ope/audit.py`, `experiments/r15_e2.py`, RESULTS R15 |
| 4 Explain slice bias | Attenuation, not confounding; verified (bias vanishes when the true hidden term is supplied) | `experiments/r15_e3.py` |
| 5 Diagnose OBD miss | Target mismatch (fixed published BTS mix vs realised mix), from the earlier post-hoc diagnostic | abstract section 4 |
| 6 Reconcile timeline | "Exists today" listed; OBD loader and sensitivity bounds reworded as rebuild / wire in | abstract section 8 |
| 8 Second generator, independent worlds | W7 generator, 40 random worlds, all 5 pre-registered criteria pass; world-level counting added (0/21 worlds, bound 13%) | `p3ope/r15_lib.py`, `experiments/r15_e1.py`, `analysis/an_r15.py`, Addendum 20 |
| Tests | 4 new tests (Round15) | `tests/test_core.py` |

Not done: fix 7 (diagram/text alignment, skipped by request), prior projects per member (the team must supply real ones; the abstract keeps a placeholder), time-aware OPE baseline, backup owner for estimators.
