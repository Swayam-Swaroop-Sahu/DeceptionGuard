# AI-Driven Phishing Email Detection with Explainability

End-to-end machine learning pipeline for phishing email detection — from raw datasets through trained models to interactive deployment, with comprehensive explainability (SHAP, LIME, feature contribution analysis).

## Overview

This project combines **6 phishing/legitimate email datasets** (~16,000 emails), engineers **5,009 features** (5,000 TF-IDF n-grams + 9 handcrafted metadata features), trains **4 classifiers**, and provides both **global** and **local** model interpretability. The recommended model (Logistic Regression) achieves **F1 = 0.987 | AUC = 0.999** with full coefficient-level transparency.

### Why Explainability Matters

Phishing detection is a security-critical task. Analysts need to understand **why** an email was flagged — not just trust a black-box score. This project provides:

- **SHAP** global feature impact (beeswarm + bar importance)
- **LR coefficient split plots** (top 20 phishing vs top 20 legitimate drivers)
- **RF labeled feature importances** (TF-IDF term vs metadata)
- **LIME local explanations** on 3 representative test emails
- **Interactive Streamlit app** with per-prediction feature contribution breakdowns

## Datasets

| Source              | Type                    | Count   |
|---------------------|-------------------------|---------|
| Nazario             | Phishing                | ~1,800  |
| Nigerian Fraud      | Phishing                | ~1,800  |
| CEAS 2008           | Mixed (ham + phishing)  | ~4,500  |
| Enron               | Ham (some phishing)     | ~5,500  |
| Ling-Spam           | Legitimate              | ~2,800  |
| SpamAssassin        | Legitimate              | ~6,000  |

Dataset source: [Kaggle — naserabdullahalam/phishing-email-dataset](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset)

## Pipeline Architecture

```
Raw CSV Datasets
      │
      ▼
[load_data.py] ─── Combine & normalize → data/processed/raw_combined.csv
      │
      ▼
[preprocessing.py] ─── Clean, tokenize, lemmatize → data/processed/cleaned.csv
      │
      ▼
[features.py] ─── TF-IDF (5000) + 9 metadata features → models/feature_pipeline.pkl
      │                              │
      │       ┌──────────────────────┘
      │       │ • num_urls          • has_ip_url
      │       │ • url_shortener     • sender_domain_mismatch
      │       │ • num_exclamations  • has_urgent_words
      │       │ • email_length      • num_uppercase_words
      │       │ • has_attachment_keyword
      │       ▼
      ▼
[train.py] ─── 4 classifiers with GridSearchCV (F1 scorer, CV=3)
      │
      ├── models/LogisticRegression.pkl      (F1=0.987)
      ├── models/RandomForestClassifier.pkl  (F1=0.984)
      ├── models/MultinomialNB.pkl           (F1=0.943)
      └── models/MLPClassifier.pkl           (F1=0.987)
      │
      ▼
[evaluate.py] ─── Confusion matrices, ROC curves, model comparison CSV
      │
      ▼
[explain.py] ─── SHAP beeswarm, LIME local explanations, explainability report
      │
      ▼
[phase6_finalize.py] ─── Static explainability artifacts (no SHAP dependency)
      │
      ▼
[app/streamlit_app.py] ─── Interactive web demo with per-feature contribution breakdown
```

## Project Structure

```
Explainable_Phishing_Email_Detection/
├── src/
│   ├── __init__.py          Package init
│   ├── load_data.py         Phase 1: Combine datasets
│   ├── preprocessing.py     Phase 1: Text cleaning & lemmatization
│   ├── features.py          Phase 2: TF-IDF + metadata feature engineering
│   ├── train.py             Phase 3: GridSearchCV training
│   ├── evaluate.py          Phase 4: Metrics & visualizations
│   ├── explain.py           Phase 6: SHAL, LIME, LR coeffs, RF importance
│   └── phase6_finalize.py  Phase 6: Static explainability artifacts
├── app/
│   └── streamlit_app.py     Phase 7: Streamlit interactive dashboard
├── notebooks/
│   └── 02_full_pipeline.ipynb  End-to-end Jupyter notebook
├── data/
│   ├── raw/                 Source CSV files (gitignored except .gitkeep)
│   └── processed/           Generated CSVs (raw_combined.csv, cleaned.csv)
├── models/                  Trained model pickles (gitignored except .gitkeep)
├── reports/
│   ├── model_comparison.csv Evaluation metrics table
│   ├── report.md            Final project report
│   ├── explainability_notes.md  Phase 6 analysis
│   └── figures/             Confusion matrices, ROC, SHAP, LIME, features
└── test_shap.py              Standalone SHAP integration test
```

## Quick Start

### Prerequisites

- Python 3.10+
- pip packages (see `requirements.txt`)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd Explainable_Phishing_Email_Detection

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows, or venv/bin/activate for Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline

Run scripts in sequence from the project root:

