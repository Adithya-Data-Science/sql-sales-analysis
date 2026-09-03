# Verification record

The AWS EMR pipeline was run in 2026 against the eight linked Olist datasets stored in Amazon S3. The run processed approximately 100,000 orders, completed the documented validation checks, and wrote processed outputs back to S3.

Account-specific bucket paths, credentials, cluster identifiers, and private logs are intentionally excluded. The published code contains the reproducible Spark job, required-column checks, duplicate and null-key checks, negative-price validation, operational SQL queries, and customer-growth analysis.

The customer-growth query produces two reporting layers:

1. State-level market KPIs, including repeat-customer rate, average customer value, recent high-value customers, re-engagement candidates, and review scores.
2. A Salesforce-ready outreach queue using de-identified external customer IDs and honest segment labels. The public source data contains no email or phone fields, so none are invented.
