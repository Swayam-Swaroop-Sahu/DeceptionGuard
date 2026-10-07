# Datasets and Evaluation Protocols

This document details the datasets used for the DeceptionGuard evaluation suite, their licenses, and the preprocessing protocols used to ensure rigorous, reproducible results.

## Public Corpora Supported

| Dataset | Type | License | Description |
|---------|------|---------|-------------|
| **SpamAssassin Public Corpus** | Ham (easy_ham) | Apache 2.0 | Standard collection of non-spam emails from 2002. High quality parsing baseline. |
| **Jose Nazario Phishing Corpus** | Phishing | Public Domain | Historical phishing emails (2005-2015). Used to evaluate static evidence extraction. |
| **Enron Email Dataset** | Ham | Open Access | Scrubbed version of the Enron corpus. Represents real corporate communications. |
| **DeceptionGuard Synthetic Phishing** | Phishing | MIT | Modern, LLM-generated phishing lures targeting contemporary threats. |

## Data Loaders

To prevent automated mass downloading during unit tests, **all dataset loaders must be run manually by the user**. 
The loaders are located in `src/deceptionguard/data/loaders.py`. 

Available loaders:
- `load_spamassassin_ham()`
- `load_nazario_phishing()`
- `load_enron_ham()`
- `load_synthetic_phishing()`

## Preprocessing and Deduplication

To ensure robust evaluation:
1. **Deduplication**: We use k-shingle hashing (k=5) and MinHash signatures to detect near-duplicates. Any emails with a Jaccard similarity ≥ 0.9 are removed to prevent data leakage between train and test splits.
2. **Splitting**: `src/deceptionguard/data/split.py` provides robust splitting mechanisms:
   - `split_stratified_random`: Standard 80/20 train/test split preserving label distribution.
   - `split_cross_corpus`: Train on dataset A, test on dataset B.
   - `split_temporal`: Train on data before date $D$, test on data after date $D$.

## Evaluation Suite (`dg evaluate --suite full`)

The full evaluation suite runs a series of **ablations**:
1. **baseline**: TF-IDF + Logistic Regression (no intent graph, no evidence).
2. **evidence_only**: Pure Python deterministic heuristics.
3. **graph_only**: LLM intent extraction only.
4. **full_pipeline**: Evidence + Intent Graph scoring.

**Metrics computed:**
- Precision, Recall, F1-Score
- ROC-AUC, PR-AUC
- FPR at 95% TPR
- Expected Calibration Error (ECE)
- Bootstrap 95% Confidence Intervals (1000 iterations, seeded)
- McNemar test (Baseline vs Full Pipeline)

All results are written to:
- `results/raw_predictions_*.jsonl` (for exact reproducibility)
- `results/summary.json`
