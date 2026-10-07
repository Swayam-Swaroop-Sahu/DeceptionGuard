# Assumptions

This file documents underlying assumptions regarding facts, licenses, and external constraints encountered during the development of DeceptionGuard.

## Phase 0
- **Python Version**: It is assumed that the deployment and testing environments will have Python 3.11 or higher, as we rely on `tomllib` which was introduced in the standard library in 3.11.
- **Environment Loading**: We assume the local `.env` file does not need complex bash-like interpolations or multiline values, as our custom `.env` parser is minimal.
- **Evaluation Framework**: `scikit-learn` and `pandas` are strictly kept as optional `dev` dependencies. The core evaluation functions fallback to `stdlib` implementations.
