import argparse
import sys
from pathlib import Path


def scan_email(file_path: str):
    """Scan a single email file and print score + top factors."""
    from src.ingestion.parser import parse_eml
    from src.intent_graph.extractor import extract_intent_graph
    from src.risk_engine.scorer import score_graph
    
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse email
    record = parse_eml(str(path))
    
    # Extract intent graph
    graph = extract_intent_graph(record)
    
    # Score
    result = score_graph(graph)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"DeceptionGuard Scan Results")
    print(f"{'='*60}")
    print(f"File: {file_path}")
    print(f"Sender: {record.sender}")
    print(f"Subject: {record.subject or '(no subject)'}")
    print(f"Date: {record.date or '(unknown)'}")
    print(f"\nRisk Score: {result.total_score}/100")
    
    if result.total_score >= 70:
        risk_level = "HIGH"
    elif result.total_score >= 40:
        risk_level = "MEDIUM"
    elif result.total_score > 0:
        risk_level = "LOW"
    else:
        risk_level = "MINIMAL"
    
    print(f"Risk Level: {risk_level}")
    print(f"\nFactor Breakdown:")
    print(f"{'-'*60}")
    
    for factor in result.factors:
        status = "TRIGGERED" if factor.contribution > 0 else "not triggered"
        print(f"  {factor.name:30s} {factor.contribution:3d}/{factor.weight:3d}  {status}")
    
    # Show links found
    if record.links:
        print(f"\nLinks Found:")
        for link in record.links:
            print(f"  {link}")
    
    # Show intent graph summary
    print(f"\nIntent Graph Summary:")
    print(f"  Claimed Identity: {graph['claimed_identity'] or '(none detected)'}")
    print(f"  Requested Action: {graph['requested_action'] or '(none detected)'}")
    print(f"  Urgency Signals: {', '.join(graph['urgency_signals']) if graph['urgency_signals'] else '(none)'}")
    print(f"  Authority Signals: {', '.join(graph['authority_signals']) if graph['authority_signals'] else '(none)'}")
    print(f"  Payload Targets: {', '.join(graph['payload_targets']) if graph['payload_targets'] else '(none)'}")
    print(f"{'='*60}\n")


def evaluate_dataset(dataset_path: str):
    """Run evaluation on a dataset and generate report."""
    import subprocess
    
    path = Path(dataset_path)
    if not path.is_absolute():
        # Make it relative to current working directory
        path = Path.cwd() / path
    
    if not path.exists():
        print(f"Error: Dataset not found: {dataset_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Running evaluation on {path}...")
    
    # Run the evaluation module
    result = subprocess.run([
        sys.executable, "-m", "src.evaluation.run_evaluation"
    ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"Evaluation failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(1)
    
    # Check for report
    report_path = Path(__file__).parent.parent / "evaluation" / "report.md"
    if report_path.exists():
        print(f"\nReport generated: {report_path}")
    else:
        print("Warning: Report file not found", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="DeceptionGuard Email Security Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m cli.main scan email.eml
  python -m cli.main evaluate --dataset data/processed/test.csv
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Scan subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan a single email file", description="Scan a single email file for phishing indicators")
    scan_parser.add_argument("file", help="Path to email file (.eml)")
    
    # Evaluate subcommand
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate system on dataset", description="Evaluate DeceptionGuard system on a labeled dataset")
    eval_parser.add_argument("--dataset", required=True, help="Path to labeled dataset CSV")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        scan_email(args.file)
    elif args.command == "evaluate":
        evaluate_dataset(args.dataset)


if __name__ == "__main__":
    main()