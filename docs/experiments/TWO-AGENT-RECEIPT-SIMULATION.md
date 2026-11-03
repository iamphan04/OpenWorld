# Two-agent receipt simulation

This executable example instantiates exactly two scripted agents in the
existing guarded W3 world. It illustrates P7's accounting mechanism without
creating a 30-agent population or requiring a visualization or model service.

## Agents and host responsibilities

- `DonorAgent` A holds its own `DonorBudget`, observations and unresolved
  donation origins. It selects a one-unit gift using its own balance and the
  existing four-unit cap. Evaluator-only actual loss is never a policy input.
- `RecipientAgent` B decides whether to return a gift only after that gift
  commits. Its fixed scenario is cooperative, hostile or recovery after the
  first ten rounds. These are scripted policies, not learned intelligence.
- The trusted same-owner host advances donation and recipient phases through
  `GuardedWorldGateway`. There are exactly two registered W3 identities, A and
  B, initially holding eight and zero resource units, respectively.
- The notification channel may delay or drop outcomes. Resource settlement
  itself is immediate. A learns no outcome for a donation it did not make.

## Three donor modes

| Mode | Behavior |
|---|---|
| `notifications` | Consume delivered notifications only; missing outcomes stay reserved |
| `reconcile` | Also check existing exact positive return receipts every third round |
| `unsafe_timeout` | Release unresolved reservations at age three without evidence; intentionally unsafe control |

Receipt recovery matches a recipient-to-donor journal action and a positive
SIMULATED transfer event for the exact originating round. A missing event does
not create success or learning feedback. Duplicate notifications after receipt
recovery cannot release a reservation twice. This association assumes one gift
and one possible return per pair per round. It is not an asynchronous receipt
protocol or an independently authenticated consent system.

## Run locally

From the repository root, with Python 3.11+ and no additional dependencies:

```bash
python examples/two_agents.py
python examples/two_agents.py --scenario hostile --summary-only
python examples/two_agents.py --scenario recovery --summary-only
python examples/two_agents.py --mode reconcile --out two-agents.json
python examples/two_agents.py --drop-every 0 --delay 0 --summary-only
python -m unittest discover -s tests -p test_two_agents.py -v
```

The default compares all three modes over 20 rounds, delays retained notices
by one round and drops every second round's notice. `--drop-every 0` disables
dropping. `--delay` accepts zero, one or two rounds; no outcome still in flight
at the end is silently flushed. `--recover-at 10` means B begins cooperating
at displayed round 11. Rounds are bounded to 1–20, matching the existing budget
fixture's horizon. The seed identifies the initial W3 world; this example's
notification schedule is deterministic, not a randomized benchmark.

Console fields distinguish actual gifts/returns, queued or dropped notices,
delivered observations, recovered receipts, unsafe timeout releases, booked
exposure and evaluator-only actual loss. Use `--json` for machine-readable
output, or `--out` to retain the complete trace, genesis, journal, event digests,
balances and final world fingerprint. Bearer grants and signing keys are not
exported. Every run verifies exact W3 replay and resource conservation.

## Default observed behavior

| Partner | Notifications: sent / returned / lost | Reconcile: sent / returned / lost | Unsafe timeout: sent / returned / lost |
|---|---|---|---|
| Cooperative | 8 / 8 / 0 | 20 / 20 / 0 | 20 / 20 / 0 |
| Hostile | 4 / 0 / 4 | 4 / 0 / 4 | 6 / 0 / 6 |
| Recovery | 4 / 0 / 4 | 4 / 0 / 4 | 6 / 0 / 6 |

All transfers are synthetic and all identities have one owner. In the
cooperative baseline, four unresolved notices exhaust the booked allowance
despite zero actual loss. Positive receipts restore activity. Under hostility,
receipt recovery cannot erase losses. The timeout control loses six units even
though its internal booked exposure never exceeds four. Once the entire loss
budget has been consumed, B's later recovery cannot create a fresh probe.

These are deterministic illustrative cases, distinct from P7's measured
960-case population experiment. No runtime interfaces or security guarantees
are added. Known upstream authorization/rollback gaps remain unchanged.

## Validation and rollback

`tests/test_two_agents.py` covers causal observations, exactly two identities,
missing notifications, hostile caps, unsafe timeout, permanent budget
depletion, duplicate delivery, missing event evidence, JSON export/replay and
CLI/input validation. Execution evidence is stored under
[`research/runs/2026-11-04/two-agents/`](../../research/runs/2026-11-04/two-agents/).

Rollback removes the optional example, its tests, documentation, README section
and recorded runs. No storage migration, external service, paid dependency or
change to a shared `src/openworld_superkernel` contract is required.
