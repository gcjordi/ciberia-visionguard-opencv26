output "public_ip" {
  value = aws_instance.visionguard.public_ip
}

output "demo_url" {
  value = "http://${aws_instance.visionguard.public_ip}/"
}

output "evidence_bucket" {
  value = aws_s3_bucket.evidence.bucket
}

output "dynamodb_table" {
  value = aws_dynamodb_table.traces.name
}

output "instance_id" {
  value = aws_instance.visionguard.id
}
