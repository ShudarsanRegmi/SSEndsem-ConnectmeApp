output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID of the environment"
}

output "instance_id" {
  value       = aws_instance.app_server.id
  description = "EC2 instance ID"
}

output "instance_public_ip" {
  value       = aws_instance.app_server.public_ip
  description = "Public IP address of the 4GB EC2 instance"
}

output "s3_bucket_arn" {
  value       = aws_s3_bucket.media.arn
  description = "ARN of the encrypted S3 media storage bucket"
}
