# DeceptionGuard - Email Security Analysis Tool

## Overview

DeceptionGuard is a local-first Python tool for analyzing emails and detecting phishing attempts using a combination of machine learning and LLM-based intent analysis. It operates entirely offline (except for optional LLM API calls) and provides a CLI for scanning individual emails or evaluating datasets.

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

### Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Ingestion** | Parse .eml and .mbox files | Python stdlib `email` |
| **Baseline Classifier** | Fast TF-IDF + LogisticRegression | scikit-learn |
| **Intent Graph** | Extract structured intent from email | NVIDIA LLM (gpt-oss-20b) + Heuristic fallback |
| **Risk Engine** | Deterministic factor-based scoring | YAML-configurable weights |
| **Evaluation** | Compare baseline vs full pipeline | scikit-learn metrics |
| **CLI** | Scan emails & evaluate datasets | argparse |

## Features

- **Email Parsing**: Supports `.eml` and `.mbox` formats
- **Dual Detection**: ML baseline + LLM intent analysis
- **Offline-First**: Works without API keys using heuristic fallback
- **Configurable Risk Scoring**: YAML-based factor weights
- **Comprehensive Evaluation**: Baseline vs pipeline comparison with subtype breakdown
- **CLI Interface**: `scan` and `evaluate` commands

## Quick Start

### Installation

```bash
# Clone and enter
git clone https://github.com/Swayam-Swaroop-Sahu/DeceptionGuard
cd DeceptionGuard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration (Optional)

For LLM-powered intent extraction, set the NVIDIA API key:

```bash
export NVIDIA_API_KEY="<Enter API Key>"
```

## Usage

### Scan a Single Email

```bash
# Scan an .eml file
python -m src.cli.main scan tests/fixtures/phishing_email.eml

# Scan an .mbox file (processes all messages)
python -m src.cli.main scan tests/fixtures/mixed_mbox.mbox
```

**Output Example:**
```
============================================================
DeceptionGuard Scan Results
============================================================
File: tests/fixtures/phishing_email.eml
Sender: Security Team <security@payroll-services.xyz>
Subject: URGENT: Your Account Has Been Compromised!
Date: Tue, 16 Jan 2024 08:15:00 +0000

Risk Score: 100/100
Risk Level: HIGH

Factor Breakdown:
------------------------------------------------------------
  claimed_identity_mismatch       25/ 25  TRIGGERED
  urgency_high                    30/ 30  TRIGGERED
  authority_spoof                 20/ 20  TRIGGERED
  payload_links                   15/ 15  TRIGGERED
  action_request                  10/ 10  TRIGGERED

Links Found:
  https://verify-account-now.malicious-site.com/login?token=abc123

Intent Graph Summary:
  Claimed Identity: Security Team
  Requested Action: Verify identity by clicking the provided link
  Urgency Signals: URGENT, Immediate action required, 24 hours
  Authority Signals: Security Team, Security Department
  Payload Targets: https://verify-account-now.malicious-site.com/login?token=abc123
