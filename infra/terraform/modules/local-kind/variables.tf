variable "cluster_name" {
  type        = string
  description = "The name of the kind cluster."
  default     = "vigil-local"
}

variable "k8s_version" {
  type        = string
  description = "Kubernetes version for the kind cluster."
  default     = "v1.27.3"
}
