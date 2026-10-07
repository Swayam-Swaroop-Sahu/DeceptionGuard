# DeceptionGuard Test Strategy

## Test Pyramid
DeceptionGuard follows a standard testing pyramid to ensure correctness, reliability, and security while maintaining high velocity.

1. **Unit Tests (Base)**:
   - Target individual functions and modules (e.g., `ingestion.normalize`, `evidence.detectors`).
   - Run in milliseconds.
   - Zero external I/O (no network, no file reading outside `tests/fixtures/`).
   - Mocking is strictly limited to external service boundaries (e.g., `urllib.request` for the LLM).

2. **Integration Tests (Middle)**:
   - Test module interactions (e.g., ingestion -> graph extraction -> scoring).
   - Use real dependencies as much as possible.
   - Examples include running a full score cycle on synthetic `EmailRecord` objects.

3. **End-to-End (E2E) Tests (Top)**:
   - CLI execution (`dg scan`, `dg evaluate`).
   - HTTP UI functionality (`test_ui_server.py`).
   - Assert exit codes, stdout formatting, and error messages.

4. **Fuzzing & Property Tests (Specialized)**:
   - Pathological inputs for ingestion (truncated MIME, null bytes, infinite nesting).
   - Adversarial text sequences (homoglyphs, bidi overrides).
   - Goal: No crashes, finite execution time, bounded memory.

5. **Mathematical & Determinism Tests (Specialized)**:
   - Metrics verification against hand-calculated values.
   - Seeded determinism (same seed = byte-identical output).
   - Isotonic regression invariants and contribution bounds.

## Coverage Targets
- **Overall**: ≥85% line coverage, including branches.
- **Critical Paths**: ≥95% (Ingestion parsing, risk engine scoring, metric calculation, intent verification).

## How to Run Tests
```bash
# Run all tests
make test

# Run tests with coverage
python -m coverage run --branch --source=src -m pytest tests/
python -m coverage report -m
```
