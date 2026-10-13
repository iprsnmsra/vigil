from typer.testing import CliRunner
from vigil_cli.main import app
from unittest.mock import patch

runner = CliRunner()

def test_init():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Initializing Vigil project structure" in result.stdout

def test_doctor():
    with patch('vigil_cli.main.check_docker', return_value=True), \
         patch('vigil_cli.main.check_kubectl', return_value=True), \
         patch('vigil_cli.main.check_kind', return_value=True), \
         patch('vigil_cli.main.check_helm', return_value=True):
        
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "All prerequisites met!" in result.stdout
