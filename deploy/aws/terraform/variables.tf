variable "aws_region" {
  type        = string
  description = "AWS region in which the subscribed COOL Marketplace AMI is available."
  default     = "eu-west-1"
}

variable "cool_ami_id" {
  type        = string
  description = "AMI ID shown by AWS after subscribing to Cloud Optimized OpenCV for AWS Graviton4."
}

variable "instance_type" {
  type        = string
  description = "Graviton4 instance. COOL supports c8g/m8g/r8g; scale up for final benchmarks."
  default     = "c8g.xlarge"
}

variable "vpc_id" {
  type        = string
  description = "VPC for the demo host."
}

variable "subnet_id" {
  type        = string
  description = "Public subnet with an Internet Gateway route."
}

variable "admin_cidr" {
  type        = string
  description = "CIDR allowed to SSH, e.g. 203.0.113.10/32. Never use 0.0.0.0/0 for SSH."
}

variable "key_name" {
  type        = string
  description = "Existing EC2 key pair name for judge/demo administration."
}

variable "project_name" {
  type    = string
  default = "ciberia-visionguard"
}
