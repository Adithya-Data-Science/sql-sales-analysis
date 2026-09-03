variable "aws_region" {
  description = "AWS region for the website bucket."
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Prefix for the globally unique bucket name."
  type        = string
  default     = "adithya-terraform-site"
}
