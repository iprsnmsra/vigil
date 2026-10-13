variable "region" {
  type    = string
  default = "us-west-2"
}

variable "cluster_name" {
  type    = string
  default = "vigil-eks-prod"
}

variable "node_instance_type" {
  type    = string
  default = "t3.large"
}

variable "node_count" {
  type    = number
  default = 3
}
