# Release Roadmap

This roadmap separates the open audit sample from the production research panel. A milestone is complete only when its stated acceptance gate is reproducible from a tagged release.

## Open benchmark: first 48 hours

Status: implemented on the review branch.

- Publish a normalized, point-in-time audit sample with entity, security, source, event, observation, relationship and coverage tables.
- Make publication, availability, tradability and validity clocks explicit.
- Ship a standard Frictionless Data Package plus domain-specific temporal and lineage validation.
- Construct direct and one-hop propagated evidence features over a complete point-in-time universe.
- Align outcomes to the first observed session close after formation and the following 20 sessions.
- Register SCEM-4W-v2 before any production holdout result.
- Run the contract, manifest, unit tests and lint checks on Python 3.11 and 3.12.

Acceptance gate: every record is traceable, the sample is visibly non-inferential, standard and custom validators pass, and the tagged files are content-addressed.

## Production capture: weeks 1–2

- Freeze the target universe definition and maintain security membership with effective dates.
- Capture the full first-party document stream for every in-scope issuer, including zero-event periods.
- Preserve first-seen time, retrieval time, source time precision, document locator and content hash.
- Operate an append-only revision ledger with deterministic event and observation identifiers.
- Measure source latency, missingness, duplicate rate and issuer/event-type coverage each week.
- Add licensed market data through an adapter; do not redistribute it in this repository.

Acceptance gate: continuous collection, replayable point-in-time snapshots, no unexplained coverage gaps and documented incident handling.

## Label and research controls: weeks 2–3

- Run blinded dual review for direction, materiality, claim type and propagation applicability.
- Report reviewer agreement and adjudication history by field.
- Implement all registered baselines, propagation-weight sensitivities, execution lags, cost scenarios and leave-one-out diagnostics.
- Produce automated temporal leakage, universe survivorship, relation-deduplication and concentration reports.
- Freeze data-quality thresholds before opening the holdout.

Acceptance gate: protocol-complete research code, independent label QC, deterministic rebuilds and passing release checks.

## Research release: weeks 3–4

- Freeze the versioned production sampling frame, contract and code.
- Publish a signed manifest, data card, coverage report, changelog and reproducibility instructions.
- Start the prospective holdout only after the frozen tag; keep validation and holdout outputs separate.
- Report negative, null and positive outcomes under the same registered decision rules.
- Publish vendor-readiness evidence for delivery stability, schema evolution, monitoring and support.

Acceptance gate: a third party can reconstruct features and outcomes from the release, while claims remain limited to the completed evidence window.

## Vendor readiness beyond week 4

QuantConnect-style distribution requires more than a successful sample. Before a commercial listing, AlphaMap will require a materially longer point-in-time history, survivorship-free coverage, stable scheduled delivery, monitoring and incident response, clear licensing, and documentation for research and live use. Those capabilities are release gates, not claims attached to the audit sample.
