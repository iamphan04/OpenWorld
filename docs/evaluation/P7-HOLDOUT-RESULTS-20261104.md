# P7 — Measured receipt-reconciliation results

**Measured source:** `f644615e3a77c4eac88915aed9e6daf7af4e7f72`, based on
`iamphan04/OpenWorld` main `6daaea93abb3aa81391bac3c1192f7c4bb973c46`.
**Date:** 2026-11-04, Asia/Saigon. **Scope:** synthetic, same-owner, immediate
W3 settlement; policy notifications alone may be delayed or lost.

The [frozen protocol](P7-RECEIPT-RECONCILIATION-PROTOCOL.md) isolates missing
receipt information from permanent budget depletion. It does not introduce a
new learning policy, permission system or production safety claim.

## Evidence and execution

- [Complete 960-case holdout JSON](../../research/runs/2026-11-04/p7-holdout.json)
  includes 10 unseen seeds 21101–21110, all four policies, four partner regimes,
  two notification channels and three reconciliation modes. It contains 71
  source/protocol/test digests and all 32 paired seed-bootstrap summaries.
- [192-case development output](../../research/runs/2026-11-04/p7-development.json)
  uses separate seeds 11101–11102. It was run before the holdout. Its source
  revision identifies the original baseline plus working-file digests; the
  holdout identifies the committed source above. No policy parameters changed
  after examining the holdout.
- [Full local test log](../../research/runs/2026-11-04/final-tests.log): **462
  tests run in 101.144 seconds, no unexpected failures, six skips and two
  expected security failures**. Nine P7 tests check absorbing loss budgets,
  positive receipt recovery, hostile controls, timeout breach, immediate
  feedback equivalence, abstention, split separation and invalid modes.
- [Initial baseline log](../../research/runs/2026-11-04/baseline-tests.log):
  407 discovered tests, 17 errors, six skips and one expected failure. Four
  benchmark modules imported Unix-only `resource`; SQLite handles in backup
  and test contexts remained open on Windows. The portability commit
  `75a2119` makes optional RSS unavailable/null on Windows and closes handles
  while preserving transaction behavior. The subsequent increase in test
  count includes suites previously blocked at import time.
- Environment: Python **3.14.7**, SQLite **3.53.4**, Windows 11 build 26200,
  eight reported CPUs. P7 holdout measured **15.252 seconds wall** and
  **15.094 seconds process CPU** while the full test suite also ran. These are
  local costs, not isolated latency or throughput measurements. P7 did not
  collect peak RSS; no memory-capacity claim is supported.
- Layout check, Python compilation and whitespace validation passed. One
  PostgreSQL live test and five Bash runner checks were skipped; live
  PostgreSQL parity was not established.

## Results

All **640 notification-only or exact-receipt cases** stayed at or below the
four-unit per-donor actual-loss-plus-current-in-flight bound. The unsafe
timeout arm exceeded that bound in **90 of 320 cases**, reaching **8** despite
its internal policy exposure counter remaining at most four.

For delayed/censored notifications, mean reward per donor decision was:

| Policy | Partner | Notification only | Exact receipts | Unsafe timeout |
|---|---|---:|---:|---:|
| always_offer | cooperative | 0.542100 | 0.600000 | 0.600000 |
| always_offer | hostile | -0.050000 | -0.050000 | -0.057625 |
| always_offer | recovery | -0.050000 | -0.050000 | -0.057625 |
| always_offer | mixed | 0.066675 | 0.073300 | 0.081750 |
| fixed_probe | cooperative | 0.542100 | 0.600000 | 0.600000 |
| fixed_probe | hostile | -0.050000 | -0.050000 | -0.057125 |
| fixed_probe | recovery | -0.024550 | -0.022450 | -0.008500 |
| fixed_probe | mixed | 0.057150 | 0.061600 | 0.068475 |
| random_probe | cooperative | 0.542100 | 0.600000 | 0.600000 |
| random_probe | hostile | -0.049625 | -0.049625 | -0.056000 |
| random_probe | recovery | -0.031550 | -0.029450 | -0.021175 |
| random_probe | mixed | 0.053200 | 0.061200 | 0.064725 |

