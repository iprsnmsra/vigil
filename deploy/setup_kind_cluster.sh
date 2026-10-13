#!/usr/bin/env bash
# Vigil Kubernetes Cluster Setup Script (Linux/macOS)
set -euo pipefail

echo "=========================================================="
echo "   VIGIL: Kubernetes Cluster & Platform Installer         "
echo "=========================================================="

CLUSTER_NAME="vigil-cluster"

# 1. Create kind cluster
if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "[OK] Kind cluster '${CLUSTER_NAME}' already exists."
else
    echo ">>> Creating kind cluster '${CLUSTER_NAME}'..."
    kind create cluster --name "${CLUSTER_NAME}"
fi

# 2. Add Helm repos
echo ">>> Adding Helm Repositories..."
helm repo add argo https://argoproj.github.io/argo-helm 2>/dev/null || true
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo update

# 3. Install ArgoCD
echo ">>> Installing ArgoCD..."
helm upgrade --install argocd argo/argo-cd \
    --namespace argocd --create-namespace \
    --set server.extraArgs="{--insecure}"

# 4. Install Argo Rollouts
echo ">>> Installing Argo Rollouts..."
helm upgrade --install argo-rollouts argo/argo-rollouts \
    --namespace argo-rollouts --create-namespace \
    --set dashboard.enabled=true

# 5. Install kube-prometheus-stack
echo ">>> Installing Prometheus & Alertmanager..."
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring --create-namespace \
    --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# 6. Deploy Vigil Platform
echo ">>> Deploying Vigil Platform (Controller & Flaky Detector)..."
helm upgrade --install vigil deploy/helm/vigil --namespace vigil --create-namespace

# 7. Apply Rollouts
echo ">>> Applying Argo Rollouts Canary manifests..."
kubectl apply -f deploy/rollouts/analysis-template.yaml -n default
kubectl apply -f deploy/rollouts/product-api-rollout.yaml -n default
kubectl apply -f deploy/rollouts/order-api-rollout.yaml -n default

echo "=========================================================="
echo "   VIGIL PLATFORM DEPLOYED SUCCESSFULLY!                  "
echo "=========================================================="
