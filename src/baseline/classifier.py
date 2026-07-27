from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from typing import List, Union
import numpy as np

class BaselineClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000)),
            ('clf', LogisticRegression(random_state=42))
        ])
    
    def train(self, records: List[str], labels: List[int]) -> None:
        """Train the classifier on text records and labels."""
        self.pipeline.fit(records, labels)
    
    def predict(self, records: List[str]) -> List[float]:
        """Return phishing probability scores (0-1)."""
        return self.pipeline.predict_proba(records)[:, 1].tolist()