Hold earns zero throughout. The full raw matrix also retains immediate
feedback and all individual seeds; the [summary JSON](../../research/runs/2026-11-04/p7-summary.json)
adds mean unresolved reservations and transfer counts.

### Positive result with a narrow interpretation

Under cooperative partners, exact receipts recover the full **0.6000** reward
from **0.5421**, a paired difference **+0.0579** (10-seed descriptive bootstrap
95% interval **[0.0414, 0.0735]**). Mean accepted donations rise from **180.7 to
200** per case. All three transferring policies behave identically in this
condition; they are not three independent replications.

Across the matrix, reconciliation recovered **1,828 unique positive receipts**
through **4,844 lookups** and **516,072 event inspections**. Its aggregated
process-clock measurement was **0.046875 seconds**, with coarse Windows timing
resolution. This repeated full-event scan is deliberately simple and is not
evidence of scalable indexing. Missing end-of-horizon notifications remain
reserved; there is no hidden final reconciliation after round 19.

### Negative results and limits

- Once four confirmed losses consume a donor's budget, reconciliation cannot
  create a new probing allowance. With always_offer, hostile and recovery
  reward both remain **-0.0500**. Under delayed recovery, **29 of 30** reconciled
  cases across transferring policies still have negative reward.
- Under delayed mixed partners, reconciliation permits more interaction and
  increases total actual losses across policies from **1,027 to 1,136** while
  respecting the per-donor cap. Each transferring policy loses reward on
  **3 of 10** seeds relative to notification-only feedback. Mean improvement
  does not mean lower realized loss or a universal benefit.
- The always_offer/mixed difference is **+0.006625**, with descriptive interval
  **[0.000125, 0.013]**. Intervals are unadjusted across 32 comparisons and
  should not be used to select a default policy.
- Timeout release can improve apparent cooperative or mixed reward while
  violating the true exposure bound. A low internal counter is insufficient
  evidence that outstanding risk was discharged.
- Actual W3 settlement is immediate. This experiment does not test delayed
  settlement, crashes, concurrent budget reservations, independent ownership,
  durable identity, calibrated change detection or strategic learning partners.

## Independent consistency review

A separate read-only review recomputed all 32 paired means and deterministic
bootstrap intervals, verified the 960 unique cells, disjoint seed splits,
identical starting worlds per seed, source digests, observation accounting,
receipt uniqueness and timing. Every case reports a verified replay and 40
ticks. All **160 immediate-feedback pairs** have identical rewards, final
world hashes, transfers and policy observations between exact and baseline
modes; no reconciliation receipts are needed there.

Raw JSON stores receipt digests, not full event traces. Positive-event matching
and replay are established by the reviewed implementation and executable tests;
the raw JSON alone cannot independently authenticate an event or reconstruct
the entire world. No outside-world observation is inferred.

## Decision and next gate

The supported research direction is **evidence-backed reconciliation plus
explicit budget availability**, before adding a more elaborate population
encoder or claiming superior change detection. Keep exact evidence, policy
beliefs, permanent losses and unresolved reservations distinct.

A next W3/W5 study should test persistent reservation/receipt state with
restart, duplicate delivery and failure between world acceptance and budget
reservation. Introduce genuinely delayed settlement only with an explicit
versioned design and W0/W3/W4 review. Separately test whether preserving a late
probe allowance helps unknown recovery times; keep the same total cap and
measure the opportunity cost. Neither proposal is implemented by P7.

The two existing security expected-failure controls remain unresolved: restoring
an old SEC-002 grant backup can revive authority, and authorization consumption
plus a downstream world effect lacks one atomic boundary. Do not onboard real
users or call the current reference production ready on the basis of this run.

**Rollback:** revert the optional P7 source commit `f644615` and remove its
reports/raw output. The Windows portability fix can be retained independently;
there is no migration or deployed service.
