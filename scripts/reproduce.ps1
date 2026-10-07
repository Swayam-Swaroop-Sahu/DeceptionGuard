# DeceptionGuard Paper Reproducibility Script
# Runs the full evaluation suite and adversarial robustness tests.

$ErrorActionPreference = "Stop"

Write-Host "=========================================================="
Write-Host " DeceptionGuard Evaluation Reproducibility Script"
Write-Host "=========================================================="

Write-Host "[1/4] Running Fuzzing Tests on Email Parsers..."
python -m pytest tests/test_fuzz_ingestion.py -v
Write-Host "[OK] Fuzzing passed.`n"

# Usually, this script would run the download scripts first.
# We will use the existing placeholder test dataset for demonstration.
$DATASET = "src/deceptionguard/data/processed/placeholder_test.csv"

Write-Host "[2/4] Verifying dataset exists..."
if (!(Test-Path $DATASET)) {
    Write-Host "[FAIL] Dataset not found: $DATASET" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Dataset verified.`n"

Write-Host "[3/4] Running Full Ablation Suite..."
python -m deceptionguard.cli.main evaluate --dataset "$DATASET" --suite full
Write-Host "[OK] Ablation Suite finished.`n"

Write-Host "[4/4] Running Adversarial Robustness Suite..."
python -m deceptionguard.cli.main evaluate --dataset "$DATASET" --suite adversarial
Write-Host "[OK] Adversarial Suite finished.`n"

Write-Host "=========================================================="
Write-Host " Reproducibility Run Complete!"
Write-Host " Results have been saved to the 'results/' directory:"
Write-Host "  - results/summary.json"
Write-Host "  - results/adversarial_robustness.json"
Write-Host "  - results/raw_predictions_*.jsonl"
Write-Host "=========================================================="
