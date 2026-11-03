# OpenWorld

**An open ecosystem for adaptive, collaborative, and evolving AI agents.**

OpenWorld is an independent, experimental open-source project exploring persistent agent identity, auditable memory, online adaptation, resource-aware reasoning, and collaboration. It is **not production ready**.

## Core components

| Component | Responsibility |
|---|---|
| **SuperKernel** | Agent lifecycle, policy, tools, budgets, and scheduling |
| **HyperMemory** | Exact historical evidence plus compact predictive memory |
| **MathKernel** | Stochastic processes, Bayesian learning, predictive state, information theory |
| **World Runtime** | Reproducible environments, event queues, sparse social interactions |
| **Open Protocols** | Capability-based interoperability and trusted interfaces |

An agent identity is **not** a dedicated foundation model. Agents may share inference engines while retaining separate memories, permissions, and histories.

## Getting started

Requires Python 3.11+; no GPU, model key, or paid GitHub Actions.

```bash
python -m unittest discover -s tests -v
python scripts/check_repository.py
```

See [Architecture](docs/ARCHITECTURE.md), [Workstreams](docs/WORKSTREAMS.md), [Roadmap](docs/ROADMAP.md), [Research limitations](research/RESEARCH-STATUS.md), and [Contributing](CONTRIBUTING.md).

## Research foundations and related projects

The [curated research map](docs/research/RELATED-RESEARCH-AND-PROJECTS.md) includes **16 foundational papers** plus newer and specialized references on applied category theory, Markov categories, POSGs, multi-agent environments, generative societies, quality-diversity and co-evolution, plus candidate open-source implementations. It maps each publication to a falsifiable OpenWorld experiment and clearly distinguishes prior art from OpenWorld outcomes.

The [October 2026 session synthesis](docs/project/SESSION-SYNTHESIS-20261028.md) reconciles the owner-supplied design iterations: an open strategic game, local-first community worlds, agent genesis, the trusted SuperKernel and optional compositional mathematics. **OpenWorld** is the canonical project name; "Open Civilization Protocol" (OCP) and "OpenWorld Protocol" (OWP) remain unratified design labels. Neither social evolution nor federation is a shipped feature.

## Population learning and agent genome — research proposal

The [population representation and typed agent-DNA design](docs/research/POPULATION-REPRESENTATION-AND-AGENT-DNA.md) assesses mean-field MARL, empirical characteristic functions, kernel mean embeddings, the owner's QID/FQID references, and why neither Riemann nor quantum computing is a prerequisite. The optional [Python research fixture](src/openworld_superkernel/population_repr.py) implements a **lossy group distribution sketch** and an **immutable content-addressed genome blueprint**, not learned intelligence, identity, permissions or a production protocol. See [session synthesis addendum](docs/project/SESSION-SYNTHESIS-20261028.md#7-october-29-2026--population-learning-and-mathematical-representation-refinement).

~~~sh
python -m unittest discover -s tests -p 'test_population_repr.py' -v
~~~

## W5 population representation benchmark (experimental)

