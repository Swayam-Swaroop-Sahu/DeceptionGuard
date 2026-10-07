
import pytest

from deceptionguard.evaluation.adversarial import (
    apply_homoglyphs,
    apply_typos,
    apply_zero_width,
    evaluate_robustness,
    mutate_record,
)
from deceptionguard.ingestion.email_record import EmailRecord


def test_apply_homoglyphs():
    original = "paypal"
    attacked = apply_homoglyphs(original, mutation_rate=1.0)
    assert original != attacked
    assert len(attacked) > 0

def test_apply_zero_width():
    original = "secure"
    attacked = apply_zero_width(original, mutation_rate=1.0)
    assert original != attacked
    assert len(attacked) > len(original)

def test_apply_typos():
    original = "account account account"
    attacked = apply_typos(original, mutation_rate=1.0)
    assert original != attacked or len(original) < 3

def test_mutate_record():
    record = EmailRecord(
        sender="test@paypal.com",
        reply_to=None,
        return_path=None,
        subject="URGENT: account locked",
        date=None,
        body_text="Please login to your paypal account to secure it.",
        links=[],
        attachments=[]
    )

    mutated = mutate_record(record, "homoglyphs")
    assert mutated.body_text != record.body_text

def test_evaluate_robustness(tmp_path):
    records = [
        EmailRecord(
            sender="test@paypal.com",
            reply_to=None,
            return_path=None,
            subject="URGENT: account locked",
            date=None,
            body_text="Please login to your paypal account to secure it.",
            links=[],
            attachments=[]
        )
    ]
    labels = [1]

    # We must patch run_pipeline and RESULTS_DIR

    import deceptionguard.evaluation.adversarial as adv

    with pytest.MonkeyPatch.context() as m:
        m.setattr(adv, "run_pipeline", lambda r, use_evidence, use_graph: 0.9)
        m.setattr(adv, "RESULTS_DIR", tmp_path)

        results = evaluate_robustness(records, labels, strategies=["homoglyphs"])
        assert "attacks" in results
        assert "homoglyphs" in results["attacks"]
