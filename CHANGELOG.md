# DeceptionGuard Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2026-10-07
### Added
- Standard Python package structure (`pyproject.toml`, `src/deceptionguard`).
- `config` module for typed configuration loading with `tomllib` and custom `.env` parser.
- `deceptionguard.cli.main:main` entry point as `dg`.

### Changed
- Removed core dependencies on `openai`, `pyyaml`, `python-dotenv`, `pandas`, and `scikit-learn` (`scikit-learn` and `pandas` kept as `dev` extras for baseline comparisons).
- Moved `weights.yaml` to `weights.toml` and changed parsing to `tomllib`.
- Updated test suites to reflect the new package structure and isolated dependencies.
