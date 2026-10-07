# DeceptionGuard QA Baseline Report (Phase Q0)

## Inventory
- **Source LOC**: ~2923 lines of Python in `src/deceptionguard/`
- **Modules**:
  - `config.py`
  - `baseline` (classifier, train_baseline)
  - `cli` (main)
  - `data` (loaders, split)
  - `evaluation` (adversarial, metrics, run_evaluation)
  - `evidence` (detectors, schema)
  - `ingestion` (email_record, html_parser, normalize, parser)
  - `intent_graph` (extractor, schema)
  - `risk_engine` (scorer)
  - `ui` (server, static assets)

## Findings

| ID | Severity | Area | Description |
|---|---|---|---|
| Q0-1 | S2 | Dependencies | Non-stdlib imports (`litellm`, `pydantic`, `sklearn`, `numpy`, `scipy`) are hard-coded in core logic (`intent_graph`, `evidence`, `baseline`, `evaluation`). If missing, the app crashes rather than gracefully degrading. |
| Q0-2 | S3 | Tests | Tests run cleanly (48 tests in ~26 seconds) but coverage is not verified to be >=85% yet. |
| Q0-3 | S2 | Edge Cases | The ingestion parser lacks comprehensive edge-case handling (null bytes, deeply nested multipart) proven via fuzzing. |
| Q0-4 | S3 | UI Security | Need to verify rate limiting, strict CSP defaults, path traversal protection, CSRF in `server.py`. |

## Next Steps
Proceeding to **Phase Q1: Test Strategy and Coverage** and addressing Q0-1 (Zero-dependency violations) to ensure core stays standard-library only.
