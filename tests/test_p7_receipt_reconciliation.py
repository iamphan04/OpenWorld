"""Causal observation and accounting checks for the optional P7 fixture."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "benchmarks"))
from p7_receipt_reconciliation import SPLITS, run_case, return_receipt
from p2_stateful_cooperation import OPPORTUNITIES
from p5_risk_aware import genesis_world
from openworld_superkernel.risk_budget import CAP, DonorBudget


class ReceiptReconciliationTests(unittest.TestCase):
    def test_absorbing_confirmed_loss_budget_cannot_probe_later_recovery(self):
        budget = DonorBudget("random_probe")
        for origin in range(CAP):
            budget.accepted(origin)
            budget.observed_outcome(origin, False, origin)
        for rnd in range(10, 20):
            self.assertFalse(budget.choose(11101, rnd, "a10", 8))
        self.assertEqual(budget.known_bad, CAP)
        self.assertEqual(budget.pending, set())

    def test_no_receipt_exists_for_an_unmade_or_future_transfer(self):
        world = genesis_world(11101)
        self.assertEqual(return_receipt(world, OPPORTUNITIES[0], 0), (None, 0))

    def test_missing_notifications_only_release_on_actual_receipts(self):
        baseline = run_case("always_offer", "cooperative", "delayed_censored",
                            "notification_only", seed=11101)
        recovered = run_case("always_offer", "cooperative", "delayed_censored",
                             "exact_receipts", seed=11101)
        self.assertGreater(len(recovered["recovered_receipts"]), 0)
        self.assertGreaterEqual(recovered["reward"], baseline["reward"])
        self.assertLessEqual(recovered["unresolved"], baseline["unresolved"])
        self.assertLessEqual(recovered["peak_actual_loss_plus_inflight"], CAP)
        self.assertEqual(recovered["known_bad"], 0)
        self.assertEqual(recovered["policy_observations"],
                         recovered["delivered_observations"] + len(recovered["recovered_receipts"]))

    def test_no_positive_receipt_is_invented_for_hostile_partner(self):
        result = run_case("always_offer", "hostile", "delayed_censored",
                          "exact_receipts", seed=11101)
        self.assertEqual(result["recovered_receipts"], [])
        self.assertEqual(result["returns"], 0)
        self.assertEqual(result["actual_losses"], 40)
        self.assertLessEqual(result["peak_actual_loss_plus_inflight"], CAP)

    def test_timeout_can_breach_actual_cap_despite_internal_cap(self):
        result = run_case("always_offer", "hostile", "delayed_censored",
                          "unsafe_timeout", seed=11101)
        self.assertGreater(result["timeout_releases"], 0)
        self.assertGreater(result["peak_actual_loss_plus_inflight"], CAP)
        self.assertLessEqual(result["peak_policy_exposure"], CAP)

    def test_immediate_observation_makes_reconciliation_redundant(self):
        a = run_case("random_probe", "mixed", "immediate", "notification_only", seed=11102)
        b = run_case("random_probe", "mixed", "immediate", "exact_receipts", seed=11102)
        for field in ("reward", "final_hash", "donations", "returns", "policy_observations"):
            self.assertEqual(a[field], b[field])
        self.assertEqual(b["recovered_receipts"], [])

    def test_hold_cannot_receive_counterfactual_feedback(self):
        result = run_case("hold", "cooperative", "delayed_censored", "exact_receipts", seed=11101)
        self.assertEqual(result["policy_observations"], 0)
        self.assertEqual(result["reward"], 0)
        self.assertEqual(result["recovered_receipts"], [])

    def test_splits_are_disjoint_from_published_p6_and_each_other(self):
        self.assertFalse(set(SPLITS["development"]) & set(SPLITS["holdout"]))
        self.assertFalse(set(range(10101, 10111)) & set(SPLITS["holdout"]))

    def test_invalid_modes_fail_closed(self):
        with self.assertRaises(ValueError):
            run_case("always_offer", "hostile", "immediate", "invented_credit", seed=11101)


if __name__ == "__main__":
    unittest.main()
