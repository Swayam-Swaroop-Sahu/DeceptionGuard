"""
Feature engineering: TF-IDF on cleaned text + 9 metadata features.
Produces a Pipeline/ColumnTransformer and saves it as models/feature_pipeline.pkl.
"""
import re
import os
import joblib
import pandas as pd
import numpy as np
import tldextract
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin

# ─── Metadata feature extractor ───────────────────────────────────────

class MetadataExtractor(BaseEstimator, TransformerMixin):
    """Extract 9 metadata features from raw email text, sender, and subject."""

    URL_RE = re.compile(r"https?://\S+|www\.\S+")
    IP_URL_RE = re.compile(
        r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?(?:/|$)"
    )
    URL_SHORT = {
        "bit.ly", "tinyurl.com", "t.co", "ow.ly", "goo.gl", "buff.ly",
        "is.gd", "shorl.com", "shorturl.at", "rb.gy", "cutt.ly", "tiny.cc",
    }
    URGENT = {
        "urgent", "immediately", "alert", "action", "required", "verify",
        "password", "suspended", "restricted", "confirm", "update", "invoice",
        "overdue", "expire", "expires", "deactivate", "compromised",
        "attention", "important", "critical", "warning", "notice", "security",
        "unauthorized", "limited", "failed", "lock", "locked", "blocked",
        "closed",
    }
    ATTACH = {
        "attachment", "attached", "pdf", "invoice pdf", "zip file",
        "attached file", "see attached", "please find attached",
    }

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.array(X)
        n = X.shape[0]

        num_urls = np.zeros(n, dtype=int)
        has_ip_url = np.zeros(n, dtype=int)
        url_shortener_flag = np.zeros(n, dtype=int)
        sender_domain_mismatch = np.zeros(n, dtype=int)
        num_exclamations = np.zeros(n, dtype=int)
        has_urgent_words = np.zeros(n, dtype=int)
        email_length = np.zeros(n, dtype=int)
        num_uppercase_words = np.zeros(n, dtype=int)
        has_attachment_keyword = np.zeros(n, dtype=int)

        for i, row in enumerate(X):
            text = str(row[0]) if len(row) > 0 else ""
            sender = str(row[1]) if len(row) > 1 else ""
            subject = str(row[2]) if len(row) > 2 else ""

            num_urls[i] = len(self.URL_RE.findall(text))
            has_ip_url[i] = 1 if self.IP_URL_RE.search(text) else 0

            lower_text = text.lower()
            url_shortener_flag[i] = 1 if any(
                s in lower_text for s in self.URL_SHORT
            ) else 0

            if sender and "@" in sender and len(self.URL_RE.findall(text)) > 0:
                sender_domain = sender.split("@")[-1].strip().lower()
                urls = self.URL_RE.findall(text)
                extracted = [tldextract.extract(u).domain for u in urls]
                sender_domain_mismatch[i] = 1 if sender_domain not in [
                    e.replace("www.", "") for e in extracted
                ] else 0

            num_exclamations[i] = text.count("!")
            has_urgent_words[i] = 1 if any(w in lower_text for w in self.URGENT) else 0
            email_length[i] = len(text)

            words = re.findall(r"\b[A-Z]{2,}\b", text)
            num_uppercase_words[i] = len(words)

            has_attachment_keyword[i] = 1 if any(
                k in lower_text for k in self.ATTACH
            ) else 0

        return np.column_stack([
            num_urls, has_ip_url, url_shortener_flag, sender_domain_mismatch,
            num_exclamations, has_urgent_words, email_length,
            num_uppercase_words, has_attachment_keyword,
        ])


def build_feature_pipeline() -> Pipeline:
    tfidf = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=3,
            max_df=0.9,
        )),
    ])

    metadata = Pipeline([
        ("extractor", MetadataExtractor()),
        ("scaler", StandardScaler()),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("tfidf", tfidf, "cleaned_text"),
            ("metadata",
             metadata,
             ["email_text", "sender", "subject"]),
        ],
        remainder="drop",
        n_jobs=1,
    )

    return preprocessor


if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned.csv")
    df["sender"] = df["sender"].fillna("")
    df["subject"] = df["subject"].fillna("")
    df["email_text"] = df["email_text"].fillna("")
    df["cleaned_text"] = df["cleaned_text"].fillna("")

    print(f"Loaded: {len(df)} rows, cols={list(df.columns)}")
    print(f"  Phishing: {(df['label'] == 1).sum()}")
    print(f"  Legitimate: {(df['label'] == 0).sum()}")

    y = df["label"].values

    pipeline = build_feature_pipeline()
    X = pipeline.fit_transform(df, y)
    print(f"Feature matrix: {X.shape[0]} rows × {X.shape[1]} features")

    os.makedirs("models", exist_ok=True)
    joblib.dump(pipeline, "models/feature_pipeline.pkl")
    print("Saved models/feature_pipeline.pkl")