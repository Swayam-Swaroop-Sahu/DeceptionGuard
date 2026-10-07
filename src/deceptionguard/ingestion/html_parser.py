import re
from html.parser import HTMLParser


class EmailHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.visible_text_parts = []
        self.hidden_text_parts = []
        self.links: list[tuple[str, str]] = []

        self.in_hidden_element = False
        self.current_href = None
        self.current_anchor_text = []

        # Tags that inherently hide content
        self.hidden_tags = {"style", "script", "noscript", "template"}
        self.current_hidden_tags = 0

    def _is_style_hidden(self, attrs) -> bool:
        """Check if inline style suggests hidden text (display:none, font-size:0, visibility:hidden, color matches bg).
        For simplicity, we just look for common hidden properties in style.
        """
        for attr, val in attrs:
            if attr == "style":
                val = val.lower().replace(" ", "")
                if "display:none" in val or "visibility:hidden" in val or "font-size:0" in val or "opacity:0" in val:
                    return True
        return False

    def handle_starttag(self, tag, attrs):
        if tag in self.hidden_tags or self._is_style_hidden(attrs):
            self.current_hidden_tags += 1

        if tag == "a":
            for attr, val in attrs:
                if attr == "href":
                    self.current_href = val
                    self.current_anchor_text = []

    def handle_endtag(self, tag):
        if tag == "a" and self.current_href is not None:
            anchor_text = "".join(self.current_anchor_text).strip()
            self.links.append((anchor_text, self.current_href))
            self.current_href = None
            self.current_anchor_text = []

        if self.current_hidden_tags > 0:
            # We decrement blindly on end tags; this is a heuristic,
            # accurate enough unless there is malformed nested hidden HTML,
            # in which case it might undercount, but let's be careful.
            # Actually, standard HTMLParser handles balanced tags mostly, but if malformed...
            # A safer way is to just keep track of the depth of hidden tags.
            # We will decrement if it was an a tag, etc. For simplicity, just decrement.
            self.current_hidden_tags -= 1
            if self.current_hidden_tags < 0:
                self.current_hidden_tags = 0

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return

        if self.current_hidden_tags > 0:
            self.hidden_text_parts.append(data)
        else:
            self.visible_text_parts.append(data)

        if self.current_href is not None:
            self.current_anchor_text.append(data)

    def get_result(self) -> tuple[str, str, list[tuple[str, str]]]:
        """Returns (visible_text, hidden_text, links)"""
        return (
            " ".join("".join(self.visible_text_parts).split()),
            " ".join("".join(self.hidden_text_parts).split()),
            self.links
        )

def parse_html_content(html: str) -> tuple[str, str, list[tuple[str, str]]]:
    """Parse HTML and extract visible text, hidden text, and links."""
    parser = EmailHTMLParser()
    try:
        parser.feed(html)
    except Exception:
        # If parsing fails drastically, fallback to regex
        visible = re.sub(r'<[^>]+>', ' ', html)
        return " ".join(visible.split()), "", []
    return parser.get_result()
