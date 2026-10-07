"""Dataset loaders for DeceptionGuard.

These scripts are user-run (via CLI or manual invocation) to download
and parse public corpora (Enron, SpamAssassin, Nazario, etc.).
They never auto-download during tests.
"""

from __future__ import annotations

import logging
import os
import tarfile
import urllib.request
from collections.abc import Iterator
from pathlib import Path

from ..ingestion.email_record import EmailRecord
from ..ingestion.parser import parse_eml, parse_mbox

logger = logging.getLogger(__name__)

# Default data dir
DATA_DIR = Path(__file__).parent.parent.parent.parent / "datasets"


def _download_file(url: str, dest_path: Path) -> None:
    """Download a file if it doesn't already exist."""
    if dest_path.exists():
        logger.info(f"File already exists: {dest_path}")
        return
    logger.info(f"Downloading {url} to {dest_path}...")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest_path))
    logger.info("Download complete.")


def load_spamassassin_ham(data_dir: Path = DATA_DIR) -> Iterator[EmailRecord]:
    """Load SpamAssassin public corpus (ham/easy_ham).

    License: Apache License 2.0
    Reference: https://spamassassin.apache.org/old/publiccorpus/
    """
    url = "https://spamassassin.apache.org/old/publiccorpus/20021010_easy_ham.tar.bz2"
    dest_tar = data_dir / "raw" / "spamassassin" / "20021010_easy_ham.tar.bz2"
    extract_dir = data_dir / "raw" / "spamassassin" / "easy_ham"

    _download_file(url, dest_tar)

    if not extract_dir.exists():
        logger.info("Extracting SpamAssassin ham...")
        with tarfile.open(dest_tar, "r:bz2") as tar:
            tar.extractall(path=extract_dir.parent)

    logger.info("Parsing SpamAssassin ham files...")
    for root, _, files in os.walk(extract_dir):
        for file in files:
            filepath = Path(root) / file
            if file == "cmds":
                continue # Skip metadata file
            try:
                yield parse_eml(str(filepath))
            except Exception as e:
                logger.debug(f"Failed to parse {filepath}: {e}")


def load_nazario_phishing(data_dir: Path = DATA_DIR) -> Iterator[EmailRecord]:
    """Load Jose Nazario's Phishing Corpus.

    License: Public Domain / Open Access
    Reference: https://monkey.org/~jose/wiki/doku.php?id=PhishingCorpus
    """
    # Using 2005 archive as an example
    url = "https://monkey.org/~jose/phishing/phishing0.mbox"
    dest_mbox = data_dir / "raw" / "nazario" / "phishing0.mbox"

    _download_file(url, dest_mbox)

    logger.info("Parsing Nazario phishing mbox...")
    try:
        yield from parse_mbox(str(dest_mbox))
    except Exception as e:
        logger.error(f"Failed to parse Nazario mbox: {e}")


def load_enron_ham(data_dir: Path = DATA_DIR) -> Iterator[EmailRecord]:
    """Load Enron corpus (PII-scrubbed, usually provided by CMU).

    License: Open access (originally published by FERC, subsequently scrubbed by CALO/CMU)
    Reference: http://www.cs.cmu.edu/~enron/
    """
    # For demonstration, we'll download a smaller pre-processed subset or just describe it,
    # as the full Enron dataset is ~1.7GB.
    logger.warning("Enron dataset is very large (~1.7GB). Manual download recommended.")
    logger.warning("URL: http://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz")

    # We will simulate parsing if the directory exists
    enron_dir = data_dir / "raw" / "enron" / "maildir"
    if not enron_dir.exists():
        logger.error(f"Enron maildir not found at {enron_dir}. Please download manually.")
        return

    logger.info("Parsing Enron ham files...")
    # Just yield a few to avoid taking forever in this function
    count = 0
    for root, _, files in os.walk(enron_dir):
        for file in files:
            if count > 1000: # Limit for safety in this loader
                break
            filepath = Path(root) / file
            try:
                yield parse_eml(str(filepath))
                count += 1
            except Exception:
                pass


def load_synthetic_phishing(data_dir: Path = DATA_DIR) -> Iterator[EmailRecord]:
    """Load LLM-generated synthetic phishing dataset.

    License: Generated via LLM by DeceptionGuard, MIT licensed.
    """
    # In a real scenario, this might download from a HuggingFace dataset repo.
    # For now, we will return some hardcoded records.
    from deceptionguard.baseline.train_baseline import PHISHING_TEXTS

    for text in PHISHING_TEXTS:
        yield EmailRecord(
            sender="attacker@example.com",
            reply_to=None,
            return_path=None,
            subject="Synthetic Phishing",
            date="Today",
            body_text=text,
            links=[],
            attachments=[]
        )
