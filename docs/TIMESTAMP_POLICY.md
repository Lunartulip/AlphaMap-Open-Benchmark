# Timestamp policy

AlphaMap stores publication, availability, tradability, formation and execution as distinct clocks.

published_at is source metadata. available_at is the earliest conservative normalization time. tradable_from is the first possible market opportunity after availability. formation_at is the research decision timestamp. execution_at is the price observation actually used by the daily reference implementation.

Each source declares timestamp_basis. wire_metadata requires a source-displayed timestamp. reconstructed_conservative means the record was assembled later and receives date-close-plus-15-minutes availability followed by the next regular-session open. The 15 minutes are a registered allowance, not measured historical latency.

The research runner uses the first observed price session strictly after Friday formation and therefore never executes at an earlier Friday close. Production releases must use exchange calendars and contemporaneous first-seen logs. A more precise timestamp creates a new vintage rather than rewriting history.
