"""Two scripted agents exchanging SIMULATED resources through the W3 gateway.

A uses the existing four-unit DonorBudget. B returns or keeps committed gifts.
Transfers settle immediately; only A's outcome notifications can be delayed or
dropped. This is a single-owner, trusted-host example, not an LLM or network.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from openworld_superkernel.risk_budget import CAP, DonorBudget
from openworld_superkernel.trust_boundaries import CapabilityAuthority
from openworld_superkernel.world_fixture import Action, Agent, World, create_world, verify_replay
from openworld_superkernel.world_guard import AuthorizedWorldAction, GuardedWorldGateway

MODES = ("notifications", "reconcile", "unsafe_timeout")
SCENARIOS = ("cooperative", "hostile", "recovery")
OWNER, PRINCIPAL = "two-agent-owner", "trusted-demo-host"


@dataclass(frozen=True)
class Outcome:
    origin: int
    returned: bool
    receipt_digest: str | None = None


@dataclass
class DonorAgent:
    """A's private policy state; no access to the evaluator's loss count."""
    mode: str
    budget: DonorBudget = field(default_factory=lambda: DonorBudget("always_offer"))
    observations: int = 0
    reconciled: int = 0
    duplicates: int = 0

    def __post_init__(self):
        if self.mode not in MODES:
            raise ValueError("unknown donor mode")

    def choose(self, round_index: int, own_balance: int) -> bool:
        return self.budget.choose(0, round_index, "B", own_balance)

    def receive(self, outcome: Outcome, at_round: int, *, reconciled=False) -> bool:
        if outcome.returned and not outcome.receipt_digest:
            raise ValueError("positive feedback requires a committed return receipt")
        if outcome.origin not in self.budget.pending:
            self.duplicates += 1
            return False
        self.budget.observed_outcome(outcome.origin, outcome.returned, at_round)
        self.observations += 1
        self.reconciled += int(reconciled)
        return True

    def reconcile(self, world: World, at_round: int) -> int:
        recovered = 0
        for origin in sorted(self.budget.pending):
            receipt = find_return_receipt(world, origin)
            if receipt is not None:
                recovered += self.receive(receipt, at_round, reconciled=True)
        return recovered

    def expire_without_evidence(self, at_round: int) -> int:
        """Explicitly unsafe negative control; never creates a learning sample."""
        expired = {origin for origin in self.budget.pending if at_round-origin >= 3}
        self.budget.pending.difference_update(expired)
        return len(expired)


@dataclass(frozen=True)
class RecipientAgent:
    """B sees whether this round's gift actually committed before deciding."""
    scenario: str
    recover_at: int = 10

    def choose_return(self, *, gift_received: bool, round_index: int) -> bool:
        return gift_received and (self.scenario == "cooperative" or
                                 self.scenario == "recovery" and round_index >= self.recover_at)


def find_return_receipt(world: World, origin: int) -> Outcome | None:
    """Match a positive journal action AND event in this one-pair/two-phase fixture.

    Inputs alone do not prove acceptance. No negative outcome is inferred from
    a missing return; unresolved reservations remain. Full replay verifies the
    final trusted world. This is not a general asynchronous receipt protocol.
    """
    if type(origin) is not int or origin < 0:
        raise ValueError("invalid transfer origin")
    tick = 2*origin + 1
    if tick >= world.tick:
        return None
    actions = [a for a in world.journal[tick].actions
               if a.request_id == f"return-{origin}" and
               (a.kind, a.actor, a.target, a.amount) == ("transfer", "B", "A", 1)]
    events = [e for e in world.events if e.tick == tick and
              (e.kind, e.actor, e.target, e.amount, e.provenance)
              == ("transfer", "B", "A", 1, "SIMULATED")]
    if len(actions) == len(events) == 1:
        return Outcome(origin, True, events[0].digest)
    return None


