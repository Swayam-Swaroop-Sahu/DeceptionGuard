import json
import re
from pathlib import Path
from urllib.parse import urlparse

from ..ingestion.email_record import EmailRecord
from .schema import Evidence, Severity

# Load brand domains
BRAND_FILE = Path(__file__).parent.parent / "data" / "brand_domains.json"
try:
    with open(BRAND_FILE, encoding="utf-8") as f:
        BRAND_DATA = json.load(f)
except FileNotFoundError:
    BRAND_DATA = []

SUSPICIOUS_TLDS = {".xyz", ".top", ".biz", ".info", ".club", ".online", ".site", ".tk", ".ml", ".ga", ".cf", ".gq"}
SHORTENERS = {"bit.ly", "t.co", "tinyurl.com", "goo.gl", "ow.ly", "is.gd", "buff.ly", "adf.ly"}
ARCHIVE_EXTS = {"zip", "rar", "7z", "tar", "gz"}
EXEC_EXTS = {"exe", "scr", "vbs", "bat", "cmd", "js", "ps1", "wsf", "jar", "msi"}
MACRO_EXTS = {"docm", "xlsm", "pptm"}
HTML_EXTS = {"html", "htm", "shtml"}


def _extract_domain(email_addr: str) -> str:
    """Extract domain from an email address string (e.g. 'John Doe <john@doe.com>')."""
    match = re.search(r'@([\w.-]+)>?', email_addr)
    return match.group(1).lower() if match else ""


def _extract_display_name(email_addr: str) -> str:
    """Extract display name from an email address string."""
    match = re.match(r'^(.*?)\s*<', email_addr)
    if match:
        name = match.group(1).strip(' \'"')
        return name
    # If no brackets, maybe just an email or just a name.
    if '@' not in email_addr:
        return email_addr.strip(' \'"')
    return ""


def detect_sender_mismatch(record: EmailRecord) -> list[Evidence]:
    evidences = []

    sender_domain = _extract_domain(record.sender)
    display_name = _extract_display_name(record.sender).lower()

    # 1. Display name vs sender domain
    # Example: Display name contains a well-known brand or domain that differs from actual sender domain
    if display_name and sender_domain:
        # Check if display name looks like a domain or known brand, and doesn't match
        if '.' in display_name and not display_name.endswith(sender_domain) and not sender_domain.endswith(display_name):
             evidences.append(Evidence(
                 evidence_type="DISPLAY_NAME_DOMAIN_MISMATCH",
                 severity=Severity.HIGH,
                 explanation=f"Display name '{display_name}' appears to be a domain different from sender domain '{sender_domain}'.",
                 header_ref="From"
             ))

        # Check against brands
        for brand_info in BRAND_DATA:
            brand_name = brand_info["brand"].lower()
            if brand_name in display_name:
                # Expect sender domain to be in the brand's domains
                if not any(sender_domain == d or sender_domain.endswith("." + d) for d in brand_info["domains"]):
                    evidences.append(Evidence(
                         evidence_type="DISPLAY_NAME_BRAND_MISMATCH",
                         severity=Severity.CRITICAL,
                         explanation=f"Display name claims to be '{brand_info['brand']}' but sender domain '{sender_domain}' is not authorized.",
                         header_ref="From"
                     ))

    # 2. From vs Reply-To vs Return-Path
    if record.reply_to:
        reply_domain = _extract_domain(record.reply_to)
        if reply_domain and reply_domain != sender_domain:
             evidences.append(Evidence(
                 evidence_type="REPLY_TO_MISMATCH",
                 severity=Severity.MEDIUM,
                 explanation=f"Reply-To domain '{reply_domain}' differs from sender domain '{sender_domain}'.",
                 header_ref="Reply-To"
             ))

    if record.return_path:
        return_domain = _extract_domain(record.return_path)
        if return_domain and return_domain != sender_domain:
             evidences.append(Evidence(
                 evidence_type="RETURN_PATH_MISMATCH",
                 severity=Severity.LOW,
                 explanation=f"Return-Path domain '{return_domain}' differs from sender domain '{sender_domain}'.",
                 header_ref="Return-Path"
             ))

    return evidences


