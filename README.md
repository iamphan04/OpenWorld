# OpenWorld

**A local research toolkit for agents that remember, adapt and cooperate.**

OpenWorld explores how persistent AI agents can keep auditable memories, learn from interactions and collaborate within explicit resource limits. The long-term goal is an open agent ecosystem; the current implementation is a **CPU-only experimental Python toolkit** with reproducible synthetic worlds and benchmarks.

An agent has its own identity, history, state and permissions. Many agents can share the same inference engine. A separate foundation model for every agent is not required.

**Status:** research prototype, not production ready. The included experiments run without a GPU, model API key or paid service.

## Start here

Requires **Python 3.11+**. The default tests and examples use the Python standard library. The optional live PostgreSQL pilot has separate setup requirements.

```bash
git clone https://github.com/iamphan04/OpenWorld.git
cd OpenWorld

# Run a small replayable world.
python examples/world/demo.py --agents 30 --ticks 20

# Check the repository and run the test suite.
python scripts/check_repository.py
python -m unittest discover -s tests -v
```

For a same-owner, three-population exchange example:

```bash
python examples/populations/local_three_groups.py
```

Run commands from the repository root. These examples use simulated agents and events; they do not call a language model or connect to other owners' worlds.

## What is implemented

| Area | Current research implementation | Longer-term goal |
|---|---|---|
| HyperMemory | Exact event records, compact predictors, online adaptation and SQLite experiments | Task-aware memory with measured quality and cost |
| MathKernel | Finite stochastic kernels, belief updates and population representation experiments | Formal, testable models of agent decisions |
| World Runtime | Sparse interactions, resource transfers, deterministic replay and checkpoints | Persistent environments with reliable scheduling |
| Trust and protocols | Scoped capability, revocation, transaction and rollback reference implementations | Reviewed identity, consent and interoperability |
| Evaluation | P1-P7 learning/cooperation studies and W5 storage, memory and recovery benchmarks | Reproducible evidence before expanding scope |

**SuperKernel** is the overarching architecture for lifecycle, policy, tools, budgets and scheduling. A complete production kernel, shared-model serving system, autonomous society and federated world network are still future work. See the [architecture](docs/ARCHITECTURE.md) and [roadmap](docs/ROADMAP.md).

## Latest study: recover evidence before spending more risk

An agent sends a resource to a partner. The partner returns it, but the notification is lost. The agent may keep that transfer reserved against its risk limit and eventually stop interacting despite successful returns.

**P7 tests whether the agent can recover from this situation by checking exact, already committed return receipts.** It compares notification-only feedback, periodic receipt reconciliation and an intentionally unsafe timeout-release control. A timeout alone provides no evidence that a resource was returned.

The [2026-11-04 measured report](docs/evaluation/P7-HOLDOUT-RESULTS-20261104.md) records **960 cases on 10 fresh world seeds**, with four policies, four partner regimes, two feedback channels and three reconciliation modes.

| Finding | Measured result |
|---|---|
| Cooperative partners with delayed/lost notifications | Mean reward per donor decision increased from **0.5421 to 0.6000** with exact receipts |
| Notification-only and exact-receipt modes | **640/640 cases** respected the four-unit per-donor exposure bound |
| Unsafe timeout-release control | **90/320 cases** exceeded the actual bound, reaching eight units |
| Budget already consumed by confirmed losses | Reconciliation could not restore that budget |
| Mixed partner behavior | Reconciliation improved mean reward but lost reward on **3/10 seeds** for each transferring policy |

These are artificial rewards in a single-owner simulation. W3 transfers settle immediately; only notifications are delayed or lost. The result supports evidence-backed reconciliation within this fixture, not a universal cooperation policy or production safety guarantee.

Reproduce the study:

```bash
python -m unittest discover -s tests -p test_p7_receipt_reconciliation.py -v
python benchmarks/p7_receipt_reconciliation.py --split development --out p7-development.json
python benchmarks/p7_receipt_reconciliation.py --split holdout --out p7-holdout.json
```

See the [frozen protocol](docs/evaluation/P7-RECEIPT-RECONCILIATION-PROTOCOL.md), [complete raw holdout](research/runs/2026-11-04/p7-holdout.json) and [validation record](research/runs/2026-11-04/validation.json). The report identifies the exact measured source commit; later documentation commits are separate.

## Research progression

Each study answers a bounded question. Synthetic results do not establish real-world intelligence, societal emergence or large-scale deployment capacity.

