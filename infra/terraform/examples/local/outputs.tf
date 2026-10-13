output "cluster_name" {
  value       = module.kind_cluster.cluster_name
}

output "kubeconfig_path" {
  value       = module.kind_cluster.kubeconfig_path
}
