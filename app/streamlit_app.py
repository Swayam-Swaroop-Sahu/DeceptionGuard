"""
Streamlit App - Phishing Email Detection with Explainability (Phase 7)
Run: streamlit run app/streamlit_app.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Register MetadataExtractor in __main__ so pickled models load
from features import MetadataExtractor
import __main__
__main__.MetadataExtractor = MetadataExtractor

import streamlit as st
import joblib
import numpy as np
import pandas as pd
from preprocessing import clean_text, tokenize_and_lemmatize

# ==================== Page Config ====================
st.set_page_config(page_title="Phishing Email Detector", page_icon="📧", layout="wide")

st.title("📧 AI-Driven Phishing Email Detection")
st.markdown(
    "Paste an email below to classify it as **Phishing** or **Legitimate**, "
    "with confidence score and feature contribution breakdown."
)

# ==================== Load Models (cached) ====================

@st.cache_resource
def load_assets():
    """Load feature pipeline and all 4 trained models."""
    fp = joblib.load("models/feature_pipeline.pkl")
    
    models = {}
    for name in ["LogisticRegression", "RandomForestClassifier", "MultinomialNB", "MLPClassifier"]:
        models[name] = joblib.load(f"models/{name}.pkl")
    
    # Get feature names
    tfidf = fp.named_transformers_["tfidf"].named_steps["tfidf"]
    tfidf_names = list(tfidf.get_feature_names_out())
    meta_names = [
        "num_urls", "has_ip_url", "url_shortener_flag",
        "sender_domain_mismatch", "num_exclamations", "has_urgent_words",
        "email_length", "num_uppercase_words", "has_attachment_keyword",
    ]
    all_names = tfidf_names + meta_names
    
    return fp, models, all_names

# ==================== Sidebar ====================

st.sidebar.title("About")
st.sidebar.markdown("""
**AI-Driven Phishing Email Detection**

Machine learning pipeline with explainable AI.

### Model Performance (Test Set)
| Model | Accuracy | F1 | AUC |
|-------|----------|------|------|
| LR | 98.6% | 0.987 | 0.999 |
| RF | 98.4% | 0.984 | 0.999 |
| NB | 94.4% | 0.943 | 0.990 |
| MLP | 98.6% | 0.987 | 0.999 |

**Recommended**: Logistic Regression for best performance + interpretability.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### Key Features")
st.sidebar.markdown("""
- IP-based URLs
- Sender domain mismatches
- Urgency keywords
- URL shortener detection
- Exclamation counts
- ALL CAPS words
- Attachment keywords
- Email length
- Total URL count
""")

# ==================== Main UI ====================

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Email Input")
    
    sender = st.text_input("Sender", placeholder="sender@example.com")
    subject = st.text_input("Subject", placeholder="Email subject...")
    email_text = st.text_area(
        "Email Body *",
        height=250,
        placeholder="Paste the full email content here..."
    )
    
    model_choice = st.selectbox(
        "Model",
        ["Logistic Regression (Recommended)", "Random Forest", "Naive Bayes", "MLP Neural Network"],
    )
    
    model_map = {
        "Logistic Regression (Recommended)": "LogisticRegression",
        "Random Forest": "RandomForestClassifier",
        "Naive Bayes": "MultinomialNB",
        "MLP Neural Network": "MLPClassifier",
    }
    
    analyze_btn = st.button("🔍 Analyze Email", type="primary", use_container_width=True)

