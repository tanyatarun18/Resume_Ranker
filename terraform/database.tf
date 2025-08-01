resource "aws_db_instance" "main" {
  allocated_storage      = 20
  engine                 = "postgres"
  instance_class         = "db.t3.micro"
  db_name                = "resumeranker"
  username               = "rankeradmin"
  password               = "yoursecurepassword123"
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.default.name
  publicly_accessible    = true
}