```bash
# Phase 1: Combine datasets
python src/load_data.py

# Phase 2: Clean and preprocess text
python src/preprocessing.py

# Phase 3: Feature engineering (TF-IDF + metadata)
python src/features.py

# Phase 4: Train models with GridSearchCV
python src/train.py

# Phase 5: Evaluate — metrics, confusion matrices, ROC curves
python src/evaluate.py

# Phase 6: Explainability — SHAP, LIME, feature importance
python src/explain.py

# Phase 6 (alternative): Static explainability artifacts
python src/phase6_finalize.py
```

### Launch the Interactive App

```bash
streamlit run app/streamlit_app.py
```

Paste an email, select a model, and get a prediction with feature-level explanations.

## Model Performance

| Model                | Accuracy | Precision | Recall | F1     | ROC-AUC | Interpretability |
|---------------------|----------|----------|--------|-------|---------|------------------|
| **Logistic Regression** | 0.9863    | 0.9852    | 0.9878  | 0.9865 | 0.9988  | Yes High          |
| Random Forest         | 0.9836    | 0.9873    | 0.9802  | 0.9837 | 0.9999  | - Medium        |
| MLP                  | 0.9864    | 0.9867    | 0.9865  | 0.9866 | 0.9990  | No Black-box     |
| Multinomial NB       | 0.9440    | 0.9797    | 0.9089  | 0.9403 | 0.9904  | - Medium        |

## Explainability

### Global Explanations

- **SHAP** (`reports/figures/shap_summary_*.png`): Beeswarm and bar importance plots for Random Forest and Logistic Regression
- **LR Coefficients** (`reports/figures/lr_top_coefficients.png`): Top 20 phishing-indicating vs top 20 legitimate-indicating features, color-coded by type
- **RF Feature Importance** (`reports/figures/rf_feature_importance.png`): Top 20 Gini importance features, labeled TF-IDF vs metadata
- **Metadata Feature Means** (`reports/figures/metadata_feature_means.png`): Per-class mean differences for all 9 engineered features
- **ROC Curves** (`reports/figures/roc_curves.png`): All 4 models overlaid

### Local Analysis (Per-Email)

- **LIME** (`reports/figures/lime_example_*.html`): 5 instance-level explanations using `LimeTextExplainer` on raw text
- **Feature Contributions** (`reports/figures/example_*.html`): 3 static HTML analysis cards showing top 10 features driving each prediction
- **Streamlit App**: Live per-feature contribution breakdown for any user-pasted email

## Recommendation

**Deploy Logistic Regression** as the primary production model:

- Performance matches Random Forest/MLP (F1 0.987 vs 0.984/0.987)
- Full linear transparency: every coefficient directly maps to a feature, making any individual prediction explainable at inference time
- Works with both LIME (local) and SHAP (global)
- Regulatory/audit-friendly — no black-box decisions

## Key Findings

| Finding | Detail |
|---------|--------|
| **Top phishing drivers** | `has_ip_url`, `sender_domain_mismatch`, `has_urgent_words`, `url_shortener_flag`, TF-IDF: "verify", "password", "account", "bank", "invoice"|
| **Top legitimate signals** | `email_length` (longer = more likely legitimate), TF-IDF: "meeting", "schedule", "team", "project", "thanks" |
| **Metadata dominates** | Engineered metadata features consistently rank in top 10 across both LR coefficients and RF importance |
| **Pharma spam easy** | "viagra", "medication", "pharmacy", "consultation" are lightning rods for detection |
| **Misclassification source** | Conflict between phishing vocabulary and legitimate-looking metadata (clean URLs, longer email) produces borderline predictions |

## Known Limitations

- SHAP requires [numb](https://numba.pydata.org/) which may have Windows compatibility issues under certain policies. Equivalent interpretability is provided via LR coefficients and RF feature_importances_ fallbacks.
- SHAP computation is memory-intensive on the full 5,009-feature sparse matrix; the scripts sample 200-500 instances for SHAP plots.
- The pipeline currently classifies all emails as binary (phishing/legitimate); future extension could add threat-level categorization.

## Tech Stack

- **ML**: Scikit-learn (Pipeline, ColumnTransformer, GridSearchCV)
- **Explainability**: SHAP (TreeExplainer, LinearExplorer), LIME (LimeTextExplainer)
- **NLP**: NLTK (tokenization, lemmatization, stopwords), BeautifulSoup4 (HTML stripping), TfidfVectorizer
- **Domain Extraction**: tldextract
- **Visualization**: Matplotlib, Seaborn
- **Deployment**: Streamlit
- **Serialization**: Joblib

## References & Perspectives

- **Full Report**: `reports/report.md`
- **Explainability Notes**: `reports/explainability_notes.md`
- **Jupyter Notebook**: `notebooks/02_full_pipeline.ipynb`
- **SHAP Test**: `test_shap.py`

## License

MIT License — see [LICENSE](LICENSE) for details.