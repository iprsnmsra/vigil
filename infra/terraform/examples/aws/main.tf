provider "aws" {
  region = var.region
}

module "eks_cluster" {
  source = "../../modules/aws-eks"

  region             = var.region
  cluster_name       = var.cluster_name
  node_instance_type = var.node_instance_type
  node_count         = var.node_count
}
