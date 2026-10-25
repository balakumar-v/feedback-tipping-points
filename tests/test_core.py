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


class ImportSmoke(unittest.TestCase):
    """Every module must import without side effects (r2_e1 / r2_e4 used to crash on import)."""

    def test_all_modules_import(self):
        names = [p[:-3].replace(os.sep, ".") for pat in ("p3ope/*.py", "experiments/*.py", "analysis/*.py")
                 for p in glob.glob(pat) if not p.endswith("__init__.py") and not p.endswith("__main__.py")]
        self.assertGreater(len(names), 40)
        for n in names:
            with self.subTest(module=n):
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
        recs = S.load_records("results/r12_e1.jsonl")
        self.assertEqual(len(recs), 192)
        self.assertEqual(len({(r["kind"], r["kappa"], r["seed"]) for r in recs}), 192)   # no duplicates
        self.assertTrue(all(r["v7"] in ("APPROVE", "NEED", "REJECT") for r in recs))
        self.assertTrue(all(r["v7"] != "APPROVE" or r["v6"] == "APPROVE" for r in recs))  # v7 can only be stricter than v6


class HeadlineNumbers(unittest.TestCase):
    """Golden values = what analysis/an_r12.py prints for the shipped logs."""

    def test_w5_headline(self):
        from p3ope import summary as S
        r = S.load_records("results/r12_e1.jsonl")
        h7, h6 = S.headline(r, "v7"), S.headline(r, "v6")
        self.assertEqual((h7["false_approve"], h7["n_worse"], h7["false_reject"], h7["correct_approve"], h7["n_better"]), (0, 144, 0, 26, 48))
        self.assertAlmostEqual(h7["fa_upper"], 0.021, places=3)
        self.assertEqual((h6["false_approve"], h6["correct_approve"]), (6, 29))
        self.assertAlmostEqual(h6["fa_upper"], 0.081, places=3)

    def test_w4_headline(self):
        from p3ope import summary as S
        h7 = S.headline(S.load_records("results/r12_e1_w4.jsonl"), "v7")
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


if __name__ == "__main__":
    unittest.main()
