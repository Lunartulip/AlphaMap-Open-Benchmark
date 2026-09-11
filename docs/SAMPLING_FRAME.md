# Sampling frame

## Open audit frame

AUDIT-V1 is a non-inferential reconstruction set. It contains eleven enumerated first-party documents chosen to exercise the contract across accelerators, memory, custom silicon, networking and power/cooling. coverage.csv is the closed inventory for that audit set. It is suitable for source review and pipeline tests only.

## Production research frame

Before statistical evaluation, SCEM-4W-v2 requires:

- a frozen point-in-time security universe with entry and exit dates;
- daily capture of every SEC filing and issuer investor-relations release for each member;
- an immutable document ledger including documents with zero eligible events;
- deterministic inclusion and exclusion rules by source type and taxonomy;
- first-seen timestamps and content hashes collected at ingestion;
- blinded direction labels with agreement metrics;
- explicit missingness, restatement and access-failure logs.

The production coverage matrix reports issuer by calendar month by document type: expected, captured, parsed, event-bearing, zero-event and failed. Research cannot advance from validation to holdout while any required cell is unresolved.