with col2:
    st.subheader("🔬 Analysis Results")
    
    if analyze_btn and email_text.strip():
        with st.spinner("Analyzing... this may take a few seconds..."):
            fp, models, all_names = load_assets()
            
            # Prepare input
            cleaned = tokenize_and_lemmatize(clean_text(email_text))
            input_df = pd.DataFrame([{
                "email_text": email_text,
                "sender": sender or "unknown@example.com",
                "subject": subject or "",
                "cleaned_text": cleaned or " ",
            }])
            
            mdl_name = model_map[model_choice]
            mdl = models[mdl_name]
            
            # Transform
            X = fp.transform(input_df)
            X_dense = X.toarray() if hasattr(X, "toarray") else X
            
            # Predict
            y_pred = int(mdl.predict(X_dense)[0])
            y_proba = mdl.predict_proba(X_dense)[0]
            
            label = "🚨 PHISHING" if y_pred == 1 else "✅ LEGITIMATE"
            confidence = y_proba[y_pred]
            
            # Feature contributions (LR coefficients × values)
            if "LogisticRegression" in mdl_name:
                clf = mdl.named_steps["clf"]
                coef = clf.coef_[0]
                
                # Get feature contributions
                contributions = []
                for i in range(len(all_names)):
                    if X_dense[0, i] != 0:
                        contrib = X_dense[0, i] * coef[i]
                        contributions.append((all_names[i], contrib))
                
                contributions.sort(key=lambda x: -abs(x[1]))
                
                top_phishing = [(n, v) for n, v in contributions if v > 0][:8]
                top_legit = [(n, v) for n, v in contributions if v <= 0][:8]
            
            # Display results
            st.markdown(f"### {label}")
            st.markdown(f"**Confidence**: {confidence:.2%}")
            st.progress(
                float(y_proba[1]),
                text=f"Phish: {y_proba[1]:.2%}  |  Legit: {y_proba[0]:.2%}"
            )
            
            # Metadata extraction
            from features import MetadataExtractor as ME
            extr = ME()
            meta_raw = extr.transform(np.array([[email_text, sender, subject]]))[0]
            meta_names_short = [
                "num_urls", "has_ip_url", "url_shortener", "sender_mismatch",
                "num_exclam", "urgent_words", "email_length", "uppercase_count", "has_attachment"
            ]
            
            st.markdown("---")
            st.markdown("#### 📋 Extracted Metadata")
            cols = st.columns(3)
            for i, (nm, val) in enumerate(zip(meta_names_short, meta_raw)):
                val_disp = f"{val:.1f}" if abs(val) >= 0.1 else "No"
                if nm in ["has_ip_url", "has_urgent_words", "has_attachment"]:
                    val_disp = "Yes" if val > 0.1 else "No"
                elif nm == "sender_mismatch":
                    val_disp = "Yes" if val > 0 else "No"
                cols[i % 3].metric(nm, val_disp)
            
            # LR feature contributions
            if "LogisticRegression" in mdl_name:
                st.markdown("---")
                st.markdown("#### 🔑 Top Phishing-Indicating Features")
                for fname, contrib in top_phishing:
                    st.markdown(f"- **{fname}**: +{contrib:.3f}")
                
                st.markdown("#### 🛡️ Top Legitimate-Indicating Features")
                for fname, contrib in top_legit:
                    st.markdown(f"- **{fname}**: {contrib:.3f}")
            
            else:
                st.info(
                    "Feature contributions shown for Logistic Regression only. "
                    "For other models, switch to LR for coefficient-level explanation."
                )
            
            # Download report
            st.markdown("---")
            report = f"""Phishing Email Analysis Report
===============================
Prediction: {label}
Confidence: {confidence:.4f}
Model: {model_choice}
Phish Prob: {y_proba[1]:.4f}
Legit Prob: {y_proba[0]:.4f}
"""
            if "LogisticRegression" in mdl_name:
                report += "\nTop Phishing Features:\n"
                for fn, fv in top_phishing:
                    report += f"  - {fn}: +{fv:.4f}\n"
                report += "\nTop Legitimate Features:\n"
                for fn, fv in top_legit:
                    report += f"  - {fn}: {fv:.4f}\n"
            
            st.download_button(
                "Download Text Report",
                report,
                file_name="prediction_report.txt",
                mime="text/plain",
            )
    
    elif not email_text.strip() and analyze_btn:
        st.warning("Please enter some email text to analyze.")