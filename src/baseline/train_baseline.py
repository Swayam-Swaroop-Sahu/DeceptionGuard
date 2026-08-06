import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from .classifier import BaselineClassifier


def generate_placeholder_data():
    """Generate synthetic placeholder dataset for testing."""
    legit_texts = [
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
    
    phishing_texts = [
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
    
    # Create DataFrame
    texts = legit_texts + phishing_texts
    labels = [0] * 20 + [1] * 20  # 0 = legit, 1 = phishing
    
    df = pd.DataFrame({"text": texts, "label": labels})
    
    # Split into train/test
    train_df, test_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df["label"])
    
    # Save to data/processed
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    train_df.to_csv(processed_dir / "placeholder_train.csv", index=False)
    test_df.to_csv(processed_dir / "placeholder_test.csv", index=False)
    
    print(f"Generated {len(train_df)} training samples and {len(test_df)} test samples")
    print(f"Train: {processed_dir / 'placeholder_train.csv'}")
    print(f"Test: {processed_dir / 'placeholder_test.csv'}")
    
    return train_df, test_df


def main():
    # Load or generate data
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    train_path = processed_dir / "placeholder_train.csv"
    test_path = processed_dir / "placeholder_test.csv"
    
    if train_path.exists() and test_path.exists():
        print("Loading existing placeholder data...")
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
    else:
        print("Generating placeholder data...")
        train_df, test_df = generate_placeholder_data()
    
    # Train classifier
    classifier = BaselineClassifier()
    classifier.train(train_df["text"].tolist(), train_df["label"].tolist())
    
    # Predict on test set
    predictions = classifier.predict(test_df["text"].tolist())
    pred_labels = [1 if p > 0.5 else 0 for p in predictions]
    
    # Calculate F1 score
    f1 = f1_score(test_df["label"].tolist(), pred_labels)
    
    print(f"\nBaseline Classifier Results:")
    print(f"Test F1 Score: {f1:.4f}")
    print(f"Test Samples: {len(test_df)}")
    
    # Print some example predictions
    print("\nSample Predictions:")
    for i in range(min(5, len(test_df))):
        text_preview = test_df.iloc[i]["text"][:80] + "..."
        true_label = "Phishing" if test_df.iloc[i]["label"] == 1 else "Legitimate"
        pred_label = "Phishing" if pred_labels[i] == 1 else "Legitimate"
        print(f"  [{predictions[i]:.3f}] True: {true_label}, Pred: {pred_label} - {text_preview}")


if __name__ == "__main__":
    main()