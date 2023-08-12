variable "AWS_ACCESS_KEY" {}
variable "AWS_SECRET_KEY" {}
variable "AWS_REGION" {
    default = "us-east-2"
}
variable "PATH_TO_PUBLIC_KEY" {
    default = "mykey.pub"
}
variable "PATH_TO_PRIVATE_KEY" {
    default = "mykey"
}
variable "INSTANCE_USERNAME" {
    default = "ubuntu" 
}
variable "AMIS" {
    type = map
    default = {
        us-east-1 = "ami-024e6efaf93d85776"
        us-east-2 = "ami-024e6efaf93d85776"
    }
  
}