variable "myvar" {
    type = string
    default = "Hello World"
}
 
variable "mymap" {
  type = map(string)
  default = {
    mykey = "my value"
  }
}

variable "mylist" {
  type = list
  default = [1,2,3]
}

#deploy command 
#terraform plan -out file.yml; terraform apply file.yml; rm file.yml

