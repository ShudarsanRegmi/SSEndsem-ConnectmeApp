module "connectme_production" {
  source               = "../../modules/connectme_env"
  environment          = "production"
  project_name         = "connectme"
  aws_region           = "ap-southeast-2"
  vpc_cidr             = "10.20.0.0/16"
  public_subnet_1_cidr = "10.20.1.0/24"
  public_subnet_2_cidr = "10.20.2.0/24"
  container_image      = "128325658589.dkr.ecr.ap-southeast-2.amazonaws.com/connectme-app:latest"
  fargate_cpu          = "1024" # 1 vCPU
  fargate_memory       = "4096" # 4GB RAM
}

output "production_alb_url" {
  value       = "http://${module.connectme_production.alb_dns_name}"
  description = "Production Application Load Balancer URL"
}

output "production_ecs_cluster" {
  value       = module.connectme_production.ecs_cluster_name
  description = "Production ECS Cluster Name"
}

output "production_s3_bucket" {
  value       = module.connectme_production.s3_bucket_arn
  description = "Production S3 Media Bucket ARN"
}