def _damerau_levenshtein(s1: str, s2: str) -> int:
    """Calculate the Damerau-Levenshtein distance between two strings."""
    len1, len2 = len(s1), len(s2)
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,      # deletion
                d[i][j - 1] + 1,      # insertion
                d[i - 1][j - 1] + cost  # substitution
            )
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost) # transposition
    return d[len1][len2]


def detect_brand_lookalike(domain: str) -> Evidence | None:
    """Detect if a domain is a lookalike to a known brand."""
    if not domain:
        return None

    # Extract root domain (e.g., 'example.com' from 'sub.example.com')
    parts = domain.split('.')
    if len(parts) >= 2:
        root_domain = parts[-2] + '.' + parts[-1]
        name_part = parts[-2]
    else:
        root_domain = domain
        name_part = domain

    # Exact match - benign (handled outside if needed, or just return None here)
    for brand_info in BRAND_DATA:
        if any(domain == d or domain.endswith("." + d) for d in brand_info["domains"]):
            return None # Legitimate brand domain

    # Check for homoglyphs or typos
    for brand_info in BRAND_DATA:
        # Check if the brand name is literally embedded in a suspicious way
        # e.g. paypal-support.com
        if brand_info["brand"].lower() in name_part and root_domain not in brand_info["domains"]:
            return Evidence(
                 evidence_type="BRAND_NAME_EMBEDDED",
                 severity=Severity.HIGH,
                 explanation=f"Domain '{domain}' embeds brand name '{brand_info['brand']}' but is not an official domain.",
                 text_span=domain
             )

        # Typo-squatting (Damerau-Levenshtein distance <= 1 for short, <= 2 for long)
        for known_domain in brand_info["domains"]:
            known_name = known_domain.split('.')[0]
            if len(known_name) > 3:
                dist = _damerau_levenshtein(name_part, known_name)
                # If distance is small, flag it
                threshold = 1 if len(known_name) <= 5 else 2
                if 0 < dist <= threshold:
                    return Evidence(
                         evidence_type="BRAND_TYPOSQUATTING",
                         severity=Severity.HIGH,
                         explanation=f"Domain '{domain}' is visually or typographically similar to official brand domain '{known_domain}'.",
                         text_span=domain
                     )

    return None


def detect_url_risks(record: EmailRecord) -> list[Evidence]:
    evidences = []

    for anchor, href in record.links:
        parsed = urlparse(href)
        domain = parsed.netloc.lower()

        if not domain:
            continue

        # 1. IP literal
        if re.match(r'^[\d\.]+$', domain):
            evidences.append(Evidence(
                 evidence_type="URL_IP_LITERAL",
                 severity=Severity.HIGH,
                 explanation=f"URL uses an IP address instead of a domain name: {domain}",
                 text_span=href
             ))

        # 2. Userinfo (@ tricks)
        if '@' in parsed.netloc:
            evidences.append(Evidence(
                 evidence_type="URL_USERINFO_TRICK",
                 severity=Severity.CRITICAL,
                 explanation=f"URL contains credentials or routing trick using '@': {parsed.netloc}",
                 text_span=href
             ))

        # 3. URL Shorteners
        if domain in SHORTENERS:
            evidences.append(Evidence(
                 evidence_type="URL_SHORTENER",
                 severity=Severity.MEDIUM,
                 explanation=f"URL uses a link shortener service: {domain}",
                 text_span=href
             ))

        # 4. Suspicious TLD
        tld = "." + domain.split('.')[-1]
        if tld in SUSPICIOUS_TLDS:
            evidences.append(Evidence(
                 evidence_type="URL_SUSPICIOUS_TLD",
                 severity=Severity.MEDIUM,
                 explanation=f"URL uses a suspicious top-level domain: {tld}",
                 text_span=href
             ))

        # 5. Excessive subdomains
        if len(domain.split('.')) > 4:
            evidences.append(Evidence(
                 evidence_type="URL_EXCESSIVE_SUBDOMAINS",
                 severity=Severity.LOW,
                 explanation=f"URL domain has an excessive number of subdomains: {domain}",
                 text_span=href
             ))

        # 6. Anchor-href mismatch
        if anchor:
            anchor_parsed = urlparse(anchor) if "://" in anchor else urlparse("http://" + anchor)
            anchor_domain = anchor_parsed.netloc.lower()
            if anchor_domain and '.' in anchor_domain:
                # Anchor looks like a URL, does it match href?
                if anchor_domain != domain:
                    # Allow subdomains matching
                    if not (anchor_domain.endswith("." + domain) or domain.endswith("." + anchor_domain)):
                        evidences.append(Evidence(
                             evidence_type="URL_ANCHOR_MISMATCH",
                             severity=Severity.CRITICAL,
                             explanation=f"Anchor text suggests domain '{anchor_domain}' but link goes to '{domain}'.",
                             text_span=f"[{anchor}]({href})"
                         ))

        # 7. Brand lookalike
        brand_ev = detect_brand_lookalike(domain)
        if brand_ev:
            brand_ev = Evidence(
                evidence_type=brand_ev.evidence_type,
                severity=brand_ev.severity,
                explanation=brand_ev.explanation,
                text_span=href
            )
            evidences.append(brand_ev)

    return evidences


