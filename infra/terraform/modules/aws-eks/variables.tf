variable "region" {
  type        = string
  description = "AWS region"
  default     = "us-west-2"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name"
  default     = "vigil-eks"
}

variable "node_instance_type" {
  type        = string
  description = "EC2 instance type for EKS nodes"
  default     = "t3.medium"
}

variable "node_count" {
  type        = number
  description = "Number of EKS nodes"
  default     = 2
}
