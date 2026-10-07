import pytest
from deceptionguard.cli.main import main
import sys
from unittest.mock import patch

def test_cli_scan(tmp_path, capsys):
    email_path = tmp_path / "test.eml"
    email_path.write_text("From: test@test.com\nTo: dest@test.com\nSubject: Test\n\nBody", encoding="utf-8")
    
    with patch.object(sys, "argv", ["dg", "scan", str(email_path)]):
        with patch("deceptionguard.intent_graph.extractor.extract_intent_graph", return_value={"urgency_pressure": True}):
            main()
    
    captured = capsys.readouterr()
    assert "Risk" in captured.out

def test_cli_evaluate(tmp_path, monkeypatch):
    import csv
    csv_path = tmp_path / "data.csv"
    with open(csv_path, "w") as f:
        f.write("text,label\n")
        f.write("test email,0\n")
        
    import deceptionguard.evaluation.run_evaluation as rev
    monkeypatch.setattr(rev, "run_evaluation_suite", lambda x: None)
    
    with patch.object(sys, "argv", ["dg", "evaluate", "--dataset", str(csv_path)]):
        main()

def test_cli_attack(tmp_path, monkeypatch):
    import csv
    csv_path = tmp_path / "data.csv"
    with open(csv_path, "w") as f:
        f.write("text,label\n")
        f.write("urgent verify account,1\n")
        
    import deceptionguard.evaluation.adversarial as adv
    monkeypatch.setattr(adv, "evaluate_robustness", lambda x, y: None)
    
    with patch.object(sys, "argv", ["dg", "evaluate", "--suite", "adversarial", "--dataset", str(csv_path)]):
        main()

def test_cli_serve(monkeypatch):
    import deceptionguard.ui.server as srv
    monkeypatch.setattr(srv, "run_server", lambda host, port: None)
    
    with patch.object(sys, "argv", ["dg", "serve"]):
        main()
