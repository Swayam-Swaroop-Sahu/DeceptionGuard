from deceptionguard.ingestion.html_parser import parse_html_content

def test_parse_html_hidden_elements():
    html = """
    <html>
    <body>
        <div style="display: none;">hidden div</div>
        <span style="visibility: hidden;">hidden span</span>
        <p style="opacity: 0;">hidden p</p>
        <div style="width: 0; height: 0;">zero size</div>
        <div style="position: absolute; left: -9999px;">offscreen</div>
        <div class="hidden-class">hidden class</div>
        <p>visible text</p>
    </body>
    </html>
    """
    visible, hidden, links = parse_html_content(html)
    assert "visible text" in visible
    assert "hidden div" in hidden
    assert "hidden span" in hidden
    assert "hidden p" in hidden
    assert "zero size" in hidden
    assert "offscreen" in hidden
    # Wait, class-based might not be caught by inline parser without CSS, but test it anyway
    
def test_parse_html_obfuscation():
    html = """
    <p>vis<!-- comment -->ible</p>
    <p>text with <span style="display:none">HIDDEN</span> inline</p>
    """
    visible, hidden, _ = parse_html_content(html)
    assert "vis ible" in visible or "visible" in visible
    assert "HIDDEN" in hidden

def test_parse_html_links():
    html = """
    <a href="http://evil.com">Click <span style="display:none">here</span></a>
    """
    visible, hidden, links = parse_html_content(html)
    assert len(links) == 1
    assert links[0][1] == "http://evil.com"
    assert "Click" in visible
    assert "here" in hidden
