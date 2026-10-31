"""Fast checks (about 30 s): imports, verdict logic, estimator maths, log integrity, headline numbers.

Run from the repository root:   python -m unittest discover -s tests -v
"""
import glob
import importlib
import json
import os
import subprocess
import sys
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)  # the code reads results/ and figures/ with relative paths


# Round-1 scripts that execute on import; see ImportSmoke.test_all_modules_import.
SCRIPT_ONLY = {
    "experiments.e2_audit", "experiments.e4_loop", "experiments.e4_loop2", "experiments.exp14_e4",
    "experiments.exp6_gen", "experiments.exp2b", "analysis.exp6_an",
    "experiments.e5_obd", "experiments.e5_full", "experiments.e5_diag",
    "experiments.xcheck_obp", "experiments.xcheck_obp_src",
}


class ImportSmoke(unittest.TestCase):
    """Every module must import without side effects (r2_e1 / r2_e4 used to crash on import)."""

    def test_all_modules_import(self):
        names = [p[:-3].replace(os.sep, ".") for pat in ("p3ope/*.py", "experiments/*.py", "analysis/*.py")
                 for p in glob.glob(pat) if not p.endswith("__init__.py") and not p.endswith("__main__.py")]
        self.assertGreater(len(names), 40)
        for n in names:
            with self.subTest(module=n):
                if n in SCRIPT_ONLY:
                    # Run-on-import scripts (read sys.argv, need the optional `obp` package or an
                    # external tasks.csv, or write results). Importing would execute them, so only
                    # check that they compile.
                    path = n.replace(".", os.sep) + ".py"
                    with open(os.path.join(ROOT, path)) as fh:
                        compile(fh.read(), path, "exec")
                else:
                    importlib.import_module(n)

    def test_import_creates_no_files(self):
        before = set(os.listdir(os.path.join(ROOT, "results")))
        importlib.import_module("experiments.r2_e1")
        importlib.import_module("experiments.r2_e4")
        self.assertEqual(before, set(os.listdir(os.path.join(ROOT, "results"))))

    def test_experiment_without_args_prints_usage(self):
        r = subprocess.run([sys.executable, "-m", "experiments.r2_e4"], capture_output=True, text=True, cwd=ROOT)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("usage", (r.stderr + r.stdout).lower())
        self.assertNotIn("Traceback", r.stderr)


class VerdictLogic(unittest.TestCase):
    def test_vs_three_outcomes(self):
        from experiments.r2_e5 import vs
        self.assertEqual(vs(0.01, 0.05, 0.01, 0.05), "APPROVE")   # both lower bounds > 0
        self.assertEqual(vs(-0.02, -0.001, -0.03, -0.01), "REJECT")
        self.assertEqual(vs(-0.01, 0.05, 0.01, 0.05), "NEED")      # static interval straddles 0

    def test_comb_requires_agreement(self):
        from experiments.r2_e5 import comb
        self.assertEqual(comb(["APPROVE"] * 4), "APPROVE")
        self.assertEqual(comb(["REJECT"] * 4), "REJECT")
        self.assertEqual(comb(["APPROVE", "APPROVE", "APPROVE", "NEED"]), "NEED")
        self.assertEqual(comb(["APPROVE", "REJECT"]), "NEED")

    def test_tipping_verdict(self):
        from p3ope.exp13_lib import verdict
        self.assertEqual(verdict(0.01, 0.05, 0.1, 0.3, 0.8), "APPROVE")   # kappa-hat clearly below kappa*
        self.assertEqual(verdict(0.01, 0.05, 0.9, 1.2, 0.8), "REJECT")    # kappa-hat clearly above kappa*
        self.assertEqual(verdict(0.01, 0.05, 0.5, 1.2, 0.8), "NEED_DATA")


class Estimators(unittest.TestCase):
    def test_ess_bounds(self):
        from p3ope.ope_pilot import ess
        self.assertAlmostEqual(ess(np.ones(100)), 100.0)
        self.assertLess(ess(np.array([100.0] + [1.0] * 99)), 10)

    def test_msm_bounds_bracket_snips(self):
        from p3ope.ope_pilot import msm_bounds
        rng = np.random.default_rng(0)
        n = 500
        e = rng.uniform(0.05, 0.5, n); c = rng.uniform(0.0, 1.0, n); y = (rng.random(n) < 0.3).astype(float)
        lo, hi = msm_bounds(c, y, e, 1.5)
        pt = (c / e * y).sum() / (c / e).sum()
        self.assertLessEqual(lo, pt + 1e-9); self.assertGreaterEqual(hi, pt - 1e-9)
        lo1, hi1 = msm_bounds(c, y, e, 1.0001)               # lambda -> 1 collapses to the point estimate
        self.assertAlmostEqual(lo1, pt, places=3); self.assertAlmostEqual(hi1, pt, places=3)

    def test_newton_fits_logistic(self):
        from p3ope.exp13_lib import newton
        rng = np.random.default_rng(1)
        X = np.column_stack([np.ones(5000), rng.normal(size=5000)])
        p = 1 / (1 + np.exp(-(X @ np.array([-0.5, 1.0])))); y = (rng.random(5000) < p).astype(float)
        b = newton(X, y, np.ones(5000), None, 10)
        self.assertLess(abs(b[0] + 0.5), 0.1); self.assertLess(abs(b[1] - 1.0), 0.1)


