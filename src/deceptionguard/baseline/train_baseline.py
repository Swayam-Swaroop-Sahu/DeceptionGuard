"""Baseline training script — generates synthetic data and trains TF-IDF + LR.

Requires scikit-learn and is part of the [dev] extras only.
"""

from __future__ import annotations

import csv
from pathlib import Path

# Guard optional imports
_HAS_SKLEARN = False
try:
    from sklearn.metrics import precision_recall_fscore_support
    from sklearn.model_selection import train_test_split

    _HAS_SKLEARN = True
except ImportError:
    pass

from .classifier import BaselineClassifier

# Synthetic data for testing and development
LEGIT_TEXTS = [
    "Dear team, please find attached the quarterly report for your review.",
    "Meeting reminder: Project kickoff tomorrow at 10 AM in Conference Room B.",
    "Hi team, here are the updated project specifications as requested.",
    "Please review the attached document and provide feedback by Friday.",
    "Thank you for your order. Your shipment will arrive within 3-5 business days.",
    "Welcome to our service! Here's how to get started with your new account.",
    "Your invoice for January services is attached. Payment due within 30 days.",
    "We're excited to announce our new product launch next month.",
    "Please confirm your availability for the client meeting next Tuesday.",
    "The quarterly budget review has been scheduled for next week.",
    "Here are the minutes from yesterday's team meeting.",
    "Your password has been successfully reset. Please log in with your new credentials.",
    "We've received your support ticket and will respond within 24 hours.",
    "The system maintenance window is scheduled for this weekend.",
    "Congratulations on your work anniversary! Here's a small gift.",
    "Please update your contact information in the employee portal.",
    "The training materials for the new software are now available online.",
    "Your expense report has been approved and will be processed this week.",
    "Reminder: Annual compliance training is due by end of month.",
    "We're hiring! Check out our latest job openings on the careers page.",
]

PHISHING_TEXTS = [
    "URGENT: Your account has been compromised! Click here to verify immediately.",
    "IMPORTANT: Update your banking information now or lose access to your funds.",
    "SECURITY ALERT: Suspicious login detected. Verify your identity at this link.",
    "Your package delivery failed. Click to reschedule or it will be returned.",
    "Congratulations! You've won a $1000 gift card. Claim now before it expires.",
    "IRS NOTICE: You owe back taxes. Pay immediately to avoid legal action.",
    "Your Netflix subscription has expired. Update payment to continue streaming.",
    "Microsoft Security: Unusual sign-in activity. Secure your account now.",
    "Amazon Order: Your package cannot be delivered. Confirm address here.",
    "PayPal Alert: Your account is limited. Resolve by clicking this link.",
    "Bank of America: Verify your identity to prevent account closure.",
    "Apple ID: Someone tried to access your account. Review recent activity.",
    "LinkedIn: You have a new connection request from a recruiter.",
    "Dropbox: Your storage is almost full. Upgrade now for 50% off.",
    "Adobe: Your Creative Cloud subscription will renew tomorrow. Cancel here.",
    "Zoom: Your meeting recording is ready. Download before it expires.",
    "GitHub: Security vulnerability found in your repository. Fix immediately.",
    "Slack: Your workspace will be deactivated. Take action to keep it.",
    "Trello: Your board has been shared with an external user. Review access.",
    "Atlassian: Critical security patch required. Apply update now.",
]


def generate_placeholder_data(output_dir: Path | None = None) -> tuple[list[dict], list[dict]]:
    """Generate synthetic placeholder dataset for testing.

    Returns:
        Tuple of (train_data, test_data) as lists of dicts with 'text' and 'label' keys.
    """
    if not _HAS_SKLEARN:
        raise ImportError(
            "scikit-learn is required for data generation. "
            "Install with: pip install deceptionguard[dev]"
        )

    texts = LEGIT_TEXTS + PHISHING_TEXTS
    labels = [0] * len(LEGIT_TEXTS) + [1] * len(PHISHING_TEXTS)

    # Create list of dicts
    data = [{"text": t, "label": l} for t, l in zip(texts, labels)]

    # Split into train/test
    train_data, test_data = train_test_split(
        data, test_size=0.3, random_state=42,
        stratify=[d["label"] for d in data],
    )

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write as CSV using stdlib
        for name, dataset in [("placeholder_train.csv", train_data), ("placeholder_test.csv", test_data)]:
            filepath = output_dir / name
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["text", "label"])
                writer.writeheader()
                writer.writerows(dataset)

        print(f"Generated {len(train_data)} training and {len(test_data)} test samples")
        print(f"Train: {output_dir / 'placeholder_train.csv'}")
        print(f"Test: {output_dir / 'placeholder_test.csv'}")

    return train_data, test_data


def main() -> None:
    """Train and evaluate the baseline classifier."""
    if not _HAS_SKLEARN:
        print("Error: scikit-learn is required. Install with: pip install deceptionguard[dev]")
        return

    processed_dir = Path(__file__).parent.parent / "data" / "processed"

    # Generate data
    train_data, test_data = generate_placeholder_data(processed_dir)

    # Train classifier
    classifier = BaselineClassifier()
    train_texts = [d["text"] for d in train_data]
    train_labels = [d["label"] for d in train_data]
    classifier.train(train_texts, train_labels)

    # Predict on test set
    test_texts = [d["text"] for d in test_data]
    test_labels = [d["label"] for d in test_data]
    predictions = classifier.predict(test_texts)
    pred_labels = [1 if p > 0.5 else 0 for p in predictions]

    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        test_labels, pred_labels, average="binary"
    )

    metrics = {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "test_samples": len(test_data),
    }

    # Save to JSON
    import json
    metrics_path = processed_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    print("\nBaseline Classifier Results:")
    print(f"Test F1 Score: {f1:.4f}")
    print(f"Test Samples: {len(test_data)}")
    print(f"Metrics saved to {metrics_path}")

    # Print some example predictions
    print("\nSample Predictions:")
    for i in range(min(5, len(test_data))):
        text_preview = test_data[i]["text"][:80] + "..."
        true_label = "Phishing" if test_data[i]["label"] == 1 else "Legitimate"
        pred_label = "Phishing" if pred_labels[i] == 1 else "Legitimate"
        print(f"  [{predictions[i]:.3f}] True: {true_label}, Pred: {pred_label} - {text_preview}")


if __name__ == "__main__":
    main()
