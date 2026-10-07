# DeceptionGuard Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