class OneStepBaseline(unittest.TestCase):
    """`python -m p3ope ope`: unbiased without hidden taste, biased with it."""

    def _snips_minus_truth(self, beta, gamma):
        from p3ope import ope_pilot as op
        rng = np.random.default_rng(0)
        logs = op.sample_logs(20000, rng, beta=beta, gamma=gamma)
        est = op.estimates(op.terms(logs, op.pi_new(logs["X"]), op.fit_q(logs["X"], logs["a"], logs["y"])))
        return est["snips"] - op.truth(op.pi_new, np.random.default_rng(1), gamma=gamma, beta=beta)

    def test_unconfounded_is_close(self):
        self.assertLess(abs(self._snips_minus_truth(0.0, 0.0)), 0.02)

    def test_hidden_taste_biases_upward(self):
        self.assertGreater(self._snips_minus_truth(0.5, 0.8), 0.03)

    def test_cli_rejects_tiny_n(self):
        r = subprocess.run([sys.executable, "-m", "p3ope", "ope", "--n", "5"], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)


class LogIntegrity(unittest.TestCase):
    def test_every_jsonl_line_parses(self):
        files = glob.glob("results/**/*.jsonl", recursive=True)
        self.assertGreater(len(files), 30)
        for f in files:
            with self.subTest(file=f):
                with open(f) as fh:
                    for line in fh:
                        if line.strip():
                            json.loads(line)

    def test_r12_log_shape(self):
        from p3ope import summary as S
        recs = S.load_records("results/round-12/r12_e1.jsonl")
        self.assertEqual(len(recs), 192)
        self.assertEqual(len({(r["kind"], r["kappa"], r["seed"]) for r in recs}), 192)   # no duplicates
        self.assertTrue(all(r["v7"] in ("APPROVE", "NEED", "REJECT") for r in recs))
        self.assertTrue(all(r["v7"] != "APPROVE" or r["v6"] == "APPROVE" for r in recs))  # v7 can only be stricter than v6


class HeadlineNumbers(unittest.TestCase):
    """Golden values = what analysis/an_r12.py prints for the shipped logs."""

    def test_w5_headline(self):
        from p3ope import summary as S
        r = S.load_records("results/round-12/r12_e1.jsonl")
        h7, h6 = S.headline(r, "v7"), S.headline(r, "v6")
        self.assertEqual((h7["false_approve"], h7["n_worse"], h7["false_reject"], h7["correct_approve"], h7["n_better"]), (0, 144, 0, 26, 48))
        self.assertAlmostEqual(h7["fa_upper"], 0.021, places=3)
        self.assertEqual((h6["false_approve"], h6["correct_approve"]), (6, 29))
        self.assertAlmostEqual(h6["fa_upper"], 0.081, places=3)

    def test_w4_headline(self):
        from p3ope import summary as S
        h7 = S.headline(S.load_records("results/round-12/r12_e1_w4.jsonl"), "v7")
        self.assertEqual((h7["false_approve"], h7["n_worse"], h7["correct_approve"], h7["n_better"]), (1, 72, 8, 24))

    def test_clopper_pearson(self):
        from p3ope.summary import clopper_pearson_upper
        self.assertEqual(clopper_pearson_upper(5, 5), 1.0)
        self.assertAlmostEqual(clopper_pearson_upper(0, 59), 1 - 0.05 ** (1 / 59), places=6)  # the "rule of 59" in the pre-registration

    def test_missing_log_gives_clear_error(self):
        from p3ope import summary as S
        with self.assertRaises(FileNotFoundError):
            S.load_records("results/does_not_exist.jsonl")


