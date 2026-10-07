"""
Email text cleaning and preprocessing.
Functions: strip_html, clean_text, tokenize_and_lemmatize.
"""
import re
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup

try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
    nltk.data.find("corpora/wordnet")
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")
    nltk.download("punkt_tab")

STOPWORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
EMAIL_PATTERN = re.compile(r"\S+@\S+")
HTML_TAG = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = BeautifulSoup(text, "html.parser").get_text(separator=" ")
    return HTML_TAG.sub(" ", text)


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = strip_html(text)
    text = URL_PATTERN.sub(" ", text)
    text = EMAIL_PATTERN.sub(" ", text)
    text = text.lower()
    text = re.sub(r"\d+", " ", text)
    text = re.sub(rf"[{re.escape(string.punctuation)}]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_and_lemmatize(text: str) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return ""
    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    tokens = [LEMMATIZER.lemmatize(t) for t in tokens]
    return " ".join(tokens)


if __name__ == "__main__":
    df = pd.read_csv("data/processed/raw_combined.csv")
    print(f"Loaded {len(df)} rows")

    df["cleaned_text"] = df["email_text"].apply(clean_text)
    df["cleaned_text"] = df["cleaned_text"].apply(tokenize_and_lemmatize)

    df = df[df["cleaned_text"].str.strip() != ""]
    print(f"After cleaning filter: {len(df)} rows")

    df.to_csv("data/processed/cleaned.csv", index=False)
    print(f"Saved data/processed/cleaned.csv")
    print(f"Columns: {list(df.columns)}")