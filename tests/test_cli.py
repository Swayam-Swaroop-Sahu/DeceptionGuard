import sys
from unittest.mock import patch

import pytest

from deceptionguard.cli.main import main


def run_cli_with_capsys(capsys, *args):
    """Run CLI command and return stdout/stderr."""
    with patch.object(sys, "argv", ["dg"] + list(args)):
        try:
            main()
            returncode = 0
        except SystemExit as e:
            returncode = e.code if e.code is not None else 0

    captured = capsys.readouterr()
    return type("Result", (), {"returncode": returncode, "stdout": captured.out, "stderr": captured.err})


def test_cli_scan_legit_email(capsys):
    """Test scan command on legitimate email."""
    result = run_cli_with_capsys(capsys, "scan", "tests/fixtures/legit_email.eml")

    assert result.returncode == 0
    assert "DeceptionGuard Scan Results" in result.stdout
    assert "john.doe@company.com" in result.stdout
    assert "Quarterly Report" in result.stdout


def test_cli_scan_phishing_email(capsys):
    """Test scan command on phishing email."""
    result = run_cli_with_capsys(capsys, "scan", "tests/fixtures/phishing_email.eml")

    assert result.returncode == 0
    assert "DeceptionGuard Scan Results" in result.stdout
    assert "security@payroll-services.xyz" in result.stdout
    assert "URGENT" in result.stdout
    assert "malicious-site.com" in result.stdout


def test_cli_scan_nonexistent_file(capsys):
    """Test scan command on nonexistent file."""
    result = run_cli_with_capsys(capsys, "scan", "nonexistent.eml")

    assert result.returncode == 1
    assert "File not found" in result.stderr


def test_cli_evaluate_dataset(capsys):
    """Test evaluate command with dataset."""
    result = run_cli_with_capsys(capsys, "evaluate", "--dataset", "src/deceptionguard/data/processed/placeholder_test.csv")

    assert result.returncode == 0
    assert "Baseline F1" in result.stdout or "Evaluation Report" in result.stdout


def test_cli_evaluate_nonexistent_dataset(capsys):
    """Test evaluate command with nonexistent dataset."""
    result = run_cli_with_capsys(capsys, "evaluate", "--dataset", "nonexistent.csv")

    assert result.returncode == 1
    assert "Dataset not found" in result.stderr


def test_cli_help(capsys):
    """Test help command."""
    result = run_cli_with_capsys(capsys, "--help")

    assert result.returncode == 0
    assert "DeceptionGuard" in result.stdout
    assert "scan" in result.stdout


def test_cli_scan_help(capsys):
    """Test scan subcommand help."""
    result = run_cli_with_capsys(capsys, "scan", "--help")

    assert result.returncode == 0
    assert "Scan a single email file" in result.stdout


def test_cli_evaluate_help(capsys):
    """Test evaluate subcommand help."""
    result = run_cli_with_capsys(capsys, "evaluate", "--help")

    assert result.returncode == 0
    assert "Evaluate" in result.stdout
    assert "--dataset" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
