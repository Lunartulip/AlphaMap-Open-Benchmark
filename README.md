# AlphaMap Open Benchmark

Point-in-time AI-infrastructure evidence for reproducible public-equity research.

[![CI](https://github.com/Lunartulip/ai-chip-industry-map/actions/workflows/ci.yml/badge.svg)](https://github.com/Lunartulip/ai-chip-industry-map/actions/workflows/ci.yml)
[![Contract](https://img.shields.io/badge/data_contract-v1-5B8CFF)](contracts/v1/dataset.schema.json)
[![Protocol](https://img.shields.io/badge/research-design_locked-12B886)](research/protocol.json)

## Registered question

Does supply-chain evidence momentum predict AI-infrastructure companies' next four-week relative returns?

This repository publishes the data contract, point-in-time sample, deterministic feature construction and falsifiable evaluation protocol required to answer that question. It makes no performance claim before a prospective holdout is complete.

## Open sample v1

| Property | Coverage |
| --- | --- |
| Evidence window | 2023-08-23 to 2025-03-18 |
| Listed issuers | 6 |
| Canonical events | 14 |
| Atomic observations | 18 |
| First-party documents | 13 |
| Return horizon | 20 trading sessions |
| Timestamp standard | UTC availability plus earliest tradable session |

The sample is deliberately small enough to audit source by source. It demonstrates semantics and temporal controls; it is not presented as a statistically powered backtest.

## Architecture

Source document -> source record -> canonical event -> atomic observation -> weekly evidence score -> forward relative return

Every investable record has stable issuer and security identifiers, a source locator, claim label, publication time, conservative availability time, earliest tradable time and append-only vintage. Relationship propagation stays off unless economic exposure is attributable and independently reviewable.

## Quick start

    python -m pip install -e ".[dev]"
    alphamap-validate data/sample/v1 --manifest
    pytest
    python research/run_research.py --prices examples/price_input_schema.csv

Price input is intentionally user-supplied. Required columns are date, security_id and adjusted_close. Optional sector enables sector-relative outcomes.

## Repository map

- data/sample/v1: versioned records and release manifest
- contracts/v1: machine-readable contract
- src/alphamap_open: validation, features and evaluation
- research: locked protocol and reproducible runner
- docs: methodology, timestamps, governance and dictionary
- legacy: frozen historical visualization retained for provenance

## Design principles

1. Point-in-time by construction: event dates never substitute for availability.
2. Claims are typed: reported facts, issuer statements and derived values remain distinct.
3. Revisions are append-only and prior releases remain addressable.
4. Identifiers are stable; tickers are attributes, not entity keys.
5. Baselines, lags, costs, concentration tests and holdout rules are specified before results.
6. A negative research result is a valid outcome.

See [Data Card](docs/DATA_CARD.md), [Methodology](docs/METHODOLOGY.md), [Timestamp Policy](docs/TIMESTAMP_POLICY.md) and [Governance](docs/GOVERNANCE.md).

## Licensing

Code is MIT licensed. AlphaMap-authored normalized sample records are CC BY 4.0 subject to DATA-LICENSE.md. Third-party documents remain governed by their publishers.
