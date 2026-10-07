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
| **Baseline Classifier** | Fast TF-IDF + LogisticRegression | scikit-learn (dev extra only) |
| **Intent Graph** | Extract structured intent from email | OpenAI-compatible API + Heuristic fallback |
| **Risk Engine** | Deterministic factor-based scoring | TOML-configurable weights |
| **Evaluation** | Compare baseline vs full pipeline | stdlib (baseline requires sklearn) |
| **CLI** | Scan emails & evaluate datasets | argparse (`dg` command) |

## Features

- **Robust Email Parsing**: Supports `.eml` and `.mbox` formats, robust handling of `multipart/alternative`, extracting URLs (anchor, href), attachments, and advanced headers (Authentication-Results, Received chain).
- **Text Normalization**: Extracts hidden text (CSS-hidden attack signals), normalizes to NFKC, and detects Bidi/zero-width controls.
- **Deterministic Evidence Layer**: Pure-Python, extensible detectors generating specific `Evidence` objects (e.g. `URL_IP_LITERAL`, `BRAND_TYPOSQUATTING`, `ATTACHMENT_EXECUTABLE`).
- **Brand Lookalike Detection**: Built-in Damerau-Levenshtein typosquatting detection for high-value targets.
- **Dual Detection**: ML baseline + Deterministic Evidence + LLM intent analysis using `litellm`
- **Pydantic Structural Validation**: Extracts verified signals for urgency, tone, financial intent, and trust abuse.
- **Offline-First**: Works without API keys using heuristic fallback
- **Configurable Risk Scoring**: TOML-based factor weights
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
# Linux/Mac: source venv/bin/activate
# Windows: venv\Scripts\activate

# Install package (with dev dependencies if needed for baseline)
pip install -e .
# Or pip install -e ".[dev]" to include scikit-learn for baselines
```

### Configuration (Optional)

For LLM-powered intent extraction, copy the example configuration file and add your NVIDIA API key:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your LLM API key
# DG_LLM_API_KEY=your_key_here
# DG_LLM_BASE_URL=https://api.openai.com/v1  # optional
# DG_LLM_MODEL=gpt-4                         # optional
```

The `.env` file is gitignored and will not be committed. The app automatically loads it via `python-dotenv` on startup.

> **Note:** Without an API key, DeceptionGuard runs fully offline using the heuristic fallback for intent extraction.

## Usage

### Scan a Single Email

```bash
# Scan an .eml file
dg scan tests/fixtures/phishing_email.eml

# Scan an .mbox file (processes all messages)
dg scan tests/fixtures/mixed_mbox.mbox
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
dg evaluate --dataset src/deceptionguard/data/processed/placeholder_test.csv
```

**Generates:** `src/evaluation/report.md` with detailed comparison.

## Project Structure

```
DeceptionGuard/
├── src/                          # Main source code
│   └── deceptionguard/           # Python package
│       ├── __init__.py
│       ├── config.py             # Typed configuration module
│       ├── ingestion/            # Email parsing
│       │   ├── __init__.py
│       │   ├── email_record.py   # EmailRecord dataclass
│       │   └── parser.py         # EML/MBOX parsers
│       ├── baseline/             # ML Classifier (optional)
│       │   ├── __init__.py
│       │   ├── classifier.py     # BaselineClassifier (TF-IDF + LR)
│       │   └── train_baseline.py # Training script with synthetic data
│       ├── intent_graph/         # LLM-based intent extraction
│       │   ├── __init__.py
│       │   ├── schema.py         # JSON schema + validation
│       │   └── extractor.py      # LLM + heuristic fallback
│       ├── risk_engine/          # Risk scoring
│       │   ├── __init__.py
│       │   ├── weights.toml      # Factor weights configuration
│       │   └── scorer.py         # Deterministic scoring logic
│       ├── evaluation/           # Evaluation harness
│       │   ├── __init__.py
│       │   └── run_evaluation.py # Baseline vs pipeline comparison
│       ├── cli/                  # Command-line interface
│       │   ├── __init__.py
│       │   └── main.py           # scan & evaluate commands
│       └── data/                 # Synthetic placeholder data
│           ├── raw/
│           └── processed/
├── tests/                        # Unit tests
├── pyproject.toml                # Package metadata and dependencies
├── scripts/                      # Helper scripts (pre_push_check)
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

The risk engine uses 5 factors (configurable via TOML or in `src/deceptionguard/risk_engine/weights.toml`):

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
python -m deceptionguard.baseline.train_baseline
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

### Risk Weights (`src/deceptionguard/risk_engine/weights.toml`)
```toml
[factor_weights]
claimed_identity_mismatch = 25
urgency_high = 30
authority_spoof = 20
payload_links = 15
action_request = 10
```

### LLM API Configuration
Configured via `.env` file or environment variables:
```env
DG_LLM_API_KEY=your_key_here
DG_LLM_BASE_URL=https://integrate.api.nvidia.com/v1
DG_LLM_MODEL=openai/gpt-oss-20b
```

## Dependencies

Core pipeline has **zero** third-party dependencies and runs entirely on the Python 3.11+ standard library.

Optional `[dev]` dependencies (for baselines and testing):
```
pytest>=7.0.0
ruff>=0.4.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
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