"""Integration checks for exactly two scripted agents and causal receipt use."""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"examples"), str(ROOT/"src")]
from two_agents import DonorAgent, Outcome, find_return_receipt, simulate
from openworld_superkernel.world_fixture import Action, Agent, TickInput, Weather, advance, create_world


class TwoAgentTests(unittest.TestCase):
    def test_lost_cooperative_notices_lock_baseline_but_receipts_restore_activity(self):
        baseline = simulate(mode="notifications")
        fixed = simulate(mode="reconcile")
        self.assertLess(baseline["sent"], 20)
        self.assertEqual(baseline["pending"], 4)
        self.assertEqual(baseline["actual_loss"], 0)
        self.assertEqual(fixed["sent"], 20)
        self.assertEqual(fixed["returned"], 20)
        self.assertGreater(fixed["recovered_receipts"], 0)
        self.assertEqual(fixed["agents"], ["A", "B"])
        self.assertEqual(fixed["balances"], {"A": 8, "B": 0})

    def test_hostile_partner_cannot_create_receipts_and_safe_agents_stop_at_four(self):
        for mode in ("notifications", "reconcile"):
            result = simulate(mode=mode, scenario="hostile")
            self.assertEqual(result["sent"], 4)
            self.assertEqual(result["actual_loss"], 4)
            self.assertEqual(result["recovered_receipts"], 0)
            self.assertLessEqual(result["peak_actual_loss_plus_inflight"], 4)

    def test_timeout_negative_control_hides_real_loss(self):
        result = simulate(mode="unsafe_timeout", scenario="hostile")
        self.assertGreater(result["actual_loss"], 4)
        self.assertLessEqual(result["peak_booked_exposure"], 4)
        self.assertGreater(result["unsafe_releases"], 0)

    def test_recovery_does_not_replenish_permanent_loss_budget(self):
        result = simulate(mode="reconcile", scenario="recovery", drop_every=0)
        self.assertEqual(result["known_loss"], 4)
        self.assertEqual(result["sent"], 4)
        self.assertTrue(all(not row["gift"] for row in result["trace"][10:]))

    def test_late_duplicate_notification_does_not_double_release(self):
        a = DonorAgent("reconcile")
        a.budget.accepted(0)
        outcome = Outcome(0, True, "fixture-receipt-digest")
        self.assertTrue(a.receive(outcome, 1, reconciled=True))
        self.assertFalse(a.receive(outcome, 2))
        self.assertEqual(a.budget.exposure, 0)
        self.assertEqual(a.observations, 1)
        self.assertEqual(a.duplicates, 1)
        with self.assertRaises(ValueError):
            a.receive(Outcome(1, True), 2)

    def test_journal_without_committed_event_is_not_a_receipt(self):
        world = create_world((Agent("A", "owner", "r", 1),
                              Agent("B", "owner", "r", 1)), (("A", "B"),), seed=1)
        world = advance(world, TickInput(0, (), ())).world
        world = advance(world, TickInput(1, (Action("return-0", 1, "owner", "B", "A", "transfer", 1),), ())).world
        self.assertIsNotNone(find_return_receipt(world, 0))
        self.assertIsNone(find_return_receipt(replace(world, events=()), 0))

    def test_full_export_replays_using_only_recorded_inputs(self):
        result = json.loads(json.dumps(simulate(mode="reconcile", delay=2)))
        genesis = result["genesis"]
        world = create_world(tuple(Agent(**a) for a in genesis["agents"]),
                             tuple((a, b) for a, adjacent in genesis["graph"]
                                   for b in adjacent if a < b), seed=genesis["seed"])
        for batch in result["journal"]:
            world = advance(world, TickInput(batch["tick"],
                            tuple(Action(**a) for a in batch["actions"]),
                            tuple(Weather(**w) for w in batch["external"]),
                            batch["action_budget"]), max_actions=batch["action_budget"]).world
        self.assertEqual(world.fingerprint(), result["final_fingerprint"])
        self.assertEqual(result["policy_observations"],
                         result["delivered_observations"]+result["recovered_receipts"])

    def test_no_counterfactual_feedback_after_agent_stops(self):
        result = simulate(scenario="hostile", delay=0, drop_every=0)
        self.assertEqual(result["policy_observations"], result["sent"])
        self.assertEqual(result["sent"], 4)
        self.assertEqual(len(result["events"]), 4)

    def test_no_missing_feedback_means_same_world_for_all_modes(self):
        results = [simulate(mode=m, delay=0, drop_every=0)
                   for m in ("notifications", "reconcile", "unsafe_timeout")]
        self.assertEqual(len({r["final_fingerprint"] for r in results}), 1)
        self.assertTrue(all(r["sent"] == 20 for r in results))

    def test_cli_json_and_bounded_input_validation(self):
        process = subprocess.run([sys.executable, str(ROOT/"examples/two_agents.py"),
                                  "--json", "--rounds", "5"],
                                 capture_output=True, text=True, timeout=20)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(len(json.loads(process.stdout)), 3)
        for kwargs in ({"rounds": 21}, {"delay": 3}, {"drop_every": -1}, {"mode": "invent"}):
            with self.assertRaises(ValueError):
                simulate(**kwargs)


if __name__ == "__main__":
    unittest.main()