[Issue #44](https://github.com/CocAgent/OpenWorld/issues/44) evaluates whether simple aggregate means and histograms are sufficient, or whether [empirical characteristic functions and random Fourier features](docs/evaluation/W5-POPULATION-REPRESENTATION-BASELINES.md) improve task-specific predictions under matching synthetic train/holdout seeds. The benchmark is **supervised synthetic regression only**, not learned multi-agent RL or proof of population scalability.

Run the bounded [W5 benchmark](benchmarks/w5_population_repr.py) on a local CPU to generate raw JSON evidence. Neither ECF nor Agent Genome is a privileged identity, trusted history or default world-state API.

## P1 — Online population-agent learning (research)

The [P1 learning study](docs/evaluation/P1-THIRTY-AGENT-ONLINE-LEARNING.md) extends the earlier [W5 distribution benchmark](docs/evaluation/W5-POPULATION-REPRESENTATION-BASELINES.md) from frozen supervised prediction into a **synthetic 30-agent contextual bandit**. Agents select binary actions and update a role-shared policy using only observed chosen-action rewards. No-summary, grouped mean, histogram and empirical characteristic-function summaries are assessed on disjoint world seeds.

This is an **offline learning positive control**, not self-evolving agents, multi-agent world training, proof of societal emergence, trusted authentication or a shipped game.

~~~sh
python -m unittest discover -s tests -p 'test_p1_population_learning.py' -v
python benchmarks/p1_population_learning.py --agents 30 --train-ticks 160 --holdout-ticks 60 --seeds 3
~~~

## W3 P0 — Local population connections (research only)

[Population Links P0](docs/world/W3-POPULATION-LINKS-P0.md) turns the earlier community/world/civilization ideas into one bounded experiment: **three agent groups in one local W3 world**, explicit directional contracts and same-owner, double resource-scoped capability checks. It reuses W3's sparse graph, immutable state, event provenance and deterministic replay. **No cross-owner transfer, federation, group privacy, learned cooperation or automatic institutional creation** is implemented.

```bash
python -m unittest discover -s tests -p 'test_population_links.py' -v
python examples/populations/local_three_groups.py
```

## P3 research — independently learning populations in a replayable world

[P3 mutual learning](docs/evaluation/P3-MUTUAL-LEARNING-W3.md) tests **20 separate donor/recipient learners among 30 registered synthetic agents** over four repeated rounds (eight W3 ticks) per episode. All transfers are simulated under one owner and go through the existing guarded W3 population router; learned policies receive delayed feedback after the recipient's actual action. This is not production MARL, automated institutions or cross-owner federation.

~~~sh
python -m unittest discover -s tests -p 'test_p3_mutual_learning_w3.py' -v
python benchmarks/p3_mutual_learning_w3.py --train-episodes 20 --holdout-episodes 8 --rounds 4 --seeds 3
~~~

## P6 research — bounded exposure and missing feedback

The [P6 exposure-cap experiment](docs/evaluation/P6-EXPOSURE-CAP-AND-CENSORED-FEEDBACK.md) tests a four-unit **per-donor** hard risk bound, seeded and fixed probing, simple change detection, a public-schedule-aware scripted partner, and delayed/censored policy notifications. The [complete 840-case measured results](docs/evaluation/P6-TEN-SEED-RESULTS-REPORT.md) include **negative** outcomes: probing costs money-like toy resources under hostile partners, and seeded probes are not universally better than fixed probes. W3 actions are SIMULATED, single-owner and authorized through the existing guarded router. **No production safety or trust claim.**

```bash
python -m unittest discover -s tests -p 'test_p6_risk_budget.py' -v
python benchmarks/p6_risk_budget.py --seeds 10 --seed-start 10101 --out p6-cases.json
```

## P7 research — exact receipt reconciliation

The [2026-11-04 research snapshot](docs/project/RESEARCH-SNAPSHOT-20261104.md)
reconciles this fork with its historical upstream context. The
[P7 measured report](docs/evaluation/P7-HOLDOUT-RESULTS-20261104.md) evaluates
**960 fresh-seed cases** separating missing policy notifications from permanent
budget exhaustion. Exact positive receipt recovery restores cooperative reward
in the tested fixture, while an unsafe timeout control breaches actual exposure
in 90/320 cases. Reconciliation does not undo confirmed losses or guarantee
improved reward for every partner/seed. All settlement remains immediate,
single-owner and SIMULATED.

```bash
python -m unittest discover -s tests -p 'test_p7_receipt_reconciliation.py' -v
python benchmarks/p7_receipt_reconciliation.py --split holdout --out p7-holdout.json
```

## Experimental compositional world research

[RFC-007: Mathematical Foundations](docs/math/RFC-007-OPENWORLD-MATHEMATICAL-FOUNDATIONS.md) is the existing proposed W2 research architecture. The independent [EXPR-001 fixture](docs/experiments/COMPOSABLE-WORLD-FIXTURE.md), [mathematical notes](docs/math/COMPOSITIONAL-WORLD-NOTES.md), and [dependency-free example](examples/composable_world.py) explore only pure typed composition, agent blueprints and resource transfer/replay. They do **not** constitute approved OWP/OCP standards or production SuperKernel code.

```bash
python -m unittest discover -s tests -p 'test_composable_world_experiment.py' -v
```

## Scientific and safety boundaries

- No claim of billion-agent scalability, universal compression, or human-level intelligence.
- A simulated or inferred memory is never evidence of an observed real-world event.
- External actions and memory sharing require explicit authorization.
- Benchmarks must include actual on-disk cost (including WAL), CPU, accuracy, uncertainty and baselines.
- Historical prototype ZIP files are **not public** pending independent license, secret, security and reproducibility review.

## Language and license

English is the canonical language for code, comments, issues, RFCs and pull requests. New source and documentation are available under [Apache-2.0](LICENSE).

## Project continuity and previous sessions

Start new work sessions with the [canonical project continuity](docs/project/PROJECT-CONTINUITY.md), [decision ledger](docs/project/DECISION-LEDGER.md), [source register](docs/project/SESSION-SOURCE-REGISTER.md), and [execution handoff](docs/project/EXECUTION-HANDOFF.md). Refer to the source register for evidence provenance and verification status.
