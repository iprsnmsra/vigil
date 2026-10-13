output "cluster_name" {
  value       = var.cluster_name
  description = "The name of the kind cluster."
}

output "kubeconfig_path" {
  value       = "~/.kube/config"
  description = "Path to the kubeconfig file."
}
