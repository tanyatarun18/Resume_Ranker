resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "resume-ranker-vpc"
  }
}

# We create two public subnets in different availability zones for high availability.
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.10.0/24" # Using a new IP range to avoid conflicts
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true # This is critical for public subnets

  tags = {
    Name = "resume-ranker-public-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.11.0/24" # Using a new IP range to avoid conflicts
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true # This is critical for public subnets

  tags = {
    Name = "resume-ranker-public-b"
  }
}