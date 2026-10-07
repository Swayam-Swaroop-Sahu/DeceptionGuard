import json
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from deceptionguard.ui.server import run_server


@pytest.fixture(scope="module")
def ui_server():
    """Start UI server on a random port in a background thread."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()

    thread = threading.Thread(target=run_server, kwargs={"host": "127.0.0.1", "port": port}, daemon=True)
    thread.start()
    time.sleep(0.5) # Wait for server to start
    yield f"http://127.0.0.1:{port}"

def test_static_files_and_headers(ui_server):
    req = Request(f"{ui_server}/")
    with urlopen(req) as response:
        assert response.status == 200
        headers = dict(response.headers)
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["Referrer-Policy"] == "no-referrer"
        assert "Content-Security-Policy" in headers

def test_analyze_api_valid(ui_server):
    payload = json.dumps({"content": "From: test@example.com\nSubject: Test\n\nHello"}).encode("utf-8")
    req = Request(f"{ui_server}/api/v1/analyze", data=payload, headers={"Content-Type": "application/json"})
    with urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert "score" in data
        assert "level" in data
        assert "factors" in data

def test_analyze_api_xss_payload(ui_server):
    """Test that XSS payloads in email don't crash parser and are returned safely (defanging is done on client, but JSON must be valid)."""
    malicious_eml = 'From: <script>alert(1)</script>@evil.com\nSubject: javascript:alert(1)\n\n<script>eval()</script>'
    payload = json.dumps({"content": malicious_eml}).encode("utf-8")
    req = Request(f"{ui_server}/api/v1/analyze", data=payload, headers={"Content-Type": "application/json"})
    with urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert "script" in data["record"]["sender"] # Parser might strip <>, but script is there

def test_path_traversal(ui_server):
    try:
        req = Request(f"{ui_server}/../../../etc/passwd")
        urlopen(req)
        raise AssertionError("Should have thrown 403 or 400")
    except HTTPError as e:
        assert e.code in [403, 400, 404]

def test_results_api_not_found(ui_server):
    try:
        req = Request(f"{ui_server}/api/v1/results/missing.json")
        urlopen(req)
        raise AssertionError("Should have thrown 404")
    except HTTPError as e:
        assert e.code == 404

def test_results_api_path_traversal(ui_server):
    try:
        req = Request(f"{ui_server}/api/v1/results/../../ui/server.py")
        urlopen(req)
        raise AssertionError("Should have thrown 403 or 404 or 400")
    except HTTPError as e:
        assert e.code in [403, 404, 400]

def test_batch_api_valid(ui_server):
    mbox_content = b"From mbox@test\nFrom: test@example.com\nSubject: Test\n\nHello\n"
    req = Request(f"{ui_server}/api/v1/batch", data=mbox_content, headers={"Content-Type": "application/octet-stream"})
    with urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["sender"] == "test@example.com"
