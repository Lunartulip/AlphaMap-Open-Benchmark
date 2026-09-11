# AlphaMap Open Benchmark

Point-in-time AI-infrastructure evidence for reproducible public-equity research.

[![CI](https://github.com/Lunartulip/ai-chip-industry-map/actions/workflows/ci.yml/badge.svg)](https://github.com/Lunartulip/ai-chip-industry-map/actions/workflows/ci.yml)
[![Contract](https://img.shields.io/badge/data_package-v1-5B8CFF)](contracts/v1/datapackage.json)
[![Protocol](https://img.shields.io/badge/protocol-draft_registered-12B886)](research/protocol.json)

## Registered question

Does supply-chain evidence momentum predict AI-infrastructure companies' next four-week relative returns?

AlphaMap separates that research program from the open audit sample. The repository publishes the point-in-time contract, evidence lineage, one-hop supply propagation, complete-universe feature construction, executable return alignment and falsifiable protocol. Statistical claims require the frozen production sampling frame and prospective holdout defined in SCEM-4W-v2.

## Open audit sample v1

| Property | Coverage |
| --- | --- |
| Evidence window | 2023-08-23 to 2025-03-18 |
| Listed issuers | 6 |
| Canonical events | 12 |
| Atomic observations | 15 |
| First-party documents | 11 |
| Confirmed supply edges | 2 |
| Timestamp basis | Explicitly observed or conservatively reconstructed |
| Inference eligibility | No; data engineering and source audit only |

The sample is small enough to reconstruct record by record. coverage.csv identifies its selection role and prevents accidental use as an inferential backtest.

## What is measured

A source event produces a direct issuer evidence impulse. When an active confirmed supplier edge exists, the same event can produce a separately labeled one-hop propagated impulse for the customer security. The registered supply-chain momentum feature is the change in 28-day decayed propagated evidence stock over four weeks.

The uniform propagation coefficient is a research parameter, not an estimate of revenue exposure. Direct and propagated components remain independently inspectable.

## Temporal model

Source publication -> conservative availability -> earliest tradable time -> Friday formation -> next observed session close -> 20-session forward return

Historical records reconstructed after publication carry timestamp_basis=reconstructed_conservative. They demonstrate no-lookahead mechanics but are never represented as contemporaneously captured observations.

## Quick start

    python -m pip install -e ".[dev]"
    alphamap-validate data/sample/v1 --manifest
    pytest
    python research/run_research.py --prices examples/price_input_schema.csv

Required price columns are date, security_id and adjusted_close. Evidence data never embeds or relicenses market prices.

## Repository map

- data/sample/v1: normalized audit sample and release manifest
- contracts/v1/datapackage.json: Frictionless-compatible tabular contract
- src/alphamap_open: contract validation, signal construction and evaluation
- research: pre-registration state and reproducible runner
- docs: methodology, sampling, timestamps, governance and field semantics
- CHANGELOG.md: release history and link to the historical visualization commit

## Quality principles

1. Event dates never substitute for availability or execution timestamps.
2. Issuer-reported actuals and forward statements remain distinct.
3. No-event securities remain in the weekly cross-section with a zero score.
4. Revisions are append-only after release.
5. Data contracts are executable and release files are content-addressed.
6. Baselines, costs, lags, concentration tests and falsifiers are fixed before results.
7. A negative result is a valid registered outcome.

Code is MIT licensed. AlphaMap-authored normalized data is CC BY 4.0 subject to DATA-LICENSE.md.
