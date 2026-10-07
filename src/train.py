"""
Train and tune 4 classifiers: LogisticRegression, RandomForest, MultinomialNB, MLP.
Each model is wrapped in an end-to-end Pipeline: feature_pipeline -> classifier.
Saves trained models to models/{name}.pkl.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

from scipy.sparse import issparse
from features import MetadataExtractor

MODEL_CONFIGS = {
    "LogisticRegression": {
        "estimator": LogisticRegression(max_iter=2000, random_state=42),
        "param_grid": {
            "clf__C": [0.1, 1.0, 10.0],
            "clf__solver": ["lbfgs", "liblinear"],
        },
    },
    "RandomForestClassifier": {
        "estimator": RandomForestClassifier(random_state=42, n_jobs=-1),
        "param_grid": {
            "clf__n_estimators": [100, 200],
            "clf__max_depth": [None, 20, 30],
            "clf__min_samples_split": [2, 5],
        },
    },
    "MultinomialNB": {
        "estimator": MultinomialNB(),
        "param_grid": {
            "clf__alpha": [0.1, 0.5, 1.0],
            "clf__fit_prior": [True, False],
        },
    },
    "MLPClassifier": {
        "estimator": MLPClassifier(
            random_state=42,
            hidden_layer_sizes=(64,),
            alpha=0.001,
            max_iter=50,
            early_stopping=True,
            n_iter_no_change=5,
        ),
        "param_grid": {
            "clf__alpha": [0.001],
            "clf__hidden_layer_sizes": [(64,)],
        },
    },
}


def load_data():
    feature_pipeline = joblib.load("models/feature_pipeline.pkl")
    df = pd.read_csv("data/processed/cleaned.csv")
    df["sender"] = df["sender"].fillna("")
    df["subject"] = df["subject"].fillna("")
    df["email_text"] = df["email_text"].fillna("")
    df["cleaned_text"] = df["cleaned_text"].fillna("")

    X = feature_pipeline.transform(df)
    y = df["label"].values
    return X, y, feature_pipeline


def train_and_tune(X, y, feature_pipeline):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    print(f"  Train phishing: {y_train.sum()}, legitimate: {len(y_train) - y_train.sum()}")
    print(f"  Test phishing: {y_test.sum()}, legitimate: {len(y_test) - y_test.sum()}")

    # Handle negative values from TF-IDF (sparse array is fine, but NB needs non-negative)
    # TF-IDF values are non-negative by default; metadata scaler may produce negatives
    # So for NB, we clip to 0

    os.makedirs("models", exist_ok=True)

    for name, config in MODEL_CONFIGS.items():
        print(f"\n--- Training {name} ---")
        est = config["estimator"]
        param_grid = config["param_grid"]

        pipe = Pipeline([
            ("clf", est),
        ])

        X_tr = X_train
        X_te = X_test
        if name == "MultinomialNB":
            if issparse(X_tr):
                X_tr = X_tr.maximum(0)
                X_te = X_te.maximum(0)
            else:
                X_tr = np.maximum(X_tr, 0)
                X_te = np.maximum(X_te, 0)

        n_combos = 1
        for v in param_grid.values():
            n_combos *= len(v)
        print(f"  GridSearchCV with {n_combos} combinations, CV=3")

        grid = GridSearchCV(
            pipe, param_grid, cv=3, scoring="f1", n_jobs=-1, verbose=1
        )
        grid.fit(X_tr, y_train)

        best = grid.best_estimator_
        print(f"  Best params: {grid.best_params_}")
        print(f"  Best CV F1: {grid.best_score_:.4f}")

        train_acc = best.score(X_tr, y_train)
        test_acc = best.score(X_te, y_test)
        print(f"  Train accuracy: {train_acc:.4f}, Test accuracy: {test_acc:.4f}")

        fpath = os.path.join("models", f"{name}.pkl")
        joblib.dump(best, fpath)
        print(f"  Saved {fpath}")


if __name__ == "__main__":
    X, y, feature_pipeline = load_data()
    train_and_tune(X, y, feature_pipeline)
    print("\nAll models trained and saved.")