# Verification record

The infrastructure was deployed in AWS in August 2026 and validated through the EC2 instance's public HTTP endpoint. The successful test confirmed that the VPC, subnet, internet gateway, route table, security group, EC2 instance, user-data bootstrap, and NGINX service worked together.

After validation, the environment was removed with `terraform destroy` to avoid unnecessary charges. Public IP addresses, account identifiers, credentials, state files, and plan files are intentionally not committed.

For a new deployment, reproduce the checks documented in the project README:

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform output nginx_url
terraform destroy
```
