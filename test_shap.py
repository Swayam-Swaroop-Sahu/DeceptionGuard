import sys
sys.path.insert(0, 'src')
import joblib
import pandas as pd
import numpy as np
import shap

# Import features module properly so MetadataExtractor is registered under src.features
from src import features
import src.features

feature_pipeline = joblib.load('models/feature_pipeline.pkl')
df = pd.read_csv('data/processed/cleaned.csv')
df["sender"] = df["sender"].fillna("")
df["subject"] = df["subject"].fillna("")
df["email_text"] = df["email_text"].fillna("")
df["cleaned_text"] = df["cleaned_text"].fillna("")

X = feature_pipeline.transform(df)
y = df["label"].values
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("X_test shape:", X_test.shape)

# Test SHAP TreeExplainer on Random Forest
rf = joblib.load('models/RandomForestClassifier.pkl')
clf_rf = rf.named_steps['clf']
print('RF classifier type:', type(clf_rf))
print('RF n_features_in_:', clf_rf.n_features_in_)

# Convert to dense for SHAP
if hasattr(X_test, "toarray"):
    X_test_dense = X_test.toarray()
else:
    X_test_dense = X_test

print("X_test_dense shape:", X_test_dense.shape)

# Try SHAP TreeExplainer with feature_perturbation='interventional'
explainer_rf = shap.TreeExplainer(clf_rf, feature_perturbation='interventional')
shap_values_rf = explainer_rf.shap_values(X_test_dense[:50], check_additivity=False)
print('SHAP TreeExplainer works!')
print('SHAP values type:', type(shap_values_rf))
if isinstance(shap_values_rf, list):
    print('List length:', len(shap_values_rf))
    print('Class 0 shape:', shap_values_rf[0].shape)
    print('Class 1 shape:', shap_values_rf[1].shape)
else:
    print('Shape:', shap_values_rf.shape)

# Test SHAP LinearExplainer on Logistic Regression
lr = joblib.load('models/LogisticRegression.pkl')
clf_lr = lr.named_steps['clf']
print('\nLR classifier type:', type(clf_lr))
print('LR coef shape:', clf_lr.coef_.shape)

X_train_dense = X_train.toarray() if hasattr(X_train, "toarray") else X_train
explainer_lr = shap.LinearExplainer(clf_lr, X_train_dense, feature_dependence="independent")
shap_values_lr = explainer_lr.shap_values(X_test_dense[:50])
print('SHAP LinearExplainer works!')
print('SHAP values shape:', shap_values_lr.shape)

print("\nAll SHAP tests passed!")