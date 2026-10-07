# DeceptionGuard Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2026-10-07
### Added
- Phase 7: Adversarial Robustness Suite.
- `src/deceptionguard/evaluation/adversarial.py` to mutate emails (homoglyphs, zero-width spaces, typos) and evaluate pipeline resilience.
- `--suite adversarial` in `dg evaluate` to compute robustness degradation.

## [0.8.0] - 2026-10-07
### Added
- Phase U2: Batch & Evaluation UI.
- Evaluation tab in Web UI to render metrics and ablations from `results/summary.json`.
- Internal API `/api/v1/results/` to serve evaluation artifacts locally to the frontend.

## [0.7.0] - 2026-10-07
### Added
- Phase 6: Datasets and Evaluation Protocol.
- `src/deceptionguard/data/loaders.py` for standardizing dataset loads (Enron, SpamAssassin, Nazario).
- `src/deceptionguard/data/split.py` for k-shingle deduplication and splitting strategies.
- `src/deceptionguard/evaluation/metrics.py` for computing ECE, bootstrap CIs, PR-AUC, and McNemar test.
- `--suite full` for `dg evaluate` to run all ablations and output JSON(L) to `results/`.
- `docs/DATASETS.md` documenting datasets and evaluation setup.

## [0.6.0] - 2026-10-07
### Added
- Phase U1: Web UI Foundation & Analyze Page.
- Professional consulting-grade web UI with deep forest green styling.
- Local stdlib-only HTTP server (`dg serve`) with strict CSP and CSRF protection.
- REST API endpoint `/api/v1/analyze` for JSON analysis output.
- Interactive web UI for dropping/pasting EML files with risk gauge, factor waterfall, and evidence list.

## [0.5.0] - 2026-10-07
### Added
- Phase 5: Baseline ML Isolation & Metrics.
- Completely isolated baseline classifier into an optional `[dev]` dependency using scikit-learn.
- Baseline training script now automatically computes precision, recall, and F1, and saves to `metrics.json`.
- Safely handles missing scikit-learn dependencies.

## [0.4.0] - 2026-10-07
### Added
- Phase 4: Risk Engine Rewrite.
- Rewrote `scorer.py` to accept and score both `IntentGraph` and `Evidence` lists simultaneously.
- Split `weights.toml` into `[intent_weights]` and `[evidence_weights]`.
- Implemented category-aware `FactorContribution` (intent vs. evidence).
- Capped max risk score at 100.
- `dg scan` and evaluation pipelines now use the combined Evidence + Intent scoring.

## [0.3.0] - 2026-10-07
### Added
- Phase 3: Intent Graph Overhaul.
- Replaced `openai` SDK with `litellm` for standardized, multi-model API access.
- Implemented robust `Pydantic` schema (`IntentGraph`) for deterministic structural validation.
- Extracted psychological factors: `urgency_pressure`, `financial_request`, `action_requested`, `deception_tone`, and `trust_abuse`.
- Fallback heuristic regex/keyword rules for all new Pydantic schema fields for offline reliability.

## [0.2.0] - 2026-10-07
### Added
- Phase 2: Deterministic Evidence Layer.
- `Evidence` schema defining specific, serializable risks (type, severity, explanation, span).
- Sender/Domain mismatch detectors (Display Name spoofing, Reply-To discrepancies).
- Comprehensive URL detectors (IP-literals, shorteners, punycode/IDN, lookalikes).
- Brand lookalike detection using Damerau-Levenshtein and a built-in JSON target list.
- Attachment and Authentication risk detectors.

## [0.1.0] - 2026-10-07
### Added
- Robust ingestion pipeline using Python's `email` and `mailbox` standard libraries.
- HTML to text parser isolating visible vs hidden text.
- Advanced URL extraction storing anchor text and href pairs.
- Extract advanced headers: Message-ID, Received chain, Authentication-Results.
- Advanced attachment parsing: size, mime type mismatches, and double extensions.
- Text normalization: NFKC standard, extraction of Bidi and Zero-width characters.
- Fuzzing suite for the ingestion parser.

## [0.0.1] - 2026-10-07
### Added
- Standard Python package structure (`pyproject.toml`, `src/deceptionguard`).
- `config` module for typed configuration loading with `tomllib` and custom `.env` parser.
- `deceptionguard.cli.main:main` entry point as `dg`.

### Changed
- Removed core dependencies on `openai`, `pyyaml`, `python-dotenv`, `pandas`, and `scikit-learn` (`scikit-learn` and `pandas` kept as `dev` extras for baseline comparisons).
- Moved `weights.yaml` to `weights.toml` and changed parsing to `tomllib`.
- Updated test suites to reflect the new package structure and isolated dependencies.
