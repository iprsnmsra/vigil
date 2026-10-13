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
def install():
    """Install Vigil on a cluster."""
    console.print("[green]Installing Vigil on the cluster...[/green]")
    # Placeholder for actual install logic

@app.command()
def demo():
    """Run the local demo."""
    console.print("[green]Starting local Vigil demo...[/green]")
    # Placeholder for demo logic

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
