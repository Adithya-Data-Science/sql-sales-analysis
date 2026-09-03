# Terraform S3 Static Website

Creates and manages a public Amazon S3 static website using Terraform.

## What it builds

- S3 bucket with a random suffix for global uniqueness
- Static website configuration with index and error documents
- Bucket ownership and public-access settings
- Least-scope public policy permitting `s3:GetObject` only
- Managed HTML objects with content types and change-detection hashes

## Deploy

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform output website_endpoint
```

Visit the output endpoint to validate the page, then remove the temporary infrastructure:

```bash
terraform destroy
```

This educational example intentionally exposes website objects publicly. A production design would normally use a private S3 origin behind CloudFront with TLS, access controls, logging, and a custom domain.

## Completed validation

The infrastructure was applied in AWS in August 2026, the generated website endpoint served the index and error pages, and the temporary resources were removed through Terraform. Account-specific endpoint and state data are intentionally not committed.
