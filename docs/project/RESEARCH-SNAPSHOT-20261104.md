# OpenWorld — Research snapshot, 2026-11-04

This dated snapshot supplements the historical continuity documents. It does
not rewrite their original evidence or promote proposals to accepted interfaces.

## Repository and reproducible state

- Current owner repository: [iamphan04/OpenWorld](https://github.com/iamphan04/OpenWorld),
  a public fork of [CocAgent/OpenWorld](https://github.com/CocAgent/OpenWorld).
  The upstream links in earlier documents remain historical tracker references.
- Inspected main: `6daaea93abb3aa81391bac3c1192f7c4bb973c46`, last pushed
  2026-10-29. No open issues or pull requests were returned for the owner's
  fork when inspected on 2026-11-04. Upstream gate acceptance was not re-ratified.
- Local research branch: `research/p7-budget-feedback-20261104`.
  Portability source `75a2119`; P7 measured source
  `f644615e3a77c4eac88915aed9e6daf7af4e7f72`.
- [Current measured results](../evaluation/P7-HOLDOUT-RESULTS-20261104.md):
  462 tests, zero unexpected failures, six skips, two preserved expected
  security failures, plus a fresh 960-case P7 holdout and complete source digests.

## What is implemented

The repository contains a CPU-only experimental toolkit: exact and predictive
memory, finite stochastic kernels, replayable sparse-agent worlds, population
links, scoped capability references, SQLite transaction/checkpoint fixtures,
an optional PostgreSQL control-plane pilot and P1–P6 synthetic research. A full
model-serving router, production personal agent and distributed agent society
remain architectural/product goals.

Useful design strengths are the separation of exact evidence from predictions,
identity from shared model weights, and trusted execution from experimental
policies. Existing tests exercise replay, conservation, stale and duplicate
requests, revocation, tampering and rollback. These remain bounded reference
tests rather than operational or external-trust certification.

## Findings that determine the next direction

1. P4 does not establish a default advantage for ECF sketches; representation
   pooling and state fragmentation remain relevant confounds. More elaborate
   mathematics should follow a demonstrated task benefit over simple summaries.
2. P6 random probes and its short change-point pause do not establish stable
   superiority. The pause also overlaps with the recent-outcome reliability
   threshold; a separate calibrated detection experiment is required.
3. P6's four-unit cap has two different blockers: unresolved receipts and
   permanent confirmed losses. Four confirmed losses are an absorbing state
   under the current rule. Additional detector complexity cannot observe a
   recovery if every new action is prohibited.
4. P7 now demonstrates that exact positive receipt reconciliation can remove
   notification-induced lockup without breaching the tested cap. It also
   records increased mixed-partner losses and failure to undo permanent budget
   exhaustion. The result supports a mechanism, not a universal policy winner.

## Prioritized research sequence

| Priority | Bounded study | Evidence required before advancing |
|---|---|---|
| Completed here | P7 receipt reconciliation | Fixed protocol, unseen seeds, unsafe timeout control, full raw matrix, negative results |
| Next W3/W5 proposal | Durable reservation and receipt state | Restart/duplicate tests, exact origin association, no double release, failures between accepted action and budget update |
| Next W2/W5 proposal | Budget-aware late exploration | Same cap, hidden recovery times, fixed/seeded/late-reserve comparators, depletion versus unavailable observations, seed-cluster uncertainty |
| Then W1/W5 | Task-relative memory value | Equal-budget simple baselines, decision loss plus exact-history availability and CPU/disk/WAL costs |
| Later W3 | Stateful/adaptive partner generalization | Held-out partner families, no future information, explicit adaptation and distribution-shift controls |
| Before real-user deployment | Independent durable witness and atomic authorization/effects | Reviewed identity/consent design, retention/deletion, fault/security acceptance and actual operating evidence |

Changing shared runtime contracts requires an ADR and compatibility review.
No new approval of federation, cross-owner memory sharing, live user data,
autonomous code mutation, paid infrastructure or production deployment is
implied by this research sequence.

## Continuation instructions

Start with this snapshot and the [P7 result report](../evaluation/P7-HOLDOUT-RESULTS-20261104.md),
then re-check actual GitHub refs and local changes. Preserve the historical
source register and both existing expected security failures. Treat literature,
proposed design, committed source, measured simulation and deployed behavior as
different evidence levels. Retain all unfavorable per-seed cases.
