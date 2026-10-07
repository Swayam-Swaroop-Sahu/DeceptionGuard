"""
Load and combine raw email datasets from multiple sources into a unified CSV.
Sources: Nazario phishing corpus, Nigerian Fraud, CEAS 2008, Enron, Ling-Spam, SpamAssassin
(Kaggle dataset: naserabdullahalam/phishing-email-dataset)
"""
import os
import pandas as pd


def load_raw_datasets(raw_dir: str = "data/raw") -> dict[str, pd.DataFrame]:
    dfs = {}
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.endswith(".csv"):
            continue
        path = os.path.join(raw_dir, fname)
        df = pd.read_csv(path)
        dfs[fname] = df
        print(f"  Loaded {fname}: {len(df)} rows, columns={list(df.columns)}")
    return dfs


def combine_datasets(raw_dir: str = "data/raw") -> pd.DataFrame:
    dfs = load_raw_datasets(raw_dir)

    rows = []

    # --- Nazario: pure phishing ---
    if "Nazario.csv" in dfs:
        df = dfs["Nazario.csv"]
        df = df[df["label"] == 1]
        for _, r in df.iterrows():
            rows.append({
                "email_text": f"Subject: {r.get('subject', '')}\n\n{r.get('body', '')}",
                "sender": r.get("sender", ""),
                "subject": r.get("subject", ""),
                "label": 1,
                "source": "Nazario",
            })

    # --- Nigerian Fraud: pure phishing ---
    if "Nigerian_Fraud.csv" in dfs:
        df = dfs["Nigerian_Fraud.csv"]
        df = df[df["label"] == 1]
        for _, r in df.iterrows():
            rows.append({
                "email_text": f"Subject: {r.get('subject', '')}\n\n{r.get('body', '')}",
                "sender": r.get("sender", ""),
                "subject": r.get("subject", ""),
                "label": 1,
                "source": "Nigerian_Fraud",
            })

    # --- CEAS 2008: both ham and phishing ---
    if "CEAS_08.csv" in dfs:
        df = dfs["CEAS_08.csv"]
        for _, r in df.iterrows():
            rows.append({
                "email_text": f"Subject: {r.get('subject', '')}\n\n{r.get('body', '')}",
                "sender": r.get("sender", ""),
                "subject": r.get("subject", ""),
                "label": int(r["label"]),
                "source": "CEAS_08",
            })

    # --- Enron: real ham, some phishing labeled ---
    if "Enron.csv" in dfs:
        df = dfs["Enron.csv"]
        # Enron doesn't have sender column
        for _, r in df.iterrows():
            rows.append({
                "email_text": f"Subject: {r.get('subject', '')}\n\n{r.get('body', '')}",
                "sender": "",
                "subject": r.get("subject", ""),
                "label": int(r["label"]),
                "source": "Enron",
            })

    # --- Ling-Spam: legitimate ---
    if "Ling.csv" in dfs:
        df = dfs["Ling.csv"]
        df = df[df["label"] == 0]
        for _, r in df.iterrows():
            rows.append({
                "email_text": f"Subject: {r.get('subject', '')}\n\n{r.get('body', '')}",
                "sender": "",
                "subject": r.get("subject", ""),
                "label": 0,
                "source": "Ling-Spam",
            })

    # --- SpamAssassin: legitimate ham ---
    if "SpamAssasin.csv" in dfs:
        df = dfs["SpamAssasin.csv"]
        df = df[df["label"] == 0]
        for _, r in df.iterrows():
            rows.append({
                "email_text": f"Subject: {r.get('subject', '')}\n\n{r.get('body', '')}",
                "sender": r.get("sender", ""),
                "subject": r.get("subject", ""),
                "label": 0,
                "source": "SpamAssassin",
            })

    combined = pd.DataFrame(rows)
    combined = combined.drop_duplicates(subset=["email_text"])
    combined = combined.dropna(subset=["email_text"])
    combined = combined[combined["email_text"].str.strip() != ""]

    return combined


if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    combined = combine_datasets()
    output_path = "data/processed/raw_combined.csv"
    combined.to_csv(output_path, index=False)

    vc = combined["label"].value_counts().to_dict()
    print(f"\nSaved {output_path}: {len(combined)} rows")
    print(f"  phishing (1): {vc.get(1, 0)}")
    print(f"  legitimate (0): {vc.get(0, 0)}")
    print(f"  Sources: {combined['source'].value_counts().to_dict()}")