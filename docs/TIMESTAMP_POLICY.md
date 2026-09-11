# Timestamp policy

Temporal integrity uses UTC and three fields:

- published_at: time displayed by the source, or date-only when no reliable time exists.
- available_at: earliest conservative time normalized evidence could be observed.
- tradable_from: first modeled regular-session execution time after availability.

EXACT_PLUS_15M adds a 15-minute ingestion allowance to an exact timestamp. AFTER_CLOSE_NEXT_SESSION begins trading at the next US regular-session open. DATE_ONLY_NEXT_SESSION places availability after the dated session and also begins at the next open.

Production must use an exchange calendar for holidays and daylight saving. The sample stores explicit timestamps; downstream code never reconstructs them from event_date. More precise evidence creates a new vintage rather than rewriting a released timestamp.
