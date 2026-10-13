module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.27"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_group_defaults = {
    instance_types = [var.node_instance_type]
  }

  eks_managed_node_groups = {
    default = {
      min_size     = var.node_count
      max_size     = var.node_count
      desired_size = var.node_count
    }
  }
}
