"""Dataset deduplication and splitting.

Implements near-duplicate detection via shingled hashing and multiple
split strategies (stratified random, cross-corpus, temporal).
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Iterable
from datetime import UTC

from ..ingestion.email_record import EmailRecord

logger = logging.getLogger(__name__)


def _get_shingles(text: str, k: int = 5) -> set[str]:
    """Generate k-shingles from text for near-duplicate detection."""
    words = text.lower().split()
    if len(words) < k:
        return {" ".join(words)}
    return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}


def _minhash(shingles: set[str], num_hashes: int = 50) -> list[int]:
    """Generate MinHash signature for a set of shingles."""
    # A simple deterministic minhash implementation
    if not shingles:
        return [0] * num_hashes

    signature = []
    for i in range(num_hashes):
        min_h = float('inf')
        for shingle in shingles:
            # Hash function: hash(shingle + seed)
            h = int(hashlib.md5(f"{shingle}{i}".encode()).hexdigest()[:8], 16)
            if h < min_h:
                min_h = h
        signature.append(min_h)
    return signature


def _jaccard_similarity_minhash(sig1: list[int], sig2: list[int]) -> float:
    """Estimate Jaccard similarity from MinHash signatures."""
    assert len(sig1) == len(sig2)
    if not sig1:
        return 0.0
    matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
    return matches / len(sig1)


def deduplicate(records: Iterable[EmailRecord], threshold: float = 0.9) -> list[EmailRecord]:
    """Deduplicate records using near-duplicate MinHash similarity."""
    unique_records = []
    signatures = []

    logger.info("Deduplicating dataset...")
    for rec in records:
        text = rec.body_text or ""
        shingles = _get_shingles(text)
        sig = _minhash(shingles)

        is_duplicate = False
        for existing_sig in signatures:
            sim = _jaccard_similarity_minhash(sig, existing_sig)
            if sim >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            signatures.append(sig)
            unique_records.append(rec)

    logger.info(f"Deduplication complete: {len(unique_records)} unique records retained.")
    return unique_records


def split_stratified_random(records: list[EmailRecord], labels: list[int], test_size: float = 0.2):
    """Create a stratified random split."""
    try:
        from sklearn.model_selection import train_test_split
        return train_test_split(records, labels, test_size=test_size, stratify=labels, random_state=42)
    except ImportError:
        logger.warning("scikit-learn not available. Falling back to naive random split.")
        import random
        rng = random.Random(42)
        combined = list(zip(records, labels))
        rng.shuffle(combined)
        split_idx = int(len(combined) * (1 - test_size))
        train = combined[:split_idx]
        test = combined[split_idx:]
        return (
            [r for r, l in train], [r for r, l in test],
            [l for r, l in train], [l for r, l in test]
        )


def split_cross_corpus(
    corpus_a: list[EmailRecord], labels_a: list[int],
    corpus_b: list[EmailRecord], labels_b: list[int]
) -> tuple[list[EmailRecord], list[EmailRecord], list[int], list[int]]:
    """Create a cross-corpus split (train on A, test on B)."""
    return corpus_a, corpus_b, labels_a, labels_b


def split_temporal(records: list[EmailRecord], labels: list[int], split_date: str) -> tuple[list[EmailRecord], list[EmailRecord], list[int], list[int]]:
    """Create a temporal split based on email date."""
    from datetime import datetime
    from email.utils import parsedate_to_datetime

    train_recs, test_recs = [], []
    train_lbls, test_lbls = [], []

    # Simple ISO date parsing for the split point
    try:
        split_dt = datetime.fromisoformat(split_date)
    except ValueError:
        logger.error("Invalid split_date format. Use YYYY-MM-DD")
        return records, [], labels, []

    for rec, lbl in zip(records, labels):
        rec_dt = None
        if rec.date:
            try:
                rec_dt = parsedate_to_datetime(rec.date)
                # Naive vs aware tz handling
                if rec_dt.tzinfo is not None:
                    # Convert split_dt to aware if rec_dt is aware
                    split_dt = split_dt.replace(tzinfo=UTC)
            except Exception:
                pass

        if rec_dt and rec_dt < split_dt:
            train_recs.append(rec)
            train_lbls.append(lbl)
        else:
            test_recs.append(rec)
            test_lbls.append(lbl)

    return train_recs, test_recs, train_lbls, test_lbls
