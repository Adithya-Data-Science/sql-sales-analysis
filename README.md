# Cloud Infrastructure and Data Engineering Portfolio

This repository contains three hands-on projects demonstrating infrastructure as code, AWS deployment workflows, and distributed data processing.

## Projects

| Project | Technologies | What it demonstrates |
| --- | --- | --- |
| [Terraform AWS NGINX Infrastructure](terraform-aws-nginx/README.md) | Terraform, EC2, VPC, Linux | Creates a network and Ubuntu web server, installs NGINX, and exposes HTTP through a controlled security group. |
| [Terraform S3 Static Website](terraform-s3-static-website/README.md) | Terraform, Amazon S3 | Creates a uniquely named S3 website bucket, uploads index/error pages, and configures public website access. |
| [Olist E-Commerce Data Engineering](olist-data-engineering/README.md) | PySpark, Spark SQL, AWS EMR, S3 | Cleans and joins eight Olist datasets, performs validation checks, and writes analytics-ready Parquet outputs. |

Each folder includes implementation files, usage instructions, architecture notes, validation steps, and cleanup guidance. No credentials, Terraform state, or large source datasets are committed.

## Responsible cloud usage

AWS resources may incur charges. Review each Terraform plan before applying and destroy temporary resources after validation.
