"""Slow checks (about 1 minute): a fresh audit must reproduce the logged records exactly.

    python -m unittest tests.test_reproduce -v
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


class ReproduceLoggedRuns(unittest.TestCase):
    def _logged(self, kind, kappa, seed):
        with open("results/r12_e1.jsonl") as fh:
            for line in fh:
                r = json.loads(line)
                if (r["kind"], r["kappa"], r["seed"]) == (kind, kappa, seed):
                    return r
        self.fail("record not found")

    def test_audit_matches_log(self):
        from p3ope.audit import run_audit
        for kind, kappa, seed in (("cubic", 0.05, 8000), ("cubic", 0.5, 8003)):
            with self.subTest(kind=kind, kappa=kappa, seed=seed):
                rec = self._logged(kind, kappa, seed)
                rep = run_audit(kind, kappa, seed, with_truth=True)
                self.assertEqual(rep.verdict, rec["v7"])
                self.assertEqual(rep.verdict_v6, rec["v6"])
                self.assertAlmostEqual(rep.unsupported_share, rec["unsup"], places=9)
                self.assertAlmostEqual(rep.shapes["ff"].forecast_lo, rec["ff_flo"], places=9)
                self.assertAlmostEqual(rep.shapes["lin"].static_lift_lo, rec["slo"], places=9)
                self.assertAlmostEqual(rep.true_lift, rec["true10"], places=9)
                for s in ("lin", "log", "mem7", "tail2"):
                    self.assertEqual(rep.shapes[s].verdict, rec[f"{s}_v"])

    def test_bad_policy_is_never_approved_in_demo_scenario(self):
        from p3ope.audit import run_audit
        rep = run_audit("cubic", 0.5, 1)
        self.assertLess(rep.true_lift, 0)
        self.assertNotEqual(rep.verdict, "APPROVE")
        self.assertGreater(rep.one_step_snips, 0)   # the static estimate is fooled; the audit is not


if __name__ == "__main__":
    unittest.main()
