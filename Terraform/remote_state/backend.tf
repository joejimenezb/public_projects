terraform {
  backend "s3" {
    bucket = "terrafor-state-tf-joe0809"
    key = "demo_state/ec2"   
  }
}