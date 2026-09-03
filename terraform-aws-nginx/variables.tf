variable "aws_region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Prefix used to name project resources."
  type        = string
  default     = "terraform-nginx"
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "IPv4 CIDR block for the public subnet."
  type        = string
  default     = "10.0.0.0/24"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}
