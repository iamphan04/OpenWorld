# P7 — Receipt reconciliation versus permanent budget depletion

**Protocol frozen:** 2026-11-04, before the fresh holdout run. Research-only,
single-owner, synthetic CPU experiment. No shared runtime interface changes.

## Question and falsifiable claims

P6 combines confirmed non-returns and unresolved notifications in one four-unit
per-donor exposure cap. These can block actions for different reasons.

1. Periodic recovery of exact, already committed return receipts can reduce
   notification-induced lockup under cooperative partners, without exceeding
   four units of actual loss plus an in-flight donation.
2. Reconciliation cannot restore a budget consumed by four confirmed losses.
   This is an absorbing state under the existing rule, independent of a later
   partner recovery. It must not be scored as a change detector failure.
3. Releasing a reservation on timeout without a receipt can exceed the actual
   loss cap. This is an explicitly unsafe negative control, never a candidate
   default.

## Fixed design

- Existing W3 router, genesis, one-unit transfers, cap 4, 20 rounds/40 ticks,
  30 registered agents and 10 active donors; same P6 reward (-0.25 per donation,
  +0.85 per committed return). No policy learning beyond existing P6 heuristics.
- Policies: hold, always_offer, fixed_probe, random_probe. Partners: cooperative,
  hostile, recovery at round 10, seeded mixed. Existing partner draws and
  notification draws are keyed by world seed, recipient and origin round.
- Feedback: immediate or P6 delayed_censored (delay 1–2 donor rounds and
  deterministic notification loss). Settlement itself remains immediate.
- Modes: notification_only; exact_receipts every third donor round before the
  next decision; unsafe_timeout releases unresolved reservations at age 3.
  Both interventions preserve the original policy threshold and cap check.
- Exact reconciliation releases only a uniquely matched positive SIMULATED
  transfer event for the origin's recipient-to-donor return tick, together
  with its journal action. No return is inferred from balances, timeout,
  an abstention or a missing event. A full final replay must verify.
- This association relies on exactly one transfer per pair per phase and no
  rejected actions in this fixture. It is not a general asynchronous receipt,
  authenticated evidence, cross-owner read permission or production audit API.
- Development seeds: 11101–11102. Fresh holdout seeds: 21101–21110, disjoint
  from development and P6's published 10101–10110. No hyperparameter search or
  policy selection after examining holdout results.

The holdout matrix contains **960 cases**: 10 seeds × 4 policies × 4 partners
× 2 feedback channels × 3 modes. Policies receive only delivered own outcomes
or the mode's explicitly scoped positive receipt. Evaluation-only actual loss
counts and partner regimes are never policy inputs.

## Measurements and gates

Keep every case. Record reward, phase reward, unresolved reservations, known
losses, peak policy exposure, independently counted actual losses plus the
current in-flight unit, cap blocks, receipt lookups/event inspections, receipts
recovered, receipt digests, timeout releases, duplicate notification skips,
and reconciliation/total CPU and wall time. Preserve state at the partner
switch and the first cap-blocked round. Verify replay, resource conservation,
SIMULATED provenance, identical starting worlds and no false receipt releases.

Report exact_receipts minus notification_only paired differences per world
seed. A deterministic 2,000-replicate percentile bootstrap resamples whole
world seeds, never donors or ticks. Intervals are descriptive, unadjusted for
multiple comparisons, and do not establish a universal policy winner.

Safe-mode gate: peak actual exposure <= 4 in every case, zero unmatched receipt
releases and no fabricated observations. Negative-control gate: disclose any
unsafe_timeout case with actual exposure > 4. Keep unfavorable rewards and
hostile/recovery cases. No default policy is promoted even if these gates pass.

## Primary literature and assumption boundaries

- Wu et al., [Conservative Bandits](https://proceedings.mlr.press/v48/wu16.html)
  (ICML 2016): a baseline-performance constraint; its baseline can earn budget
  slack. P6's hold earns zero and does not replenish the loss budget.
- Badanidiyuru, Kleinberg and Slivkins,
  [Bandits with Knapsacks](https://arxiv.org/abs/1305.2545) (FOCS 2013;
  extended version 2017): learning with finite resources motivates measuring
  exhaustion. Its results do not validate this receipt accounting.
- Vernade, Cappe and Perchet,
  [Stochastic Bandit Models for Delayed Conversions](https://proceedings.mlr.press/r15/vernade17a.html)
  (UAI 2017): separates delay and censoring under a known delay law. P6's lost
  notifications use a different observation mechanism.
- Besbes, Gur and Zeevi,
  [Stochastic Multi-Armed-Bandit Problem with Non-stationary Rewards](https://proceedings.nips.cc/paper_files/paper/2014/file/91ba7292e5388b90b58d0b839a7f19ec-Paper.pdf)
  (NeurIPS 2014): explicit reward variation assumptions; no guarantee of
  detecting recovery when no further experiment is permitted.

## Reproduction and rollback

```sh
python -m unittest discover -s tests -p 'test_p7_receipt_reconciliation.py' -v
python benchmarks/p7_receipt_reconciliation.py --split development --out p7-dev.json
python benchmarks/p7_receipt_reconciliation.py --split holdout --out p7-holdout.json
```

Raw output includes source file digests, protocol digest, baseline Git revision,
environment and measured cost. Separate source identity from an evidence commit.
Rollback removes the optional P7 benchmark, tests and documentation; no storage
migration, model calls, paid services, real users or network endpoints.
