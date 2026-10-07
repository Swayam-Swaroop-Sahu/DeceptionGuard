import pytest
import subprocess
import sys
from pathlib import Path


def run_cli(*args):
    """Run CLI command and return result."""
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main"] + list(args),
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    return result


def test_cli_scan_legit_email():
    """Test scan command on legitimate email."""
    result = run_cli("scan", "tests/fixtures/legit_email.eml")
    
    assert result.returncode == 0
    assert "DeceptionGuard Scan Results" in result.stdout
    assert "john.doe@company.com" in result.stdout
    assert "Quarterly Report" in result.stdout


def test_cli_scan_phishing_email():
    """Test scan command on phishing email."""
    result = run_cli("scan", "tests/fixtures/phishing_email.eml")
    
    assert result.returncode == 0
    assert "DeceptionGuard Scan Results" in result.stdout
    assert "security@payroll-services.xyz" in result.stdout
    assert "URGENT" in result.stdout
    assert "malicious-site.com" in result.stdout


def test_cli_scan_nonexistent_file():
    """Test scan command on nonexistent file."""
    result = run_cli("scan", "nonexistent.eml")
    
    assert result.returncode == 1
    assert "File not found" in result.stderr


def test_cli_evaluate_dataset():
    """Test evaluate command with dataset."""
    result = run_cli("evaluate", "--dataset", "src/data/processed/placeholder_test.csv")
    
    assert result.returncode == 0
    assert "Baseline F1" in result.stdout or "Evaluation Report" in result.stdout


def test_cli_evaluate_nonexistent_dataset():
    """Test evaluate command with nonexistent dataset."""
    result = run_cli("evaluate", "--dataset", "nonexistent.csv")
    
    assert result.returncode == 1
    assert "Dataset not found" in result.stderr


def test_cli_help():
    """Test help command."""
    result = run_cli("--help")
    
    assert result.returncode == 0
    assert "DeceptionGuard Email Security Analyzer" in result.stdout
    assert "scan" in result.stdout
    assert "evaluate" in result.stdout


def test_cli_scan_help():
    """Test scan subcommand help."""
    result = run_cli("scan", "--help")
    
    assert result.returncode == 0
    assert "Scan a single email file" in result.stdout


def test_cli_evaluate_help():
    """Test evaluate subcommand help."""
    result = run_cli("evaluate", "--help")
    
    assert result.returncode == 0
    assert "Evaluate DeceptionGuard system" in result.stdout
    assert "--dataset" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])