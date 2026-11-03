"""P7: exact simulated return receipts versus censored policy notifications.

The timeout arm is deliberately unsafe. No public runtime or permission API.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import random
import sqlite3
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "benchmarks"))
from p2_stateful_cooperation import OPPORTUNITIES
from p3_mutual_learning_w3 import _exchange, make_router
from p5_risk_aware import genesis_world, partner_returns
from p6_risk_budget import receipt_dropped, receipt_due
from openworld_superkernel.risk_budget import CAP, DonorBudget
from openworld_superkernel.world_fixture import World, verify_replay

POLICIES = ("hold", "always_offer", "fixed_probe", "random_probe")
REGIMES = ("cooperative", "hostile", "recovery", "mixed")
FEEDBACKS = ("immediate", "delayed_censored")
MODES = ("notification_only", "exact_receipts", "unsafe_timeout")
SPLITS = {"development": (11101, 11102), "holdout": tuple(range(21101, 21111))}
PROTOCOL = ROOT / "docs/evaluation/P7-RECEIPT-RECONCILIATION-PROTOCOL.md"
SCHEMA = "openworld.p7.receipt-reconciliation.v0"


def return_receipt(world: World, op, origin: int) -> tuple[str | None, int]:
    """Positive evidence only; scoped to this one-transfer-per-pair fixture."""
    tick = 2 * origin + 1
    if tick >= world.tick:
        return None, 0
    action_id = f"p3-p7-back-{origin}-{op.recipient}"
    actions = [a for a in world.journal[tick].actions
               if a.request_id == action_id and a.kind == "transfer"
               and (a.actor, a.target, a.amount) == (op.recipient, op.actor, 1)]
    events = [e for e in world.events if e.tick == tick and e.kind == "transfer"
              and (e.actor, e.target, e.amount, e.provenance)
              == (op.recipient, op.actor, 1, "SIMULATED")]
    # Journal input alone is not proof an action was accepted.
    if len(actions) == len(events) == 1:
        return events[0].digest, len(world.events)
    return None, len(world.events)


def run_case(policy: str, regime: str, feedback: str, mode: str, *, seed: int) -> dict:
    if (policy not in POLICIES or regime not in REGIMES
            or feedback not in FEEDBACKS or mode not in MODES
            or type(seed) is not int or not 0 <= seed < 2**31):
        raise ValueError("invalid bounded P7 case")
    router, tokens = make_router()
    genesis = world = genesis_world(seed)
    budgets = {op.actor: DonorBudget(policy) for op in OPPORTUNITIES}
    actual_losses = dict.fromkeys(budgets, 0)
    first_block = dict.fromkeys(budgets)
    notices = []
    rewards = []
    receipts = []
    donations = returns = delivered = duplicates = timeouts = 0
    lookups = inspections = actual_peak = 0
    reconciliation_cpu = 0.0
    switch_state = {}
    for rnd in range(20):
        for notice in tuple(notices):
            due, origin, donor, success, dropped = notice
            if due == rnd:
                if not dropped:
                    if origin in budgets[donor].pending:
                        budgets[donor].observed_outcome(origin, success, rnd)
                        delivered += 1
                    else:
                        duplicates += 1
                notices.remove(notice)
        t0 = time.process_time()
        if mode == "exact_receipts" and rnd % 3 == 0:
            for op in OPPORTUNITIES:
                for origin in sorted(budgets[op.actor].pending):
                    digest, inspected = return_receipt(world, op, origin)
                    lookups += 1
                    inspections += inspected
                    if digest is not None:
                        budgets[op.actor].observed_outcome(origin, True, rnd)
                        receipts.append({"donor": op.actor, "origin": origin,
                                         "at_round": rnd, "digest": digest})
        elif mode == "unsafe_timeout":
            for budget in budgets.values():
                expired = {origin for origin in budget.pending if rnd - origin >= 3}
                budget.pending.difference_update(expired)
                timeouts += len(expired)
                # Intentionally no evidence or learning sample: an unsafe release.
        reconciliation_cpu += time.process_time() - t0
        if rnd == 10:
            switch_state = {a: {"known_bad": b.known_bad, "pending": len(b.pending)}
                            for a, b in budgets.items()}
        selected, asks = [], []
        balances = dict(world.balances)
        for op in OPPORTUNITIES:
            budget = budgets[op.actor]
            if budget.choose(seed, rnd, op.recipient, balances[op.actor]):
                asks.append(_exchange(world, tokens, actor=op.actor,
                    recipient=op.recipient, source=op.source_group,
                    target=op.target_group, round_index=rnd, label="p7-give"))
                selected.append(op)
            elif budget.exposure >= CAP and first_block[op.actor] is None:
                first_block[op.actor] = rnd
        outgoing = router.advance(world, exchanges=tuple(asks), max_actions=10)
        expected = {f"p3-p7-give-{rnd}-{op.actor}" for op in selected}
        if outgoing.state.rejected or set(outgoing.state.accepted) != expected:
            raise AssertionError("P7 donation not committed exactly once")
        world = outgoing.state.world
        for op in selected:
            budgets[op.actor].accepted(rnd)
            actual_peak = max(actual_peak, actual_losses[op.actor] + 1)
        responding = [op for op in selected
                      if partner_returns(regime, seed, rnd, op.recipient)]
        replies = tuple(_exchange(world, tokens, actor=op.recipient,
            recipient=op.actor, source=op.target_group, target=op.source_group,
            round_index=rnd, label="p7-back") for op in responding)
        back = router.advance(world, exchanges=replies, max_actions=10)
        expected = {f"p3-p7-back-{rnd}-{op.recipient}" for op in responding}
        if back.state.rejected or set(back.state.accepted) != expected:
            raise AssertionError("P7 return not committed exactly once")
        world = back.state.world
        donations += len(selected)
        returns += len(responding)
        rewards.append((-0.25 * len(selected) + 0.85 * len(responding)) / 10)
        for op in selected:
            success = f"p3-p7-back-{rnd}-{op.recipient}" in expected
            actual_losses[op.actor] += int(not success)
            due = receipt_due(feedback, seed, rnd, op.recipient)
            dropped = receipt_dropped(feedback, seed, rnd, op.recipient)
            if due == rnd:
                if not dropped:
                    budgets[op.actor].observed_outcome(rnd, success, rnd)
                    delivered += 1
            else:
                notices.append((due, rnd, op.actor, success, dropped))
        if any(b.exposure > CAP for b in budgets.values()):
            raise AssertionError("P7 policy-accounted cap exceeded")
        if mode != "unsafe_timeout" and actual_peak > CAP:
            raise AssertionError("P7 safe-mode actual cap exceeded")
    if not verify_replay(genesis, world) or world.tick != 40:
        raise AssertionError("P7 replay failed")
    if sum(v for _, v in genesis.balances) != sum(v for _, v in world.balances):
        raise AssertionError("P7 resource conservation failed")
    if any(e.provenance != "SIMULATED" for e in world.events):
        raise AssertionError("P7 invalid provenance")
    return {"policy": policy, "regime": regime, "feedback": feedback, "mode": mode,
            "seed": seed, "initial_hash": genesis.fingerprint(),
            "final_hash": world.fingerprint(), "replay_verified": True,
            "registered_agents": 30, "active_donors": 10, "ticks": world.tick,
            "reward": statistics.fmean(rewards),
            "phase_rewards": [statistics.fmean(rewards[:10]), statistics.fmean(rewards[10:])],
            "donations": donations, "returns": returns,
            "known_bad": sum(b.known_bad for b in budgets.values()),
            "unresolved": sum(len(b.pending) for b in budgets.values()),
            "actual_losses": sum(actual_losses.values()),
            "peak_actual_loss_plus_inflight": actual_peak,
            "peak_policy_exposure": max(b.peak_exposure for b in budgets.values()),
            "cap_blocks": sum(b.blocked for b in budgets.values()),
            "delivered_observations": delivered,
            "policy_observations": sum(len(b.observed) for b in budgets.values()),
            "duplicate_notifications_skipped": duplicates,
            "timeout_releases": timeouts, "receipt_lookups": lookups,
            "event_inspections": inspections, "recovered_receipts": receipts,
            "reconciliation_cpu_seconds": reconciliation_cpu,
            "at_round_10": switch_state, "first_cap_block_round": first_block}


def paired_summary(cases: list[dict]) -> list[dict]:
    result = []
    for policy in POLICIES:
        for regime in REGIMES:
            for feedback in FEEDBACKS:
                subset = [c for c in cases if (c["policy"], c["regime"], c["feedback"])
                          == (policy, regime, feedback)]
                paired = {}
                for c in subset:
                    paired.setdefault(c["seed"], {})[c["mode"]] = c["reward"]
                differences = [p["exact_receipts"] - p["notification_only"]
                               for _, p in sorted(paired.items())]
                rng = random.Random(7042026)
                means = sorted(statistics.fmean(rng.choices(differences, k=len(differences)))
                               for _ in range(2000))
                result.append({"policy": policy, "regime": regime, "feedback": feedback,
                    "seed_clusters": len(differences), "paired_differences": differences,
                    "mean_reward_difference": statistics.fmean(differences),
                    "bootstrap_percentile_95": [means[49], means[1949]]})
    return result


def source_identity() -> dict:
    files = sorted((ROOT / "src").rglob("*.py")) + sorted((ROOT / "benchmarks").glob("*.py"))
    files += sorted((ROOT / "tests").glob("*.py"))
    files += [PROTOCOL]
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout.strip()
    return {"git_revision": revision,
            "sha256": {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest()
                       for p in files}}


def evaluate(split: str = "holdout") -> dict:
    if split not in SPLITS:
        raise ValueError("unknown preregistered split")
    identity = source_identity()
    wall, cpu = time.perf_counter(), time.process_time()
    cases = [run_case(p, r, f, m, seed=s) for s in SPLITS[split]
             for p in POLICIES for r in REGIMES for f in FEEDBACKS for m in MODES]
    for seed in SPLITS[split]:
        if len({c["initial_hash"] for c in cases if c["seed"] == seed}) != 1:
            raise AssertionError("P7 unequal starting worlds")
    result = {"schema": SCHEMA, "split": split, "source": identity, "cases": cases,
              "paired_summary": paired_summary(cases),
              "environment": {"python": sys.version, "sqlite": sqlite3.sqlite_version,
                              "platform": platform.platform(), "cpu_count": os.cpu_count()},
              "wall_seconds": time.perf_counter() - wall,
              "process_cpu_seconds": time.process_time() - cpu}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=tuple(SPLITS), default="holdout")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    output = json.dumps(evaluate(args.split), sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
