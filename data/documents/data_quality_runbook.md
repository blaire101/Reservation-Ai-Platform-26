# Reservation Data Quality Runbook

## Checks
1. Freshness: ingestion delay should not exceed 120 minutes.
2. Partition completeness: actual reservation rows should be at least 80% of the recent site baseline.
3. Duplicate rate: reservation_id must be unique after ingestion deduplication.
4. Null rate: user_id, campaign_id, product_id, and site should have less than 1% nulls.

## Incident response
When the dashboard is incomplete, identify the affected date and site, check source completion, compare actual rows with the baseline, remove or correct invalid records, rerun the partition, and validate downstream metrics.
