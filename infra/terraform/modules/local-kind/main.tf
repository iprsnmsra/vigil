resource "null_resource" "kind_cluster" {
  provisioner "local-exec" {
    command = "kind create cluster --name ${var.cluster_name} --image kindest/node:${var.k8s_version}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kind delete cluster --name ${self.triggers.cluster_name}"
  }

  triggers = {
    cluster_name = var.cluster_name
  }
}
