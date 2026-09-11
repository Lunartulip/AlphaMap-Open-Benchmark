# Architecture

The system separates five layers: immutable source evidence; canonical events and atomic observations; point-in-time timestamps, identifiers and vintages; deterministic research features and outcomes; and assurance through contracts, hashes, tests and governance.

The CSV surface is a portable reference implementation. Production should publish append-only Parquet partitions by knowledge date, revision feeds, exchange-calendar and security-master history, and signed manifests.

Source parsing cannot mutate released semantic records. Identifier changes cannot rewrite entity history. Market prices remain outside the evidence license boundary. Signal code consumes validated tables and cannot infer missing timestamps.
