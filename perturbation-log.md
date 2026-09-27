# Perturbation Log

This log records deliberate changes made to the three systems and the observed contrast with the unperturbed behavior.

## System 1 — Policy extraction and routing

**Deliberate change:** Set the required `premium_amount` extraction field to `None`.

**Command/evidence run:** The retry test was exercised with:
```bash
.venv/bin/pytest tests/test_us01_retry.py -v
```
A separate controlled perturbation run was saved in `perturbation/own-perturbation.txt`.

**Observed result:** `RetryFutileEscalation` was returned for `premium_amount`, with `detected_pattern='premium_amount_absent'`, and the controlled result recorded **1 API call**. The system treated the missing source field as a condition where retrying is futile.

**Unperturbed contrast:** In the routing evidence, a populated high-confidence record was routed to `auto_approve`, while the low-confidence `premium_amount` record was routed to `human_review`. Evidence: `01-policy-pipeline/routing_decisions.json`.

**Artifacts:** `01-policy-pipeline/perturbation/own-perturbation.txt`, `01-policy-pipeline/perturbation/retry-perturbation.txt`, `01-policy-pipeline/routing_decisions.json`.

## System 2 — Mortgage mathematical consistency

**Deliberate change:** Keep the calculated monthly income at `9642.17` but change only the document-stated total from `9642.17` to `10892.17`.

**Command/evidence run:** The controlled validator execution is recorded in `02-mortgage-extraction/perturbation/own-perturbation.txt`.

**Observed result:** Baseline returned `consistent=True`. After the perturbation, validation returned `consistent=False` with:
- field: `total_monthly_income`
- calculated: `9642.17`
- stated: `10892.17`
- delta: `-1250.0`

**Unperturbed contrast:** The clean appraisal replay and the normal validator behavior are recorded in `02-mortgage-extraction/extract-run.txt`; the document-level mismatch contrast is in `02-mortgage-extraction/discrepancy-run.txt`.

**Artifacts:** `02-mortgage-extraction/perturbation/own-perturbation.txt`, `02-mortgage-extraction/extract-run.txt`, `02-mortgage-extraction/discrepancy-run.txt`, `02-mortgage-extraction/perturbation/comparison.txt`.

## System 3 — Supply-chain resilient coordination

**Deliberate change:** Simulate a logistics-source timeout with:
```bash
.venv/bin/supply-chain-investigate meridian --offline --simulate-timeout
```

**Observed result:** The run completed and recorded `logistics unavailable (timeout)`. The late-shipment finding became incomplete, while evidence still available from the supplier-audit source was retained. The normal source conflict section did not appear because the logistics evidence was unavailable.

**Unperturbed contrast:** The normal offline investigation retained both `95.0%` and `78.0%` on-time delivery values as a contested, high-impact conflict and separately marked production-capacity utilization as incomplete. Evidence: `03-supply-chain/investigation-run.txt`.

**Artifacts:** `03-supply-chain/timeout-run.txt`, `03-supply-chain/investigation-run.txt`, `03-supply-chain/perturbation/timeout-comparison.txt`, `03-supply-chain/briefing.md`.

## Overall perturbation lesson

The three perturbations target different failure modes: missing evidence, contradictory arithmetic, and source unavailability. In each case, the system produced an observable state change instead of silently preserving the happy-path result. That behavior is the main reliability evidence captured by this submission.