def simulate(*, mode="reconcile", scenario="cooperative", rounds=20,
             drop_every=2, delay=1, recover_at=10, seed=2026) -> dict:
    if (mode not in MODES or scenario not in SCENARIOS
            or type(rounds) is not int or not 1 <= rounds <= 20
            or type(drop_every) is not int or drop_every < 0
            or type(delay) is not int or not 0 <= delay <= 2
            or type(recover_at) is not int or not 0 <= recover_at <= 20
            or type(seed) is not int or not 0 <= seed < 2**31):
        raise ValueError("invalid bounded two-agent simulation settings")
    a, b = DonorAgent(mode), RecipientAgent(scenario, recover_at)
    genesis = world = create_world((Agent("A", OWNER, "local", 8),
                                    Agent("B", OWNER, "local", 0)),
                                   (("A", "B"),), seed=seed)
    authority = CapabilityAuthority(os.urandom(32), issuer="two-agent-demo", audience="local")
    gateway = GuardedWorldGateway(authority, authenticated_principal=lambda: PRINCIPAL)
    now = int(time.time())
    tokens = {actor: authority.issue(principal=PRINCIPAL, owner=OWNER,
              resource=actor, action="write_agent", valid_from=now-10,
              expires_at=now+120) for actor in ("A", "B")}
    channel: list[tuple[int, Outcome]] = []
    trace = []
    sent = returned = dropped = delivered = expired = true_peak = 0

    def commit(actor, target, request_id, enabled):
        nonlocal world
        actions = (AuthorizedWorldAction(Action(request_id, world.tick, OWNER,
                    actor, target, "transfer", 1), tokens[actor]),) if enabled else ()
        step = gateway.advance(world, actions=actions, max_actions=1)
        if step.rejected or step.accepted != ((request_id,) if enabled else ()):
            raise AssertionError("unexpected W3 action rejection or acceptance")
        world = step.world

    for rnd in range(rounds):
        delivered_now = 0
        for item in tuple(channel):
            due, outcome = item
            if due == rnd:
                delivered_now += int(a.receive(outcome, rnd))
                channel.remove(item)
        delivered += delivered_now
        recovered_now = a.reconcile(world, rnd) if mode == "reconcile" and rnd % 3 == 0 else 0
        expired_now = a.expire_without_evidence(rnd) if mode == "unsafe_timeout" else 0
        expired += expired_now
        give = a.choose(rnd, dict(world.balances)["A"])
        commit("A", "B", f"gift-{rnd}", give)
        if give:
            a.budget.accepted(rnd)
            true_peak = max(true_peak, sent-returned+1)
            sent += 1
        give_back = b.choose_return(gift_received=give, round_index=rnd)
        commit("B", "A", f"return-{rnd}", give_back)
        returned += int(give_back)
        notice = "none"
        if give:
            receipt = find_return_receipt(world, rnd)
            # The host observed the completed recipient phase. A cannot query
            # B's hidden policy or learn an outcome after an unmade gift.
            outcome = receipt if receipt is not None else Outcome(rnd, False)
            if drop_every and (rnd+1) % drop_every == 0:
                dropped += 1
                notice = "dropped"
            elif delay:
                channel.append((rnd+delay, outcome))
                notice = f"due-round-{rnd+delay+1}"
            else:
                delivered_now += int(a.receive(outcome, rnd))
                delivered += 1
                notice = "delivered"
        actual_loss = sent-returned  # Evaluator-only; never a policy input.
        if a.budget.exposure > CAP or (mode != "unsafe_timeout" and true_peak > CAP):
            raise AssertionError("safe simulation exposure invariant failed")
        trace.append({"round": rnd+1, "gift": give, "return": give_back,
                      "notification": notice, "delivered": delivered_now,
                      "recovered_receipts": recovered_now, "timeout_releases": expired_now,
                      "known_loss": a.budget.known_bad, "pending": len(a.budget.pending),
                      "booked_exposure": a.budget.exposure, "actual_loss": actual_loss,
                      "balances": dict(world.balances)})
    if not verify_replay(genesis, world) or sum(dict(world.balances).values()) != 8:
        raise AssertionError("world replay or resource conservation failed")
    if any(e.provenance != "SIMULATED" for e in world.events):
        raise AssertionError("non-simulated event")
    if a.observations != delivered+a.reconciled:
        raise AssertionError("fabricated or duplicated policy observation")
    return {"schema": "openworld.two-agents.receipts.v0", "mode": mode,
            "scenario": scenario, "agents": ["A", "B"], "rounds": rounds,
            "drop_every": drop_every, "delay": delay, "recover_at": recover_at,
            "sent": sent, "returned": returned, "actual_loss": sent-returned,
            "peak_actual_loss_plus_inflight": true_peak,
            "peak_booked_exposure": a.budget.peak_exposure,
            "pending": len(a.budget.pending), "known_loss": a.budget.known_bad,
            "dropped_notifications": dropped, "delivered_observations": delivered,
            "recovered_receipts": a.reconciled, "policy_observations": a.observations,
            "duplicates_ignored": a.duplicates, "unsafe_releases": expired,
            "replay_verified": True, "balances": dict(world.balances),
            "genesis": asdict(genesis), "journal": [asdict(t) for t in world.journal],
            "events": [asdict(e) for e in world.events],
            "final_fingerprint": world.fingerprint(), "trace": trace}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("compare",)+MODES, default="compare")
    parser.add_argument("--scenario", choices=SCENARIOS, default="cooperative")
    parser.add_argument("--rounds", type=int, default=20)
    parser.add_argument("--drop-every", type=int, default=2, help="0 keeps every notification")
    parser.add_argument("--delay", type=int, choices=(0, 1, 2), default=1)
    parser.add_argument("--recover-at", type=int, default=10, help="zero-based recovery round")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit complete traces as JSON")
    parser.add_argument("--out", type=Path, help="also save complete evidence as JSON")
    args = parser.parse_args()
    try:
        results = [simulate(mode=mode, scenario=args.scenario, rounds=args.rounds,
                           drop_every=args.drop_every, delay=args.delay,
                           recover_at=args.recover_at, seed=args.seed)
                   for mode in (MODES if args.mode == "compare" else (args.mode,))]
    except ValueError as exc:
        parser.error(str(exc))
    output = json.dumps(results, indent=2, sort_keys=True)+"\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    if args.json:
        print(output, end="")
        return
    print("Two scripted agents | A sends, B returns/keeps | SIMULATED, same owner")
    print("Actual loss is evaluator-only. Transfers settle immediately; notices may be lost.")
    for result in results:
        print(f"\n[{result['mode']}] partner={result['scenario']}")
        if not args.summary_only:
            for row in result["trace"]:
                print(f"round {row['round']:02d} | A->B={int(row['gift'])} "
                      f"B->A={int(row['return'])} | notice={row['notification']} "
                      f"delivered={row['delivered']} receipts={row['recovered_receipts']} "
                      f"expired={row['timeout_releases']} | booked={row['booked_exposure']}/4 "
                      f"pending={row['pending']} | actual_loss={row['actual_loss']}")
        print(f"sent={result['sent']} returned={result['returned']} "
              f"actual_loss={result['actual_loss']} pending={result['pending']} "
              f"recovered_receipts={result['recovered_receipts']} "
              f"peak_actual_exposure={result['peak_actual_loss_plus_inflight']} "
              f"replay=PASS")
        if result["peak_actual_loss_plus_inflight"] > CAP:
            print("UNSAFE CONTROL: actual exposure exceeded 4 despite the internal counter.")


if __name__ == "__main__":
    main()
