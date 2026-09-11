# Methodology

## Hypothesis

Changes in reviewable supply-chain evidence may reveal demand, capacity utilization or bottlenecks before effects are fully reflected across the AI-infrastructure value chain.

## Canonicalization

Documents are decomposed into atomic events and observations. Every record is labeled reported_fact, issuer_claim, derived_value, estimate or relationship_assertion. Summaries paraphrase evidence and preserve uncertainty.

## Feature

At each Friday UTC anchor, only events already tradable are eligible. Direction maps to -1, 0 or +1. Claim-label weights are fixed in code. Evidence decays with a 28-day half-life. Scores become centered cross-sectional percentile ranks. The open implementation uses direct impact only.

## Outcome and test

The primary outcome is the 20-session forward adjusted-close return minus the contemporaneous sector return. If a sector contains fewer than three covered securities, the universe mean is used and marked. The primary statistic is weekly Spearman rank IC with at least five securities per date and date-block bootstrap inference.

Baselines are same-timestamp disclosure count, trailing 20-session price momentum and unweighted signed evidence. Sensitivities cover 10, 25 and 50 bps costs, delayed availability, alternate half-lives and leave-one-group-out tests. No headline alpha claim is permitted before the prospective holdout finishes.
