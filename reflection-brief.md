# Evaluation and Observability — Reflection Brief

## System 1 — Validated, Routed Insurance Policy Extraction

The policy system demonstrates reliability through validation, retry classification, and human-in-the-loop routing. The strongest evidence from my run is the routing test: one populated high-confidence record was assigned `auto_approve`, while a record with `premium_amount` confidence of `0.50` was assigned `human_review` because that field was below the routing threshold. This shows that routing is influenced by field-level confidence rather than treating every extraction as equally trustworthy. Evidence: `01-policy-pipeline/routing_decisions.json`, `01-policy-pipeline/perturbation/routing-test.txt`.

The deliberate perturbation set the required `premium_amount` field to `None`. The system returned `RetryFutileEscalation` with `detected_pattern='premium_amount_absent'` after exactly one API call. This is important because retrying cannot recover information that is absent from the source. The system therefore converts a missing-source condition into an explicit escalation instead of repeatedly calling the model. Evidence: `01-policy-pipeline/perturbation/own-perturbation.txt`, `01-policy-pipeline/perturbation/retry-perturbation.txt`.

The calibration results also show why confidence should not be interpreted blindly. The `premium_amount` group had confidence `0.95`, accuracy `1.00`, and Brier score `0.003`, while the `umbrella/exclusions` group had confidence `0.93` but accuracy `0.00` and Brier score `0.865`. The second case is a concrete example of a system appearing highly confident while being wrong on the calibration sample. Evidence: `01-policy-pipeline/calibration-report.txt`.

My full automated test suite passed with 45 tests and 3 API-dependent tests skipped because no `ANTHROPIC_API_KEY` was available. The end-to-end live pipeline therefore could not be completed in this environment; `pipeline-run.txt` records the authentication failure. I did not treat the routing-test artifact as a substitute for a successful live pipeline run. Evidence: `01-policy-pipeline/tests.txt`, `01-policy-pipeline/pipeline-run.txt`.

## System 2 — Resilient Mortgage Document Extraction

The mortgage system separates extraction from mathematical validation. The clean appraisal replay produced a structured result containing the borrower, property information, gross living area, and appraised value, while the income fields were not required for that document type. Evidence: `02-mortgage-extraction/extract-run.txt`.

The system also demonstrates why missing information should remain null rather than being fabricated. In the `income_missing_bonus` replay, `bonus_monthly` remained `null` while the other available values were preserved. The system did not invent a bonus value to complete the calculation. Evidence: `02-mortgage-extraction/missing-bonus-run.txt`.

The deliberate perturbation changed only the stated monthly income total from `9642.17` to `10892.17`, while the calculated total remained `9642.17`. Validation changed from `consistent=True` to `consistent=False` and emitted a discrepancy for `total_monthly_income` with delta `-1250.0`. This demonstrates a useful reliability property: contradictory evidence is surfaced rather than silently corrected. Evidence: `02-mortgage-extraction/perturbation/own-perturbation.txt`.

The document-level mismatch case produced the same type of validation signal: calculated income `9642.17` versus stated income `10892.17`, with the report marked inconsistent. The full test suite passed 25 tests, and both mypy and ruff completed without errors. Evidence: `02-mortgage-extraction/discrepancy-run.txt`, `02-mortgage-extraction/tests.txt`, `02-mortgage-extraction/static-checks.txt`.

## System 3 — Resilient Supply-Chain Multi-Source Synthesis

The supply-chain system explicitly represents agreement, conflict, and incompleteness between sources. In the normal investigation, the on-time delivery rate was reported as `95.0%` by the supplier-audit source and `78.0%` by the logistics source. Rather than choosing one value and discarding the other, the system classified the finding as a contested, high-impact conflict. Production-capacity utilization was separately marked incomplete because the required source was missing. Evidence: `03-supply-chain/investigation-run.txt`, `03-supply-chain/briefing.md`.

The deliberate perturbation simulated a logistics-source timeout. The run completed successfully and reported `logistics unavailable (timeout)`. Findings that depended on that source became incomplete, while information still available from the supplier-audit source was retained. The normal conflict did not appear because one side of the conflicting evidence was unavailable. This is preferable to silently presenting a complete-looking conclusion after a source failure. Evidence: `03-supply-chain/timeout-run.txt`, `03-supply-chain/perturbation/timeout-comparison.txt`.

The system therefore treats source availability as part of the evidence state itself. A missing or failed source changes what can legitimately be concluded, rather than merely changing an internal error message. The full test suite passed 34 tests, and mypy and ruff completed without errors. Evidence: `03-supply-chain/tests.txt`, `03-supply-chain/static-checks.txt`.

## Cross-System Synthesis

Across all three systems, the common reliability principle is to make uncertainty and failure observable instead of hiding them.

The policy system stops futile retries and routes low-confidence output to human review. The mortgage system preserves null values and exposes arithmetic contradictions. The supply-chain system retains conflicting evidence and explicitly marks conclusions as incomplete when a source fails. These are different mechanisms, but they all reduce the chance that a downstream user receives a clean-looking answer whose evidentiary basis is weak.

The perturbation results are particularly useful because they show behavior under failure rather than only success on normal inputs. In System 1, missing source information produced an escalation after one API call. In System 2, a deliberately changed stated total produced an explicit discrepancy. In System 3, a simulated timeout changed source-dependent findings to an incomplete state while preserving available evidence. Evidence: `perturbation-log.md` and the three system-specific perturbation artifacts.

Another important lesson is that confidence, consistency, and source availability are separate dimensions of reliability. System 1's calibration sample contains a high-confidence but incorrect `umbrella/exclusions` result; System 2 can have a structurally valid extraction that is mathematically inconsistent; and System 3 can have correct individual source observations but still lack enough evidence when a source is unavailable. A reliable system therefore needs explicit validation and observability around each of these dimensions rather than relying on model confidence alone.

## Overall Reflection

The strongest evidence from this capstone is not that the systems always produce the right answer. It is that the systems are designed to expose conditions under which an answer should not be trusted automatically. The test suites, perturbation runs, calibration results, discrepancies, routing decisions, conflict handling, and incomplete states make those conditions inspectable.

One limitation of my evidence pack is the missing live Anthropic API credential for the System 1 end-to-end pipeline. I preserved the actual authentication failure rather than fabricating a successful run. The remaining System 1 routing, retry, and calibration evidence still demonstrates the relevant reliability behaviors, but the submission should distinguish those artifacts from a completed live pipeline execution.

This capstone reinforced that evaluation and observability are not separate from system design. They are mechanisms for making model behavior, uncertainty, data quality, and failure handling visible enough for a human or downstream process to make an informed decision.
