.PHONY: help install test lint fuzz evaluate reproduce

DATASET ?= src/deceptionguard/data/processed/placeholder_test.csv

help:
	@echo "DeceptionGuard Makefile"
	@echo "======================="
	@echo "install   - Install package and dev dependencies"
	@echo "test      - Run full test suite"
	@echo "lint      - Run Ruff linter"
	@echo "fuzz      - Run hypothesis fuzzing tests"
	@echo "evaluate  - Run evaluation suite (full ablation)"
	@echo "reproduce - Run the entire reproducibility script"

install:
	pip install -e .[dev,llm]

test:
	python -m pytest tests/ -v

lint:
	python -m ruff check src/ tests/

fuzz:
	python -m pytest tests/test_fuzz_ingestion.py -v

evaluate:
	python -m deceptionguard.cli.main evaluate --dataset $(DATASET) --suite full

reproduce:
	bash scripts/reproduce.sh
