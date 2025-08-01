output "rds_endpoint" {
  description = "The endpoint address of the RDS database."
  value       = aws_db_instance.main.address
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket for resumes."
  value       = aws_s3_bucket.resumes.id
}

output "sqs_queue_url" {
  description = "The URL of the SQS queue."
  value       = aws_sqs_queue.resume_processing_queue.id
}
