resource "aws_s3_bucket" "resumes" {
  # Use a new, unique name to avoid conflicts
  bucket = "resume-ranker-bucket-tanya-2025-final" 
}

resource "aws_sqs_queue" "resume_processing_queue" {
  name = "ResumeProcessingQueue"
}