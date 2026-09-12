# Experiment decision report

## Recommendation

**Launch With Monitoring** for the simulated onboarding redesign.

The treatment changed 7-day activation from 43.0% to 47.5%, an absolute effect of 4.45% (95% CI 3.19% to 5.70%; p=0.0000) and relative lift of 10.3%.

Randomization passed the sample-ratio-mismatch check (p=0.737) and prior-activity balance check (p=0.147). Regression adjustment estimated an effect of 4.33%. The engagement difference-in-differences estimate was 0.332 events per user.

## Decision rule

Launch only if the primary metric's 95% confidence interval is above zero and plausible harm remains below +1 percentage point for support contacts and +15 ms for latency. Continue monitoring long-term retention, segment stability, logging quality, and novelty effects.

## Limitations

The data are synthetic. Subgroups are exploratory after false-discovery-rate correction. Difference-in-differences depends on parallel trends, and one pre-period cannot establish that assumption. A real rollout should use preregistered metrics, an exposure audit, longer retention windows, and sequential-testing controls if results are monitored repeatedly.
