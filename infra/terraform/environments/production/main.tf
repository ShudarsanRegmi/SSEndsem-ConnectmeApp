module "connectme_production" {
  source             = "../../modules/connectme_env"
  environment        = "production"
  project_name       = "connectme"
  aws_region         = "us-east-1"
  vpc_cidr           = "10.20.0.0/16"
  public_subnet_cidr = "10.20.1.0/24"
  instance_type      = "t3.medium" # 4GB RAM instance
}

output "production_instance_ip" {
  value       = module.connectme_production.instance_public_ip
  description = "Public IP for Production 4GB Instance"
}

output "production_s3_bucket" {
  value       = module.connectme_production.s3_bucket_arn
  description = "Production S3 Media Bucket ARN"
}
