import subprocess
import shutil

def check_docker() -> bool:
    """Checks if Docker is installed and running."""
    return shutil.which("docker") is not None

def check_kubectl() -> bool:
    """Checks if kubectl is installed."""
    return shutil.which("kubectl") is not None

def check_kind() -> bool:
    """Checks if kind is installed."""
    return shutil.which("kind") is not None

def check_helm() -> bool:
    """Checks if helm is installed."""
    return shutil.which("helm") is not None
