"""
Evaluate all 4 trained models on test set.
Produces: reports/model_comparison.csv, confusion matrices, ROC curves in reports/figures/
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, RocCurveDisplay
)

from features import MetadataExtractor


def main():
    os.makedirs("reports/figures", exist_ok=True)

    feature_pipeline = joblib.load("models/feature_pipeline.pkl")
    df = pd.read_csv("data/processed/cleaned.csv")
    df["sender"] = df["sender"].fillna("")
    df["subject"] = df["subject"].fillna("")
    df["email_text"] = df["email_text"].fillna("")
    df["cleaned_text"] = df["cleaned_text"].fillna("")

    X = feature_pipeline.transform(df)
    y = df["label"].values
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model_names = [
        "LogisticRegression",
        "RandomForestClassifier",
        "MultinomialNB",
        "MLPClassifier",
    ]

    results = []
    models = {}

    for name in model_names:
        path = f"models/{name}.pkl"
        model = joblib.load(path)
        models[name] = model

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        results.append({
            "model": name,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "roc_auc": auc,
        })
        print(f"{name}: Acc={acc:.4f}, Prec={prec:.4f}, Rec={rec:.4f}, F1={f1:.4f}, AUC={auc:.4f}")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(4, 3))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=["Legit", "Phish"], yticklabels=["Legit", "Phish"])
        plt.title(f"Confusion Matrix — {name}")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()
        plt.savefig(f"reports/figures/cm_{name}.png", dpi=150)
        plt.close()

    # ROC curves overlay
    plt.figure(figsize=(6, 5))
    for name, model in models.items():
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
            RocCurveDisplay.from_predictions(y_test, y_proba, name=name, ax=plt.gca())
    plt.plot([0, 1], [0, 1], "k--", alpha=0.5)
    plt.title("ROC Curves — All Models")
    plt.tight_layout()
    plt.savefig("reports/figures/roc_curves.png", dpi=150)
    plt.close()

    # Save comparison CSV
    df_res = pd.DataFrame(results)
    df_res.to_csv("reports/model_comparison.csv", index=False)
    print("\nSaved reports/model_comparison.csv")
    print(df_res.to_string(index=False))

    # Also save per-model detailed metrics
    for name in model_names:
        y_pred = models[name].predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        with open(f"reports/figures/metrics_{name}.txt", "w") as f:
            f.write(f"TN={tn}, FP={fp}, FN={fn}, TP={tp}\n")


if __name__ == "__main__":
    main()