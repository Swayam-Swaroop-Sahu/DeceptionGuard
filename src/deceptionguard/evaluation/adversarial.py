"""Adversarial Robustness Evaluation.

Applies mutations to email content to test the resilience of the pipeline against
common evasion techniques like homoglyphs, zero-width characters, and typos.
"""

from __future__ import annotations

import json
import logging
import random

from deceptionguard.evaluation.metrics import compute_all_metrics
from deceptionguard.evaluation.run_evaluation import RESULTS_DIR, run_pipeline
from deceptionguard.ingestion.email_record import EmailRecord

logger = logging.getLogger(__name__)

# Common homoglyph mappings (ASCII -> Unicode lookalikes)
HOMOGLYPHS = {
    'a': 'а', # Cyrillic a
    'c': 'с', # Cyrillic c
    'e': 'е', # Cyrillic e
    'o': 'о', # Cyrillic o
    'p': 'р', # Cyrillic p
    'x': 'х', # Cyrillic x
    'y': 'у', # Cyrillic y
}

def apply_homoglyphs(text: str, mutation_rate: float = 0.3) -> str:
    """Replace a percentage of characters with visual lookalikes."""
    result = []
    for char in text:
        if char.lower() in HOMOGLYPHS and random.random() < mutation_rate:
            mutated = HOMOGLYPHS[char.lower()]
            result.append(mutated.upper() if char.isupper() else mutated)
        else:
            result.append(char)
    return "".join(result)


def apply_zero_width(text: str, mutation_rate: float = 0.3) -> str:
    """Inject zero-width spaces (\u200b) into words to break tokenizers."""
    result = []
    for char in text:
        result.append(char)
        if char.isalpha() and random.random() < mutation_rate:
            result.append("\u200b")
    return "".join(result)


def apply_typos(text: str, mutation_rate: float = 0.1) -> str:
    """Apply random typos (character deletion or transposition)."""
    words = text.split(" ")
    result = []
    for word in words:
        if len(word) > 3 and word.isalpha() and random.random() < mutation_rate:
            # 50% chance delete, 50% chance transpose
            if random.random() < 0.5:
                # delete random char
                idx = random.randint(1, len(word) - 2)
                word = word[:idx] + word[idx+1:]
            else:
                # transpose
                idx = random.randint(0, len(word) - 2)
                word = word[:idx] + word[idx+1] + word[idx] + word[idx+2:]
        result.append(word)
    return " ".join(result)

def mutate_record(record: EmailRecord, strategy: str) -> EmailRecord:
    """Apply a mutation strategy to an EmailRecord."""
    text = record.body_text

    if strategy == "homoglyphs":
        text = apply_homoglyphs(text)
    elif strategy == "zero_width":
        text = apply_zero_width(text)
    elif strategy == "typos":
        text = apply_typos(text)
    elif strategy == "combined":
        text = apply_homoglyphs(text, 0.1)
        text = apply_zero_width(text, 0.1)
        text = apply_typos(text, 0.05)

    mutated_kwargs = {"body_text": text}
    if record.subject:
        mutated_kwargs["subject"] = apply_typos(record.subject) if strategy == "typos" else record.subject

    import dataclasses
    return dataclasses.replace(record, **mutated_kwargs)

def evaluate_robustness(
    records: list[EmailRecord],
    labels: list[int],
    strategies: list[str] | None = None
) -> dict:
    """Evaluate pipeline robustness against adversarial attacks."""
    if not strategies:
        strategies = ["homoglyphs", "zero_width", "typos", "combined"]

    # Only attack malicious emails (label == 1) to see evasion success
    # Or attack all? Evasion implies modifying malicious to look benign.
    # We will mutate all, but typically robustness focuses on TPR drop (evasion).

    logger.info("Running baseline performance before attack...")
    base_preds = []
    for rec in records:
        prob = run_pipeline(rec, use_evidence=True, use_graph=True)
        base_preds.append(prob)

    base_metrics = compute_all_metrics(labels, base_preds)

    results = {
        "original": base_metrics,
        "attacks": {}
    }

    for strategy in strategies:
        logger.info(f"Running adversarial attack: {strategy}")
        mutated_records = [mutate_record(r, strategy) for r in records]

        mut_preds = []
        for rec in mutated_records:
            prob = run_pipeline(rec, use_evidence=True, use_graph=True)
            mut_preds.append(prob)

        mut_metrics = compute_all_metrics(labels, mut_preds)

        # Calculate degradation
        f1_drop = base_metrics.get("f1", 0) - mut_metrics.get("f1", 0)
        recall_drop = base_metrics.get("recall", 0) - mut_metrics.get("recall", 0)

        results["attacks"][strategy] = {
            "metrics": mut_metrics,
            "degradation": {
                "f1_drop": f1_drop,
                "recall_drop": recall_drop
            }
        }

    # Save results
    out_path = RESULTS_DIR / "adversarial_robustness.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    logger.info(f"Robustness evaluation complete. Saved to {out_path}")
    return results
