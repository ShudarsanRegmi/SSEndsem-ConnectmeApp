module "connectme_staging" {
  source               = "../../modules/connectme_env"
  environment          = "staging"
  project_name         = "connectme"
  aws_region           = "ap-southeast-2"
  vpc_cidr             = "10.10.0.0/16"
  public_subnet_1_cidr = "10.10.1.0/24"
  public_subnet_2_cidr = "10.10.2.0/24"
  container_image      = "128325658589.dkr.ecr.ap-southeast-2.amazonaws.com/connectme-app:v0.7.0"
  fargate_cpu          = "1024" # 1 vCPU
  fargate_memory       = "4096" # 4GB RAM
}

output "staging_alb_url" {
  value       = "http://${module.connectme_staging.alb_dns_name}"
  description = "Staging Application Load Balancer URL"
}

output "staging_ecs_cluster" {
  value       = module.connectme_staging.ecs_cluster_name
  description = "Staging ECS Cluster Name"
}

output "staging_s3_bucket" {
  value       = module.connectme_staging.s3_bucket_arn
  description = "Staging S3 Media Bucket ARN"
}
