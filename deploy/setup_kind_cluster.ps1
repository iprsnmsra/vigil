# Vigil Kubernetes Cluster Setup Script (Windows PowerShell)
# Creates a local kind cluster and installs ArgoCD, Argo Rollouts, Prometheus, and Vigil

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   VIGIL: Kubernetes Cluster & Platform Installer         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Preflight checks
$missing = @()
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { $missing += "Docker (Start Docker Desktop)" }
if (-not (Get-Command kind -ErrorAction SilentlyContinue)) { $missing += "kind (Install: winget install Kubernetes.kind)" }
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) { $missing += "kubectl (Install: winget install Kubernetes.kubectl)" }
if (-not (Get-Command helm -ErrorAction SilentlyContinue)) { $missing += "helm (Install: winget install Helm.Helm)" }

if ($missing.Count -gt 0) {
    Write-Host "`n[!] Missing prerequisites for local Kubernetes:" -ForegroundColor Yellow
    foreach ($m in $missing) {
        Write-Host "    - $m" -ForegroundColor Red
    }
    Write-Host "`nQuick install via Windows winget:" -ForegroundColor Cyan
    Write-Host "    winget install Kubernetes.kind"
    Write-Host "    winget install Kubernetes.kubectl"
    Write-Host "    winget install Helm.Helm"
    Write-Host "`nEnsure Docker Desktop is running, then re-run this script." -ForegroundColor Yellow
    exit 1
}

# 2. Create kind cluster
$clusterName = "vigil-cluster"
$existingClusters = kind get clusters 2>$null
if ($existingClusters -contains $clusterName) {
    Write-Host "`n[OK] Kind cluster '$clusterName' already exists." -ForegroundColor Green
} else {
    Write-Host "`n>>> Creating kind cluster '$clusterName'..." -ForegroundColor Cyan
    kind create cluster --name $clusterName
}

# 3. Add Helm repos
Write-Host "`n>>> Adding Helm Repositories..." -ForegroundColor Cyan
helm repo add argo https://argoproj.github.io/argo-helm 2>$null
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>$null
helm repo update

# 4. Install ArgoCD
Write-Host "`n>>> Installing ArgoCD..." -ForegroundColor Cyan
helm upgrade --install argocd argo/argo-cd `
    --namespace argocd --create-namespace `
    --set server.extraArgs="{--insecure}"

# 5. Install Argo Rollouts
Write-Host "`n>>> Installing Argo Rollouts..." -ForegroundColor Cyan
helm upgrade --install argo-rollouts argo/argo-rollouts `
    --namespace argo-rollouts --create-namespace `
    --set dashboard.enabled=true

# 6. Install kube-prometheus-stack
Write-Host "`n>>> Installing Prometheus & Alertmanager..." -ForegroundColor Cyan
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack `
    --namespace monitoring --create-namespace `
    --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# 7. Deploy Vigil Platform
Write-Host "`n>>> Deploying Vigil Platform (Controller & Flaky Detector)..." -ForegroundColor Cyan
$helmPath = Join-Path $PSScriptRoot "helm\vigil"
helm upgrade --install vigil $helmPath --namespace vigil --create-namespace

# 8. Deploy Demo Applications & Canary Rollouts
Write-Host "`n>>> Applying Argo Rollouts Canary manifests..." -ForegroundColor Cyan
$rolloutsPath = Join-Path $PSScriptRoot "rollouts"
kubectl apply -f "$rolloutsPath\analysis-template.yaml" -n default
kubectl apply -f "$rolloutsPath\product-api-rollout.yaml" -n default
kubectl apply -f "$rolloutsPath\order-api-rollout.yaml" -n default

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "   VIGIL PLATFORM DEPLOYED SUCCESSFULLY!                  " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "ArgoCD UI:        kubectl port-forward svc/argocd-server -n argocd 8080:443"
Write-Host "Argo Rollouts UI: kubectl argo rollouts dashboard"
Write-Host "Prometheus UI:    kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090"
Write-Host "Vigil Controller: kubectl port-forward svc/vigil-controller -n vigil 8083:8080"
