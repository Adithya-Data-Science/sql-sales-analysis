# Analytics, Cloud Infrastructure, and Data Engineering Portfolio

This repository contains reproducible projects supporting the technical and analytical work described in my resume.

## Projects

| Project | Technologies | What it demonstrates |
| --- | --- | --- |
| [Community Engagement Dashboard and Impact Reporting](community-engagement-dashboard/README.md) | Excel workflow, Python, data visualization | Defines five stakeholder KPI areas, validation controls, and a privacy-safe reproducible sample analysis. |
| [Terraform AWS NGINX Infrastructure](terraform-aws-nginx/README.md) | Terraform, EC2, VPC, Linux | Creates a network and Ubuntu web server, installs NGINX, and exposes HTTP through a controlled security group. |
| [Terraform S3 Static Website](terraform-s3-static-website/README.md) | Terraform, Amazon S3 | Creates a uniquely named S3 website bucket, uploads index/error pages, and configures public website access. |
| [Olist Data Engineering, Customer Growth, and Operations Analytics](olist-data-engineering/README.md) | PySpark, SQL, AWS EMR, S3 | Validates and joins eight datasets, prepares operational KPIs, segments customers, and creates outreach-ready outputs. |
| [Object-Oriented Survey Analytics and Stakeholder Reporting](survey-data-analysis/README.md) | Python, OOP, Pandas, Matplotlib, Pytest | Separates validation, KPI analysis, and reporting into reusable classes; verifies four KPIs and three charts with automated tests. |
| [Large-Scale Equity Data Pipeline](https://github.com/Adithya-Data-Science/equity-factor-analysis) | Python, Pandas | Converts raw market records into a validated panel and retains honest out-of-sample results. |

Each folder includes implementation files, usage instructions, validation steps, and privacy or cleanup guidance. Credentials, Terraform state, private institutional records, and large source datasets are not committed.

## Responsible use

AWS resources may incur charges. Review each Terraform plan before applying and destroy temporary resources after validation. Projects based on institutional work publish only data definitions and sanitized samples.
