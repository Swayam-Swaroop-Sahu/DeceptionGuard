import re
import unicodedata

# Zero-width characters
ZERO_WIDTH = {
    "\\u200b", "\\u200c", "\\u200d", "\\uFEFF", "\\u2060"
}

# Bidi control characters
BIDI_CONTROLS = {
    "\\u202a", "\\u202b", "\\u202c", "\\u202d", "\\u202e", "\\u2066", "\\u2067", "\\u2068", "\\u2069"
}

def normalize_text(text: str) -> tuple[str, bool, bool]:
    """
    Normalize text and detect suspicious characters.

    Returns:
        Tuple of (normalized_text, has_bidi_controls, has_zero_width)
    """
    if not text:
        return "", False, False

    # Check for controls before stripping
    has_bidi = any(c.encode('unicode_escape').decode('ascii').lower() in BIDI_CONTROLS for c in text)
    has_zw = any(c.encode('unicode_escape').decode('ascii').lower() in ZERO_WIDTH for c in text)

    # In practice, simpler regex to match characters
    has_bidi = bool(re.search('[\u202a-\u202e\u2066-\u2069]', text))
    has_zw = bool(re.search('[\u200b-\u200d\ufeff\u2060]', text))

    # Strip bidi and zero-width
    clean_text = re.sub('[\u202a-\u202e\u2066-\u2069\u200b-\u200d\ufeff\u2060]', '', text)

    # Normalize to NFKC
    clean_text = unicodedata.normalize("NFKC", clean_text)

    return clean_text, has_bidi, has_zw
