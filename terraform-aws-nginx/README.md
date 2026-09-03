# Terraform AWS NGINX Infrastructure

Provisions a small, reproducible AWS network and an Ubuntu EC2 instance running NGINX.

## Architecture

Internet -> Internet Gateway -> Public Route Table -> Public Subnet -> Security Group -> EC2 / NGINX

## Resources

- VPC and public subnet
- Internet gateway, route table, and subnet association
- Security group allowing inbound HTTP on port 80
- Ubuntu 22.04 EC2 instance with an encrypted 10 GiB gp3 root volume
- Bootstrap script that installs and starts NGINX

## Deploy

Prerequisites: Terraform 1.5+, AWS CLI, and configured AWS credentials.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform output nginx_url
```

Open the reported URL and confirm the NGINX welcome page loads.

## Clean up

```bash
terraform destroy
```

Terraform state and plan files are intentionally excluded from version control. The example allows public HTTP only; production deployments should add HTTPS, restricted administrative access, monitoring, and hardened configuration.
