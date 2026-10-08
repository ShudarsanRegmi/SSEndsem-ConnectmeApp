module "connectme_staging" {
  source             = "../../modules/connectme_env"
  environment        = "staging"
  project_name       = "connectme"
  aws_region         = "us-east-1"
  vpc_cidr           = "10.10.0.0/16"
  public_subnet_cidr = "10.10.1.0/24"
  instance_type      = "t3.medium" # 4GB RAM instance
}

output "staging_instance_ip" {
  value       = module.connectme_staging.instance_public_ip
  description = "Public IP for Staging 4GB Instance"
}

output "staging_s3_bucket" {
  value       = module.connectme_staging.s3_bucket_arn
  description = "Staging S3 Media Bucket ARN"
}
