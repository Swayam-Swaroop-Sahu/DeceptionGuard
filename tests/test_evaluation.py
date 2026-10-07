from deceptionguard.data.split import deduplicate, split_stratified_random, split_temporal
from deceptionguard.evaluation.run_evaluation import load_and_prep_dataset
from deceptionguard.ingestion.email_record import EmailRecord


def test_deduplicate():
    records = [
        EmailRecord(sender="sender", body_text="This is a very specific phishing test string to check duplicates"),
        EmailRecord(sender="sender", body_text="This is a very specific phishing test string to check duplicates and extra"),
        EmailRecord(sender="sender", body_text="Completely different email content that should not match")
    ]
    unique = deduplicate(records, threshold=0.7)
    assert len(unique) == 2

def test_split_stratified_random():
    records = [EmailRecord(sender=f"s{i}") for i in range(10)]
    labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]

    train_r, test_r, train_l, test_l = split_stratified_random(records, labels, test_size=0.4)

    assert len(train_r) == 6
    assert len(test_r) == 4

    # Should maintain ~50/50 ratio
    assert sum(test_l) == 2
    assert sum(train_l) == 3

def test_split_temporal():
    records = [
        EmailRecord(sender="s", date="Sun, 01 Jan 2023 10:00:00 +0000"),
        EmailRecord(sender="s", date="Mon, 01 May 2023 10:00:00 +0000"),
        EmailRecord(sender="s", date="Sun, 01 Oct 2023 10:00:00 +0000")
    ]
    labels = [0, 1, 0]

    train_r, test_r, train_l, test_l = split_temporal(records, labels, "2023-06-01")

    assert len(train_r) == 2
    assert len(test_r) == 1
    assert train_l == [0, 1]
    assert test_l == [0]

def test_load_and_prep_dataset(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("text,label,subtype\nHello world,0,ham\nPhishing link,1,credential\n")

    records, labels, subtypes = load_and_prep_dataset(str(csv_file))
    assert len(records) == 2
    assert labels == [0, 1]
    assert subtypes == ["ham", "credential"]
