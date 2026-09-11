# Data dictionary

The field-level source of truth is the root-level datapackage.json. Each resource defines field name, type, nullability, enum constraints and primary key.

The semantic groups are:

- identity: immutable entity_id and security_id; ticker validity is bounded by dataset coverage;
- provenance: source_id, URL, version, access state, locator and optional document hash;
- timing: published_at, available_at, tradable_from and timestamp basis;
- evidence: event type, stage, direction and claim label;
- values: one numeric or text observation with explicit unit, comparator and period;
- network: time-bounded directed relationship, registered propagation weight and economic-exposure flag;
- coverage: closed audit inventory and inference eligibility;
- revision: vintage_id and supersedes_id.

Unknown values are blank only where the contract permits null. Zero, false and not observed are never encoded as blank.
