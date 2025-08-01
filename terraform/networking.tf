resource "aws_security_group" "db_sg" {
  name        = "resume-ranker-db-sg"
  description = "Allow PostgreSQL traffic for Resume Ranker"
  vpc_id      = aws_vpc.main.id

  # Rule to allow YOUR computer to connect to the database.
  # IMPORTANT: Replace the IP address with the one you just looked up.
  ingress {
    description = "PostgreSQL from my computer"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["152.58.79.138/32"] 
  }

  # Allows all outbound traffic from the database.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "resume-ranker-db-sg"
  }
}

# This tells the RDS database which subnets it is allowed to live in.
resource "aws_db_subnet_group" "default" {
  name       = "resume-ranker-subnet-group"
  subnet_ids = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  tags = {
    Name = "Resume Ranker DB Subnet Group"
  }
}

# This creates the "door" from your VPC to the public internet.
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "resume-ranker-igw"
  }
}

# This creates a route table to direct traffic to the internet gateway.
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = {
    Name = "resume-ranker-public-rt"
  }
}

# This associates the route table with our public subnets.
resource "aws_route_table_association" "public_assoc_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_assoc_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public_rt.id
}