class AuditInput(unittest.TestCase):
    def test_validation(self):
        from p3ope.audit import validate
        validate("cubic", 0.2, 1)
        for bad in (("nope", 0.2, 1), ("cubic", -1, 1), ("cubic", float("nan"), 1), ("cubic", 0.2, -3)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate(*bad)

    def test_cli_rejects_bad_shape_cleanly(self):
        r = subprocess.run([sys.executable, "-m", "p3ope", "audit", "--kind", "nope"], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 2)
        self.assertIn("unknown fatigue shape", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


class Dashboard(unittest.TestCase):
    def test_dashboard_builds_from_logs(self):
        import tempfile
        from p3ope.report import build
        with tempfile.TemporaryDirectory() as d:
            out = build(os.path.join(d, "dash.html"))
            html = open(out, encoding="utf-8").read()
        for needle in ("0/144", "26/48", "<table>", 'lang="en"', "prefers-color-scheme"):
            self.assertIn(needle, html)
        self.assertNotIn("http://", html.replace("http://www.w3.org", ""))   # no external requests


class Round13(unittest.TestCase):
    """Golden values for the strict-panel round (R13): guard stress and the drift MVP."""

    def test_guard_stress(self):
        import glob
        from p3ope import summary as S
        r = [x for f in sorted(glob.glob("results/round-13/r13_e1_*.jsonl")) for x in S.load_records(f)]
        self.assertEqual(len(r), 96)
        self.assertTrue(all(x["guard_fires"] for x in r))
        h7 = S.headline(r, "v7")
        self.assertEqual((h7["false_approve"], h7["n_worse"], h7["correct_approve"], h7["n_better"]), (0, 72, 0, 24))
        self.assertEqual(S.headline(r, "v5")["correct_approve"], 23)   # without the guard it would approve 23/24

    def test_drift_mvp(self):
        from p3ope import summary as S
        r = S.load_records("results/round-13/mvp_drift_logit_d1.0.jsonl")
        self.assertEqual(len(r), 200)
        self.assertEqual(sum(x["ba_wrong_sign"] for x in r), 200)
        self.assertAlmostEqual(sum(x["dr_cov"] for x in r) / 200, 0.935, places=3)

    def test_drift_reproduces_exactly(self):
        from experiments import mvp_drift as M
        first = json.loads(open("results/round-13/mvp_drift_dir_d1.0.jsonl").readline()) if os.path.exists("results/round-13/mvp_drift_dir_d1.0.jsonl") else None
        if first is None:
            self.skipTest("log missing")
        self.assertAlmostEqual(M.one(first["seed"], first["truth"])["dr"], first["dr"], places=9)




class TestAblation(unittest.TestCase):
    """Post-hoc ablation and decision-value script (analysis/an_ablation.py)."""

    def test_headline_counts(self):
        from analysis import an_ablation as ab
        from p3ope.summary import load_records
        sealed = [r for f in ab.SEALED for r in load_records(f)]
        t = ab.rule_table(sealed)
        s = ab.score(sealed, t["four + guard + veto (final v7)"])
        self.assertEqual((s["fa"], s["nw"], s["ca"], s["nb"]), (0, 144, 26, 48))
        design = [r for f in ab.DESIGN for r in load_records(f)]
        td = ab.rule_table(design)
        self.assertEqual(ab.score(design, td["four-shape agreement"])["fa"], 13)
        self.assertEqual(ab.score(design, td["free-form model alone"])["fa"], 1)

    def test_decision_value_orders_rules(self):
        from analysis import an_ablation as ab
        from p3ope.summary import load_records
        sealed = [r for f in ab.SEALED for r in load_records(f)]
        t = ab.rule_table(sealed)
        final = ab.decision_value(sealed, t["four + guard + veto (final v7)"], 1)
        oracle = ab.decision_value(sealed, [("APPROVE" if r["true10"] > 0 else "REJECT") for r in sealed], 1)
        onestep = ab.decision_value(sealed, ["APPROVE" if r["one_step_lo"] > 0 else "NEED" for r in sealed], 1)
        self.assertGreater(final, onestep)
        self.assertGreater(oracle, final)


class Round15(unittest.TestCase):
    """R15 (Addendum 20): W7 generator, larger-B option, analysis script."""

    def test_w7_worlds_differ_and_are_reproducible(self):
        from p3ope import r15_lib as W7
        a, b = W7.world(3), W7.world(4)
        self.assertNotEqual((a["phi"], a["rdec"]), (b["phi"], b["rdec"]))
        self.assertEqual(W7.world(3)["phi"], a["phi"])
        d1 = W7.sim_w7(300, np.random.default_rng(1), 3, 0.3, .5, .8, "tail", T=6)
        d2 = W7.sim_w7(300, np.random.default_rng(1), 3, 0.3, .5, .8, "tail", T=6)
        self.assertTrue(np.array_equal(d1["Y"], d2["Y"]))
        self.assertEqual(set(d1), {"X0", "A", "Y", "G", "e", "n", "T"})

    def test_w7_truth_falls_with_kappa(self):
        from p3ope import r15_lib as W7
        lifts = [W7.true_lift_w7(0, k, .5, .8, n=8000) for k in (0.02, 0.2, 0.8)]
        self.assertGreater(lifts[0], lifts[1]); self.assertGreater(lifts[1], lifts[2]); self.assertLess(lifts[2], 0)

    def test_boot_validation_and_default(self):
        from p3ope.audit import run_audit
        with self.assertRaises(ValueError): run_audit("cubic", 0.2, 1, with_truth=False, boot=3)
        from experiments import r12_e1 as F
        self.assertEqual(F.B, 30)

    def test_analysis_world_count(self):
        import io, contextlib
        from analysis import an_r15
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): an_r15.r14_worlds()
        out = buf.getvalue()
        self.assertIn("192 audits = 12 worlds (cells) x 16 fresh datasets", out)
        self.assertIn("truly-worse worlds 9", out)


if __name__ == "__main__":
    unittest.main()
