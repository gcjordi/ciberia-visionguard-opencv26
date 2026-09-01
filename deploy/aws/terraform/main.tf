provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  evidence_bucket = "visionguard-evidence-${data.aws_caller_identity.current.account_id}-${var.aws_region}"
  tags = {
    Project     = "CiberIA VisionGuard"
    Competition = "OpenCV AI Competition 2026"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket" "evidence" {
  bucket = local.evidence_bucket
  tags   = local.tags
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    id     = "expire-demo-evidence"
    status = "Enabled"
    expiration { days = 7 }
  }
}

resource "aws_dynamodb_table" "traces" {
  name         = "${var.project_name}-traces"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "trace_id"
  attribute {
    name = "trace_id"
    type = "S"
  }
  point_in_time_recovery { enabled = true }
  tags = local.tags
}

resource "aws_iam_role" "ec2" {
  name = "${var.project_name}-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
  tags = local.tags
}

resource "aws_iam_role_policy" "app" {
  role = aws_iam_role.ec2.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject"]
        Resource = "${aws_s3_bucket.evidence.arn}/*"
      },
      {
        Effect = "Allow"
        Action = ["dynamodb:PutItem", "dynamodb:GetItem"]
        Resource = aws_dynamodb_table.traces.arn
      },
      {
        Effect = "Allow"
        Action = ["cloudwatch:PutMetricData"]
        Resource = "*"
        Condition = { StringEquals = { "cloudwatch:namespace" = "CiberIA/VisionGuard" } }
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_name}-instance-profile"
  role = aws_iam_role.ec2.name
}

resource "aws_security_group" "app" {
  name        = "${var.project_name}-sg"
  description = "VisionGuard judge/demo endpoint"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP demo endpoint"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH restricted to administrator"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_instance" "visionguard" {
  ami                         = var.cool_ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  associate_public_ip_address = true
  key_name                    = var.key_name
  vpc_security_group_ids      = [aws_security_group.app.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2.name

  root_block_device {
    encrypted   = true
    volume_type = "gp3"
    volume_size = 30
  }

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  tags = merge(local.tags, { Name = var.project_name })
}
