output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID of the environment"
}

output "alb_dns_name" {
  value       = aws_lb.main.dns_name
  description = "Public DNS name of the Application Load Balancer"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "ECS Cluster Name"
}

output "ecs_service_name" {
  value       = aws_ecs_service.main.name
  description = "ECS Service Name"
}

output "s3_bucket_arn" {
  value       = aws_s3_bucket.media.arn
  description = "ARN of the encrypted S3 media storage bucket"
}
