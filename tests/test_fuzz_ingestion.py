import random
import string

from deceptionguard.ingestion.parser import parse_eml_string


def generate_random_string(length: int) -> str:
    return ''.join(random.choices(string.printable, k=length))

def generate_malformed_email(seed: int) -> str:
    random.seed(seed)

    # Randomly corrupt different parts
    corruption_type = random.randint(0, 5)

    if corruption_type == 0:
        # Missing headers
        return "Just a body, no headers at all.\n" + generate_random_string(100)
    elif corruption_type == 1:
        # Malformed From
        return "From: \nTo: b@c.com\n\nBody"
    elif corruption_type == 2:
        # Binary garbage
        return generate_random_string(500)
    elif corruption_type == 3:
        # Extremely long header
        return f"From: a@b.com\nSubject: {'A'*10000}\n\nBody"
    elif corruption_type == 4:
        # Missing boundary in multipart
        return """From: a@b.com
Content-Type: multipart/mixed; boundary="missing"

--missing
Content-Type: text/plain

text
"""
    else:
        # Control characters in headers
        return "From: a@b.com\x00\x01\nSubject: test\n\nbody"

def test_fuzz_parser_no_exceptions():
    """Fuzz test generating malformed inputs, ensuring no unhandled crashes."""
    # We expect ParseError on some inputs, but NO other exceptions (e.g. ValueError, IndexError, RecursionError)

    for i in range(100):
        raw_email = generate_malformed_email(seed=i)

        try:
            parse_eml_string(raw_email)
        except Exception as e:
            # Only ParseError is allowed.
            from deceptionguard.ingestion.parser import ParseError
            assert isinstance(e, ParseError), f"Unexpected exception type {type(e)} on seed {i}: {e}"
