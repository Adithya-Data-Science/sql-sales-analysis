output "instance_id" {
  description = "ID of the NGINX EC2 instance."
  value       = aws_instance.nginx.id
}

output "public_ip" {
  description = "Public IPv4 address of the NGINX EC2 instance."
  value       = aws_instance.nginx.public_ip
}

output "nginx_url" {
  description = "Public HTTP endpoint for NGINX."
  value       = "http://${aws_instance.nginx.public_ip}"
}
