# AlphaMap product surfaces

AlphaMap is designed around one public data contract and multiple delivery surfaces. The open benchmark establishes the current semantics and conformance baseline. The target institutional surface is intended to extend coverage, timeliness and production delivery without changing the meaning of shared fields; coverage, cadence, rights and service terms are defined per engagement.

## Surface model

| Surface | Primary purpose | Status / intended scope |
| --- | --- | --- |
| Open Benchmark | Reproducibility, schema review, source audit and client integration testing | Public: versioned audit data, executable validation, reference signal code and falsifiable research protocol |
| AlphaMap Research | Canonical public research and product context | Public: ongoing research, methodology notes and public updates |
| Institutional Data/API | Production research and systematic ingestion | Evaluation-stage: coverage, delivery cadence, rights and service terms are defined per engagement |

The open benchmark is complete for its declared scope. Institutional differentiation is based on coverage breadth, observation latency, longitudinal depth and operational reliability. Definitions required to reproduce the public reference workflow remain public.

## Shared compatibility contract

The same concepts should remain compatible across public and institutional surfaces:

1. Stable entity, security, source, event, observation and relationship identifiers.
2. Explicit publication, availability and earliest-tradable timestamps.
3. Append-only vintages, supersession links and correction history.
4. Consistent event, claim, direction and relationship semantics.
5. Versioned schemas with documented breaking-change rules.
6. Open conformance fixtures that clients can use before receiving licensed data.
7. Reproducible feature definitions separated from customer-supplied market prices.

Institutional resources may add fields and tables. They should not silently redefine an existing public field; semantic breaks require a major contract version.

## Institutional delivery package

A procurement-ready AlphaMap package should include:

- **Bulk history:** versioned Parquet or CSV snapshots with manifests and checksums.
- **Incremental delivery:** cursor-based API or object-store deltas with deterministic replay.
- **As-of access:** queries and snapshots that reconstruct what was knowable at a specified time.
- **Correction channel:** append-only revisions, supersession reasons and customer notifications.
- **Coverage ledger:** issuer, market, document-type and date coverage with explicit gaps.
- **Data dictionary:** types, units, nullability, enumerations, examples and change policy.
- **Quality report:** latency, completeness, duplicate rate, revision rate and unresolved exceptions.
- **Provenance and rights:** source-level provenance, permitted-use boundaries and a rights schedule for every delivered resource.
- **Security and continuity:** target materials covering access controls, data handling, continuity and incident-response procedures.
- **Operations:** authentication, entitlements, rate limits, status reporting, support and service objectives.

A practical API surface can expose entities, securities, sources, events, observations, relationships, release manifests and change cursors. Bulk snapshots and incremental API delivery should resolve to the same release identifiers and content hashes.

## Evaluation-to-procurement path

1. **Open benchmark:** the evaluator checks semantics, lineage and integration mechanics.
2. **Bounded evaluation pack:** a larger time-delayed or coverage-limited dataset tests fit for the client's workflow.
3. **Parallel validation:** the client runs ingestion, as-of reconstruction and research evaluation against agreed acceptance criteria.
4. **Production license:** coverage, fields, delivery cadence, rights, service objectives and support are contractually defined.
5. **Ongoing governance:** releases, corrections, schema changes and quality metrics are reviewed through a documented process.

The evaluation pack should be representative enough to test ingestion and research utility, while respecting source rights and avoiding redistribution of third-party market data.

## Product and research claims

AlphaMap is evaluated on data quality, point-in-time integrity, coverage, delivery and research usability. Predictive performance is treated as a separately tested research outcome.

Public and commercial materials should therefore distinguish:

- feature values from realized returns;
- historical reconstruction from contemporaneous capture;
- registered parameters from estimated economic exposure;
- audit samples from inferential or production sampling frames;
- research evidence from investment advice or return promises.

## Canonical links

- AlphaMap research: https://lunartuliplab.com/en/alphamap
- Institutional access: https://lunartuliplab.com/en/institutional-access
- Open benchmark: https://github.com/Lunartulip/AlphaMap-Open-Benchmark
- Public protocol: ../research/protocol.json
- Data package: ../datapackage.json

Public website articles are research publications, not licensed dataset deliveries. AlphaMap-authored normalized records in this repository are licensed separately under ../DATA-LICENSE.md.
