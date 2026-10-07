#!/usr/bin/env bash
# DeceptionGuard Paper Reproducibility Script
# Runs the full evaluation suite and adversarial robustness tests.

set -e

echo "=========================================================="
echo " DeceptionGuard Evaluation Reproducibility Script"
echo "=========================================================="

echo "[1/4] Running Fuzzing Tests on Email Parsers..."
python -m pytest tests/test_fuzz_ingestion.py -v
echo "[OK] Fuzzing passed."
echo ""

# Usually, this script would run the download scripts first:
# python -c "from deceptionguard.data.loaders import load_spamassassin_ham; load_spamassassin_ham()"
# But we will use the existing placeholder test dataset for demonstration.
DATASET="src/deceptionguard/data/processed/placeholder_test.csv"

echo "[2/4] Verifying dataset exists..."
if [ ! -f "$DATASET" ]; then
    echo "[FAIL] Dataset not found: $DATASET"
    exit 1
fi
echo "[OK] Dataset verified."
echo ""

echo "[3/4] Running Full Ablation Suite..."
python -m deceptionguard.cli.main evaluate --dataset "$DATASET" --suite full
echo "[OK] Ablation Suite finished."
echo ""

echo "[4/4] Running Adversarial Robustness Suite..."
python -m deceptionguard.cli.main evaluate --dataset "$DATASET" --suite adversarial
echo "[OK] Adversarial Suite finished."
echo ""

echo "=========================================================="
echo " Reproducibility Run Complete!"
echo " Results have been saved to the 'results/' directory:"
echo "  - results/summary.json"
echo "  - results/adversarial_robustness.json"
echo "  - results/raw_predictions_*.jsonl"
echo "=========================================================="