| Study | Question and evidence |
|---|---|
| W5 population representations | Do means, histograms or distribution sketches preserve useful information? [Baseline study](docs/evaluation/W5-POPULATION-REPRESENTATION-BASELINES.md) |
| P1 | Can a synthetic 30-agent contextual bandit learn from chosen-action rewards? [Study](docs/evaluation/P1-THIRTY-AGENT-ONLINE-LEARNING.md) |
| P2 | How does stateful cooperation change learning inside a replayable world? [Study](docs/evaluation/P2-STATEFUL-COOPERATION-EXPERIMENT.md) |
| P3 | What happens when donor and recipient policies learn separately? [Study](docs/evaluation/P3-MUTUAL-LEARNING-W3.md) |
| P4 | Which representations help sample efficiency under partner shifts? [Results](docs/evaluation/P4-FIVE-SEED-RESULTS-REPORT.md) |
| P5 | What is the reward/loss trade-off of abstention and probing? [Results](docs/evaluation/P5-FIVE-SEED-RESULTS-REPORT.md) |
| P6 | Can a hard exposure cap coexist with missing feedback? [840-case results](docs/evaluation/P6-TEN-SEED-RESULTS-REPORT.md) |
| P7 | Can exact receipts reduce notification-induced lockup? [960-case results](docs/evaluation/P7-HOLDOUT-RESULTS-20261104.md) |

The [primary literature map](docs/research/RELATED-RESEARCH-AND-PROJECTS.md) connects earlier research to testable OpenWorld questions. Further proposals cover [population representations and agent genomes](docs/research/POPULATION-REPRESENTATION-AND-AGENT-DNA.md), [compositional worlds](docs/experiments/COMPOSABLE-WORLD-FIXTURE.md) and [mathematical foundations](docs/math/RFC-007-OPENWORLD-MATHEMATICAL-FOUNDATIONS.md). Their proposed scope is distinct from the implemented experiments.

## Validation and known limits

The **2026-11-04 Windows checkpoint** ran **462 tests with zero unexpected failures**, six skips and two expected security failures. Its environment was Python 3.14.7 and SQLite 3.53.4. The [full log](research/runs/2026-11-04/final-tests.log) and [measured report](docs/evaluation/P7-HOLDOUT-RESULTS-20261104.md) preserve the details.

- The two expected failures document unresolved authority rollback and atomicity gaps: restoring an old grant backup can revive authority, and authorization consumption plus its downstream world effect lacks one atomic boundary.
- One live PostgreSQL test and five Bash runner checks were skipped. That checkpoint does not establish live PostgreSQL parity.
- Exact historical evidence stays separate from predictions and simulated replay. Generated content cannot establish that an outside-world event happened.
- Cross-owner access and consequential external actions require explicit authorization. The included same-owner fixtures do not establish independent bilateral consent.
- Population counts do not measure concurrent model inference. Billion-agent capacity, universal memory compression and general intelligence are not demonstrated.
- Historical prototype archives remain excluded pending rights, secrets, security and reproducibility review.

## Next research steps

1. Persist budgets and receipts, then test restart, duplicate delivery and failure between accepting a transfer and recording its reservation.
2. Compare ways to preserve a late probing allowance under the same total cap and unknown partner recovery times.
3. Measure memory's decision benefit alongside exact-history availability, CPU, disk and SQLite WAL costs.
4. Evaluate unfamiliar adaptive partners before expanding toward distributed or federated worlds.

These are proposed studies. Shared runtime changes require architecture and compatibility review. See the [current research snapshot](docs/project/RESEARCH-SNAPSHOT-20261104.md) and [research status](research/RESEARCH-STATUS.md).

## Repository guide

- [`src/openworld_superkernel/`](src/openworld_superkernel/): reference implementations.
- [`benchmarks/`](benchmarks/): repeatable synthetic experiments.
- [`tests/`](tests/): invariant, failure and integration checks.
- [`examples/`](examples/): runnable local demonstrations.
- [`docs/`](docs/): architecture, protocols, decisions and experiment reports.
- [`research/`](research/): research status and recorded execution evidence.

This repository is [iamphan04/OpenWorld](https://github.com/iamphan04/OpenWorld), a fork of [CocAgent/OpenWorld](https://github.com/CocAgent/OpenWorld). Older issue and PR links refer to that upstream history. Start future sessions with the [current snapshot](docs/project/RESEARCH-SNAPSHOT-20261104.md), [continuity](docs/project/PROJECT-CONTINUITY.md), [decision ledger](docs/project/DECISION-LEDGER.md), [source register](docs/project/SESSION-SOURCE-REGISTER.md) and [handoff](docs/project/EXECUTION-HANDOFF.md).

## Contributing and license

Public documentation, code comments, issues and pull requests use **English**. Contributions should include assumptions, baselines, seeds, negative findings, reproducible local checks and rollback instructions. See [Contributing](CONTRIBUTING.md), [Workstreams](docs/WORKSTREAMS.md) and [Security](SECURITY.md).

New OpenWorld-authored source and documentation are licensed under [Apache-2.0](LICENSE). Referenced third-party projects and historical materials retain their own rights and review requirements.
