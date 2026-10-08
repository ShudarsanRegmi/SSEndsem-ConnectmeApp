variable "environment" {
  type        = string
  description = "Target deployment environment (staging or production)"
}

variable "project_name" {
  type        = string
  default     = "connectme"
  description = "Project name prefix for AWS resources"
}

variable "aws_region" {
  type        = string
  default     = "ap-southeast-2"
  description = "AWS deployment region"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the dedicated VPC"
}

variable "public_subnet_1_cidr" {
  type        = string
  default     = "10.0.1.0/24"
  description = "CIDR block for public subnet in AZ a"
}

variable "public_subnet_2_cidr" {
  type        = string
  default     = "10.0.2.0/24"
  description = "CIDR block for public subnet in AZ b"
}

variable "container_image" {
  type        = string
  default     = "128325658589.dkr.ecr.ap-southeast-2.amazonaws.com/connectme-app:latest"
  description = "ECR container image URI for ConnectMe application"
}

variable "fargate_cpu" {
  type        = string
  default     = "1024"
  description = "Fargate vCPU units (1024 = 1 vCPU)"
}

variable "fargate_memory" {
  type        = string
  default     = "4096"
  description = "Fargate memory allocation in MiB (4096 = 4GB RAM)"
}

variable "db_host" {
  type        = string
  default     = "127.0.0.1"
  description = "Database host address"
}

variable "db_user" {
  type        = string
  default     = "aparichit"
  description = "Database username"
}

variable "db_password" {
  type        = string
  default     = "letmelogin"
  sensitive   = true
  description = "Database user password"
}

variable "db_name" {
  type        = string
  default     = "connectme_db"
  description = "Database schema name"
}

variable "jwt_secret_key" {
  type        = string
  default     = "8f4e2b1c6d9a0e5f7a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f"
  sensitive   = true
  description = "JWT encryption key for tokens"
}
