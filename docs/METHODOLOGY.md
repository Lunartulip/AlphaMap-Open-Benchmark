# Methodology

## Research object

The primary object is propagated evidence momentum rather than issuer disclosure level. An eligible supplier event receives a direct score at the supplier and a separately labeled one-hop score at the customer when a confirmed relationship is active. The relationship coefficient is fixed at 0.25 for the primary specification and is explicitly non-economic.

At each Friday 23:59:59 UTC formation, the engine computes a 28-day decayed propagated evidence stock. Momentum is the current stock minus its four-week lag. Every member of the frozen point-in-time universe is present; securities without eligible evidence receive zero before cross-sectional ranking.

## Claim typing

issuer_reported_actual means the issuer reported a realized historical metric; it is not independent verification. issuer_forward_statement identifies guidance or qualitative outlook. derived_value, estimate and relationship_assertion remain separate.

## Execution and outcome

The daily reference implementation executes at the first adjusted close strictly after formation. The outcome is the subsequent 20-session adjusted-close return minus the equal-weight return of all other available universe members. This leave-one-out benchmark avoids mechanical self-inclusion.

## Inference

The primary statistic is weekly Spearman rank IC. Five-week moving-date blocks address overlapping four-week outcomes. Portfolio cost sensitivity is a separate dollar-neutral tercile test with defined execution price, weight changes and one-way costs.

The open audit sample is excluded from statistical claims. It exists to test schema, source reconstruction, temporal alignment and feature mechanics.
