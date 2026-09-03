output "bucket_name" {
  description = "Generated S3 bucket name."
  value       = aws_s3_bucket.website.id
}

output "website_endpoint" {
  description = "S3 static website endpoint."
  value       = "http://${aws_s3_bucket_website_configuration.website.website_endpoint}"
}
