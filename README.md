# DeceptionGuard - Email Security Analysis Tool

## Overview
DeceptionGuard is a local-first Python tool for analyzing emails and detecting phishing attempts using a combination of machine learning and LLM-based intent analysis.

## Architecture
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Ingestion   │────▶│ Baseline     │────▶│ Risk        │
│ (Email)     │     │ Classifier   │     │ Engine      │
└─────────────┘     └──────────────┘     └─────────────┘
      │                   │                   │
      ▼                   ▼                   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Intent      │────▶│ Risk         │────▶│ CLI /       │
│ Graph       │     │ Scoring      │     │ Evaluation  │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`

## Usage

### Scan a single email
```bash
python -m deceptionguard.cli.main scan email.eml
```

### Evaluate on dataset
```bash
python -m deceptionguard.cli.main evaluate --dataset data/processed/test.csv
```

## Project Structure
```
deceptionguard/
├── ingestion/        # Email parsing (EML, MBOX)
│   ├── email_record.py   # EmailRecord dataclass
│   └── parser.py         # EML/MBOX parsers
├── baseline/         # TF-IDF + LogisticRegression classifier
│   ├── classifier.py     # BaselineClassifier
│   └── train_baseline.py # Training script with placeholder data
├── intent_graph/     # LLM-based intent extraction
│   ├── schema.py         # JSON schema for intent graph
│   └── extractor.py      # LLM extraction (placeholder)
├── risk_engine/      # Deterministic risk scoring
│   ├── weights.yaml      # Factor weights configuration
│   └── scorer.py         # Risk scoring logic
├── evaluation/       # Evaluation harness
│   └── run_evaluation.py # Baseline vs system comparison
├── cli/              # Command-line interface
│   └── main.py         # scan and evaluate commands
├── data/
│   ├── raw/              # Raw email files (gitignored)
│   └── processed/        # Processed datasets (gitignored except placeholders)
└── tests/            # Unit tests for all modules
```

## Requirements
- Python 3.11+
- Dependencies in `requirements.txt`

## Known Limitations / Placeholder Data
- LLM integration in `intent_graph/extractor.py` is currently a placeholder (requires API key in environment: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`)
- Training data in `data/processed/` is synthetic placeholder
- Real-world dataset needed for production use
- Timezone handling in date parsing is limited
- MBOX parsing is basic (not fully RFC-compliant)

## Development
Run tests:
```bash
pytest tests/ -v
```

Train baseline classifier:
```bash
python -m deceptionguard.baseline.train_baseline
```

Run evaluation:
```bash
python -m deceptionguard.evaluation.run_evaluation
```

## License
MIT License