def detect_auth_failures(record: EmailRecord) -> list[Evidence]:
    evidences = []

    for method, verdict in record.auth_results.items():
        if verdict in ["fail", "softfail", "hardfail", "neutral"]:
            severity = Severity.HIGH if verdict in ["fail", "hardfail"] else Severity.MEDIUM
            evidences.append(Evidence(
                 evidence_type=f"AUTH_{method.upper()}_FAILURE",
                 severity=severity,
                 explanation=f"Email authentication for {method.upper()} resulted in {verdict}.",
                 header_ref="Authentication-Results"
             ))

    return evidences


def detect_attachment_risks(record: EmailRecord) -> list[Evidence]:
    evidences = []

    for att in record.attachments:
        filename = att["filename"].lower()
        ext = filename.split('.')[-1] if '.' in filename else ""

        # 1. Executables
        if ext in EXEC_EXTS:
            evidences.append(Evidence(
                 evidence_type="ATTACHMENT_EXECUTABLE",
                 severity=Severity.CRITICAL,
                 explanation=f"Attachment '{filename}' is an executable file.",
                 header_ref="Content-Disposition"
             ))

        # 2. Macros
        if ext in MACRO_EXTS:
            evidences.append(Evidence(
                 evidence_type="ATTACHMENT_MACRO_ENABLED",
                 severity=Severity.HIGH,
                 explanation=f"Attachment '{filename}' is a macro-enabled document.",
                 header_ref="Content-Disposition"
             ))

        # 3. HTML Attachments
        if ext in HTML_EXTS:
            evidences.append(Evidence(
                 evidence_type="ATTACHMENT_HTML",
                 severity=Severity.MEDIUM,
                 explanation=f"Attachment '{filename}' is an HTML file, often used for phishing pages.",
                 header_ref="Content-Disposition"
             ))

        # 4. Double Extensions
        if att.get("double_extension", False):
            evidences.append(Evidence(
                 evidence_type="ATTACHMENT_DOUBLE_EXTENSION",
                 severity=Severity.HIGH,
                 explanation=f"Attachment '{filename}' attempts to hide its true extension.",
                 header_ref="Content-Disposition"
             ))

        # 5. Extension Mismatch
        if att.get("extension_mismatch", False):
            evidences.append(Evidence(
                 evidence_type="ATTACHMENT_EXTENSION_MISMATCH",
                 severity=Severity.HIGH,
                 explanation=f"Attachment '{filename}' has an extension that does not match its MIME type '{att['mime_type']}'.",
                 header_ref="Content-Type"
             ))

    return evidences


def detect_all(record: EmailRecord) -> list[Evidence]:
    """Run all evidence detectors on an EmailRecord."""
    evidences = []
    evidences.extend(detect_sender_mismatch(record))
    evidences.extend(detect_url_risks(record))
    evidences.extend(detect_auth_failures(record))
    evidences.extend(detect_attachment_risks(record))

    # Text normalization risks
    if record.has_zero_width or record.has_bidi_controls:
        evidences.append(Evidence(
            evidence_type="TEXT_OBFUSCATION",
            severity=Severity.HIGH,
            explanation="Body contains hidden control characters (Zero-width or Bidi overrides) used for obfuscation."
        ))

    if record.hidden_text:
        evidences.append(Evidence(
            evidence_type="HTML_HIDDEN_TEXT",
            severity=Severity.MEDIUM,
            explanation="HTML body contains invisible text which may confuse text classifiers or humans."
        ))

    return evidences