============================================================
```

### Evaluate on Dataset

```bash
# Run evaluation on test dataset
python -m src.cli.main evaluate --dataset src/data/processed/placeholder_test.csv
```

**Generates:** `src/evaluation/report.md` with detailed comparison.

## Project Structure

```
DeceptionGuard/
├── src/                          # Main source code
│   ├── __init__.py
│   ├── ingestion/                # Email parsing
│   │   ├── __init__.py
│   │   ├── email_record.py       # EmailRecord dataclass
│   │   └── parser.py             # EML/MBOX parsers
│   ├── baseline/                 # ML Classifier
│   │   ├── __init__.py
│   │   ├── classifier.py         # BaselineClassifier (TF-IDF + LR)
│   │   └── train_baseline.py     # Training script with synthetic data
│   ├── intent_graph/             # LLM-based intent extraction
│   │   ├── __init__.py
│   │   ├── schema.py             # JSON schema + validation
│   │   └── extractor.py          # NVIDIA LLM + heuristic fallback
│   ├── risk_engine/              # Risk scoring
│   │   ├── __init__.py
│   │   ├── weights.yaml          # Factor weights configuration
│   │   └── scorer.py             # Deterministic scoring logic
│   ├── evaluation/               # Evaluation harness
│   │   ├── __init__.py
│   │   └── run_evaluation.py     # Baseline vs pipeline comparison
│   ├── cli/                      # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py               # scan & evaluate commands
│   └── data/
│       ├── raw/                  # Raw emails (gitignored)
│       └── processed/            # Processed datasets
│           ├── placeholder_train.csv
│           └── placeholder_test.csv
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_ingestion.py
│   ├── test_baseline.py
│   ├── test_intent_graph.py
│   ├── test_risk_engine.py
│   ├── test_evaluation.py
│   ├── test_cli.py
│   └── fixtures/
│       ├── __init__.py
│       ├── legit_email.eml
│       ├── phishing_email.eml
│       └── mixed_mbox.mbox
├── requirements.txt
├── .gitignore
└── README.md
```

## Risk Scoring Factors

The risk engine uses 5 factors (configurable in `src/risk_engine/weights.yaml`):

| Factor | Weight | Description |
|--------|--------|-------------|
| `claimed_identity_mismatch` | 25 | Sender claims to be security/support/admin |
| `urgency_high` | 30 | Urgency keywords (urgent, immediate, 24h, deadline) |
| `authority_spoof` | 20 | Authority impersonation (bank, IRS, Microsoft, etc.) |
| `payload_links` | 15 | Suspicious links (verify, login, account, secure) |
| `action_request` | 10 | Explicit action requests (click, verify, update) |

**Score Range:** 0-100
- **0-10**: MINIMAL
- **11-39**: LOW
- **40-69**: MEDIUM
- **70-100**: HIGH

## Intent Graph Schema

```json
{
  "claimed_identity": "string|null",
  "requested_action": "string|null",
  "urgency_signals": ["string"],
  "authority_signals": ["string"],
  "payload_targets": ["string"]
}
```

Extracted via:
1. **NVIDIA LLM** (gpt-oss-20b) - Primary
2. **Heuristic Fallback** - Keyword-based, no API needed

## Training the Baseline

```bash
# Generates synthetic data and trains TF-IDF + LogisticRegression
python -m src.baseline.train_baseline
```

**Output:**
```
Baseline Classifier Results:
Test F1 Score: 0.7143
Test Samples: 12
```

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific module
python -m pytest tests/test_ingestion.py -v
python -m pytest tests/test_intent_graph.py -v
python -m pytest tests/test_cli.py -v
```

**Current Results:** 31 tests passing

## Configuration Files

### Risk Weights (`src/risk_engine/weights.yaml`)
```yaml
factor_weights:
  claimed_identity_mismatch: 25
  urgency_high: 30
  authority_spoof: 20
  payload_links: 15
  action_request: 10
```

### NVIDIA API (`src/intent_graph/extractor.py`)
```python
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "default-key")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "openai/gpt-oss-20b"
```

## Dependencies

```
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
pyyaml>=6.0
pytest>=7.0.0
openai>=1.0.0
```

## Known Limitations

| Limitation | Status |
|------------|--------|
| LLM requires internet for NVIDIA API | Fallback available |
| Training data is synthetic | Replace with real data for production |
| MBOX parsing is basic | Not fully RFC-compliant |
| Timezone handling limited | Uses email date as-is |
| Single-threaded evaluation | Could be parallelized |

## Extending the Project

### Add New Risk Factors
1. Update `src/risk_engine/weights.yaml`
2. Add detection logic in `src/risk_engine/scorer.py`

### Swap LLM Provider
Modify `src/intent_graph/extractor.py`:
- Replace `_call_nvidia_llm()` with your provider
- Keep `_fallback_extract()` for offline support

### Add Email Format Support
Extend `src/ingestion/parser.py` with new parsing functions.

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request