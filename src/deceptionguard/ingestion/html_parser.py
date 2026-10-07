import re
from html.parser import HTMLParser


class EmailHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.visible_text_parts = []
        self.hidden_text_parts = []
        self.links: list[tuple[str, str]] = []

        self.hidden_stack = []
        self.a_stack = []

        # Tags that inherently hide content
        self.hidden_tags = {"style", "script", "noscript", "template"}
        self.void_elements = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def _is_style_hidden(self, attrs) -> bool:
        """Check if inline style suggests hidden text (display:none, font-size:0, visibility:hidden, color matches bg)."""
        for attr, val in attrs:
            if attr == "style" and val:
                val = val.lower().replace(" ", "")
                if ("display:none" in val or "visibility:hidden" in val or 
                    "font-size:0" in val or "opacity:0" in val or
                    "width:0" in val or "height:0" in val or
                    "left:-99" in val or "top:-99" in val):
                    return True
        return False

    def handle_starttag(self, tag, attrs):
        is_hidden = tag in self.hidden_tags or self._is_style_hidden(attrs)
        if tag not in self.void_elements:
            self.hidden_stack.append((tag, is_hidden))

        if tag == "a":
            href = None
            for attr, val in attrs:
                if attr == "href":
                    href = val
                    break
            self.a_stack.append((href, []))
            
    def handle_startendtag(self, tag, attrs):
        pass # void element, no stack push/pop

    def handle_endtag(self, tag):
        if tag == "a" and self.a_stack:
            href, anchor_text = self.a_stack.pop()
            if href is not None:
                self.links.append(("".join(anchor_text).strip(), href))

        for i in range(len(self.hidden_stack) - 1, -1, -1):
            if self.hidden_stack[i][0] == tag:
                self.hidden_stack = self.hidden_stack[:i]
                break

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return

        is_currently_hidden = any(h for _, h in self.hidden_stack)

        if is_currently_hidden:
            self.hidden_text_parts.append(data)
        else:
            self.visible_text_parts.append(data)

        if self.a_stack:
            self.a_stack[-1][1].append(data)

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
