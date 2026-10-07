"""DeceptionGuard CLI — scan emails and run evaluations.

Entry point: `dg` (installed via pyproject.toml).
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_env() -> None:
    """Load environment variables from .env using our stdlib-only parser."""
    from deceptionguard.config import load_dotenv

    load_dotenv()


def scan_email(file_path: str) -> None:
    """Scan a single email file and print score + top factors."""
    from deceptionguard.evidence import detect_all
    from deceptionguard.ingestion.parser import parse_eml
    from deceptionguard.intent_graph.extractor import extract_intent_graph
    from deceptionguard.risk_engine.scorer import score_email

    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Parse email
    record = parse_eml(str(path))

    # Extract intent graph
    graph = extract_intent_graph(record)

    # Detect evidence
    evidence_list = detect_all(record)

    # Score
    result = score_email(graph, evidence_list)

    # Print results
    print(f"\n{'=' * 60}")
    print("DeceptionGuard Scan Results")
    print(f"{'=' * 60}")
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
    print("\nFactor Breakdown:")
    print(f"{'-' * 80}")
    print(f"  {'Factor Name':<30} | {'Category':<10} | {'Score'}")
    print(f"{'-' * 80}")
    for factor in result.factors:
        status = "TRIGGERED" if factor.contribution > 0 else "not triggered"
        print(f"  {factor.name:30s} | {factor.category:10s} | {factor.contribution:3d}/{factor.weight:3d}  {status}")

    # Show links found
    if record.links:
        print("\nLinks Found:")
        for link in record.links:
            print(f"  {link}")

    # Show intent graph summary
    print("\nIntent Graph Summary:")
    print(f"  Urgency Pressure: {graph.get('urgency_pressure', False)}")
    print(f"  Financial Request: {graph.get('financial_request', False)}")
    print(f"  Action Requested: {graph.get('action_requested') or '(none detected)'}")
    print(f"  Deception Tone: {graph.get('deception_tone') or '(none detected)'}")
    print(f"  Trust Abuse: {graph.get('trust_abuse') or '(none detected)'}")
    print(f"{'=' * 60}\n")


def evaluate_dataset(dataset_path: str) -> None:
    """Run evaluation on a dataset and generate report."""
    import sys


    path = Path(dataset_path)
    if not path.is_absolute():
        # Make it relative to current working directory
        path = Path.cwd() / path

    if not path.exists():
        print(f"Error: Dataset not found: {dataset_path}", file=sys.stderr)
        sys.exit(1)

    from deceptionguard.evaluation.run_evaluation import run_evaluation_suite
    try:
        run_evaluation_suite(dataset_path)
    except Exception as e:
        print(f"Evaluation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    _load_env()

    parser = argparse.ArgumentParser(
        prog="dg",
        description="DeceptionGuard — Email Security Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  dg scan email.eml
  dg evaluate --dataset data/processed/test.csv
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Scan subcommand
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a single email file",
        description="Scan a single email file for phishing indicators",
    )
    scan_parser.add_argument("file", help="Path to email file (.eml)")

    # Evaluate subcommand
    eval_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate system on dataset",
        description="Evaluate DeceptionGuard system on a labeled dataset"
    )
    eval_parser.add_argument("--dataset", required=True, help="Path to labeled dataset CSV")
    eval_parser.add_argument("--suite", choices=["standard", "full"], default="standard", help="Evaluation suite to run")

    # Serve subcommand
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the DeceptionGuard Console Web UI",
        description="Launch the local web UI for interactive analysis"
    )
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    serve_parser.add_argument("--port", type=int, default=8765, help="Port to bind to (default: 8765)")

    args = parser.parse_args()

    if args.command == "scan":
        scan_email(args.file)
    elif args.command == "evaluate":
        if args.suite == "full":
            from deceptionguard.evaluation.run_evaluation import run_evaluation_suite
            run_evaluation_suite(args.dataset)
        else:
            evaluate_dataset(args.dataset)
    elif args.command == "serve":
        from deceptionguard.ui.server import run_server
        run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
