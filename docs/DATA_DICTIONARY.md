# Data dictionary

entities.csv stores immutable issuer keys and descriptive attributes. security_mappings.csv stores stable instrument keys with point-in-time ticker validity.

sources.csv identifies first-party documents, publication precision and narrow source locators. events.csv stores the disclosing actor, impacted security, event taxonomy, typed claim, timing, eligibility and summary.

observations.csv contains exactly one numeric_value or text_value per row with metric, unit, comparator, period and locator. relationships.csv contains time-bounded supply-chain edges; alpha_feature_eligible remains false until economic exposure is attributable.

release_manifest.json records version, release time, schema version, row counts and SHA-256 for every distributed table.
