# Data card

## Intended use

AlphaMap Open Benchmark is a research-grade sample for testing whether changes in verifiable supply-chain evidence precede four-week relative returns among listed AI-infrastructure companies. It supports schema review, pipeline integration, feature replication and protocol critique.

## Coverage and unit

Version 1 covers six US-listed issuers and first-party disclosures from 2023-08-23 through 2025-03-18. An event is a time-stamped change in economically relevant evidence. An observation is one atomic numeric or textual claim attached to that event.

## Point-in-time fields

published_at records the source timestamp. available_at is the earliest conservative machine-ingestion time. tradable_from is the earliest modeled regular-session execution time. ingestion_at and vintage_id preserve dataset history.

## Known limitations

- The sample is not statistically powered and contains no market prices.
- Public issuer disclosures overrepresent management-selected information.
- Date-only releases receive conservative next-session treatment.
- Unquantified supply relationships are ineligible for propagated alpha features.
- A production universe requires broader identifier and corporate-action history.

Passing validation means records satisfy the contract. It does not certify issuer claims or predictive performance.
