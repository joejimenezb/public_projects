variable "AWS_REGION" {
  default = "us-east-2"
}

variable "AMIS" {
  type = map(string)
  default = {
    us-east-1 = "ami-0f34c5ae932e6f0e4"
    us-east-2 = "ami-02a89066c48741345"
    eu-west-1 = "ami-8447e0bf"
  }
}

