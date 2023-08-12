resource "aws_instance" "example" {
  ami = "ami-02a89066c48741345"
  instance_type = "t2.micro"
}