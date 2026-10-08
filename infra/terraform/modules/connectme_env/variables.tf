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
  default     = "us-east-1"
  description = "AWS deployment region"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the dedicated VPC"
}

variable "public_subnet_cidr" {
  type        = string
  default     = "10.0.1.0/24"
  description = "CIDR block for public subnet"
}

variable "instance_type" {
  type        = string
  default     = "t3.medium"
  description = "4GB RAM AWS EC2 instance type (t3.medium: 2 vCPUs, 4 GiB memory)"
}

variable "ami_id" {
  type        = string
  default     = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS (us-east-1)
  description = "Base AMI ID for application server"
}
