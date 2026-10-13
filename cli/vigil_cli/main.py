import typer
from rich.console import Console
from .checks import check_docker, check_kubectl, check_kind, check_helm

app = typer.Typer(help="Vigil CLI - Self-healing CI/CD platform")
console = Console()

@app.command()
def init():
    """Initialize Vigil in a project."""
    console.print("[green]Initializing Vigil project structure...[/green]")
    # Placeholder for actual init logic

@app.command()
def install(
    cluster_name: str = typer.Option("vigil-cluster", "--cluster-name", help="Name of the kind cluster to create/target"),
):
    """Install Vigil on a Kubernetes cluster (ArgoCD, Argo Rollouts, Prometheus, Helm)."""
    import shutil
    import subprocess
    import sys
    import os

    console.print(f"[bold cyan]>>> Starting Vigil Kubernetes Cluster Installer (Cluster: {cluster_name})...[/bold cyan]")
    
    missing = []
    if not shutil.which("docker"):
        missing.append("Docker (Ensure Docker Desktop is installed and running)")
    if not shutil.which("kind"):
        missing.append("kind (Install: winget install Kubernetes.kind)")
    if not shutil.which("kubectl"):
        missing.append("kubectl (Install: winget install Kubernetes.kubectl)")
    if not shutil.which("helm"):
        missing.append("helm (Install: winget install Helm.Helm)")

    if missing:
        console.print("\n[bold red][MISSING PREREQUISITES][/bold red]")
        for m in missing:
            console.print(f"  [red]-[/red] {m}")
        console.print("\n[yellow]To install quickly on Windows PowerShell:[/yellow]")
        console.print("  [bold white]winget install Kubernetes.kind Kubernetes.kubectl Helm.Helm[/bold white]")
        console.print("  [dim]After installing, launch Docker Desktop and run 'vigil install' again.[/dim]")
        console.print(f"[cyan]Automated setup script is ready at:[/cyan] deploy/setup_kind_cluster.ps1\n")
        raise typer.Exit(code=1)

    script = "setup_kind_cluster.ps1" if sys.platform == "win32" else "setup_kind_cluster.sh"
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "deploy", script))
    
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path] if sys.platform == "win32" else ["bash", script_path]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise typer.Exit(code=res.returncode)

@app.command()
def demo(
    bad_release: bool = typer.Option(False, "--bad-release", help="Simulate a failing canary release to demonstrate auto-rollback"),
):
    """Run the local demo of Vigil's self-healing platform."""
    import subprocess
    import sys
    import os
    
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "live_demo.py"))
    cmd = [sys.executable, script_path]
    if bad_release:
        cmd.append("--bad-release")
    subprocess.run(cmd)

@app.command()
def status():
    """Show status of Vigil components."""
    console.print("[green]Checking Vigil component status...[/green]")
    # Placeholder for status logic

@app.command()
def doctor():
    """Check prerequisites (Docker, kubectl, kind, helm)."""
    console.print("Checking prerequisites for Vigil...")
    
    checks = [
        ("Docker", check_docker()),
        ("kubectl", check_kubectl()),
        ("kind", check_kind()),
        ("Helm", check_helm())
    ]
    
    all_passed = True
    for name, passed in checks:
        if passed:
            console.print(f"[green][OK][/green] {name} is installed")
        else:
            console.print(f"[red][MISSING][/red] {name} is missing")
            all_passed = False
            
    if all_passed:
        console.print("\n[bold green]All prerequisites met![/bold green]")
    else:
        console.print("\n[bold red]Please install missing prerequisites.[/bold red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
