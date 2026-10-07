"""DeceptionGuard HTTP Server for the Professional Web UI.

Uses only stdlib `http.server`.
Provides static file serving (securely) and a JSON API for analysis.
"""

from __future__ import annotations

import json
import logging
import mimetypes
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from deceptionguard.evidence import detect_all
from deceptionguard.ingestion.parser import parse_eml_string
from deceptionguard.intent_graph.extractor import extract_intent_graph
from deceptionguard.risk_engine.scorer import score_email

logger = logging.getLogger(__name__)

# The directory containing static UI files
STATIC_DIR = Path(__file__).parent / "static"


def _set_security_headers(handler: BaseHTTPRequestHandler) -> None:
    """Set mandatory security headers for all responses."""
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Referrer-Policy", "no-referrer")
    # Very strict CSP. Allow styles and scripts only from 'self'. No inline!
    handler.send_header(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none';"
    )


class DeceptionGuardHandler(BaseHTTPRequestHandler):
    """Handles API requests and static file serving."""

    def do_GET(self) -> None:
        """Serve static files and results."""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path.startswith("/api/v1/results/"):
            self._handle_results_get(path)
            return

        # Default to index.html
        if path == "/" or path == "":
            path = "/index.html"

        # Prevent path traversal
        try:
            # Resolve resolves symlinks and normalizes path
            safe_base = STATIC_DIR.resolve()
            target_path = (STATIC_DIR / path.lstrip("/")).resolve()

            # Check if target is within base directory
            if not str(target_path).startswith(str(safe_base)):
                self.send_error(403, "Forbidden")
                return
        except Exception:
            self.send_error(400, "Bad Request")
            return

        if not target_path.exists() or not target_path.is_file():
            self.send_error(404, "Not Found")
            return

        # Serve the file
        mime_type, _ = mimetypes.guess_type(str(target_path))
        mime_type = mime_type or "application/octet-stream"

        try:
            with open(target_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache") # per requirements, or maybe just for API?
            _set_security_headers(self)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            logger.error(f"Error serving {path}: {e}")
            self.send_error(500, "Internal Server Error")

    def do_POST(self) -> None:
        """Handle API requests."""
        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path == "/api/v1/analyze":
            self._handle_analyze()
        elif parsed_path.path == "/api/v1/batch":
            self._handle_batch()
        else:
            self.send_error(404, "API Endpoint Not Found")

    def _handle_analyze(self) -> None:
        """Process an email for analysis."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 10 * 1024 * 1024:  # 10MB limit
                self.send_error(413, "Payload Too Large")
                return

            post_data = self.rfile.read(content_length)

            # We expect raw EML content or JSON with 'content'
            content_type = self.headers.get("Content-Type", "")

            if "application/json" in content_type:
                data = json.loads(post_data.decode("utf-8"))
                raw_eml = data.get("content", "")
            else:
                raw_eml = post_data.decode("utf-8")

            if not raw_eml:
                self._send_json(400, {"error": "Empty content"})
                return

            # Run pipeline
            record = parse_eml_string(raw_eml)
            graph = extract_intent_graph(record)
            evidence_list = detect_all(record)
            result = score_email(graph, evidence_list)

            # Determine risk level
            if result.total_score >= 70:
                risk_level = "HIGH"
            elif result.total_score >= 40:
                risk_level = "MEDIUM"
            elif result.total_score > 0:
                risk_level = "LOW"
            else:
                risk_level = "MINIMAL"

            response_data = {
                "score": result.total_score,
                "level": risk_level,
                "factors": [
                    {
                        "name": f.name,
                        "weight": f.weight,
                        "contribution": f.contribution,
                        "category": f.category
                    } for f in result.factors if f.contribution > 0
                ],
                "graph": graph,
                "evidence": [e.to_dict() for e in evidence_list],
                "record": {
                    "sender": record.sender,
                    "subject": record.subject,
                    "date": record.date,
                    "body_text": record.body_text,
                    "auth_results": record.auth_results,
                    "links": record.links
                }
            }
            self._send_json(200, response_data)

        except Exception as e:
            logger.exception("Analysis failed")
            self._send_json(500, {"error": str(e)})

    def _handle_batch(self) -> None:
        """Process an mbox file for batch analysis."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 50 * 1024 * 1024:  # 50MB limit
                self.send_error(413, "Payload Too Large")
                return

            post_data = self.rfile.read(content_length)

            import os
            import tempfile

            from deceptionguard.ingestion.parser import parse_mbox

            # Save to temporary file to parse
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(post_data)
                temp_path = f.name

            try:
                records = parse_mbox(temp_path)
            finally:
                os.unlink(temp_path)

            results = []
            for record in records:
                try:
                    graph = extract_intent_graph(record)
                    evidence_list = detect_all(record)
                    result = score_email(graph, evidence_list)

                    if result.total_score >= 70:
                        risk_level = "HIGH"
                    elif result.total_score >= 40:
                        risk_level = "MEDIUM"
                    elif result.total_score > 0:
                        risk_level = "LOW"
                    else:
                        risk_level = "MINIMAL"

                    results.append({
                        "score": result.total_score,
                        "level": risk_level,
                        "subject": record.subject or "(No Subject)",
                        "sender": record.sender,
                    })
                except Exception as e:
                    logger.error(f"Failed to score record in batch: {e}")

            self._send_json(200, {"results": results})
        except Exception as e:
            logger.exception("Batch analysis failed")
            self._send_json(500, {"error": str(e)})

    def _handle_results_get(self, path: str) -> None:
        """Serve files from the results directory."""
        from deceptionguard.evaluation.run_evaluation import RESULTS_DIR
        filename = path.replace("/api/v1/results/", "")

        target_path = (RESULTS_DIR / filename).resolve()

        try:
            if not str(target_path).startswith(str(RESULTS_DIR.resolve())):
                self.send_error(403, "Forbidden")
                return
        except Exception:
            self.send_error(400, "Bad Request")
            return

        if not target_path.exists() or not target_path.is_file():
            self.send_error(404, "Result file not found")
            return

        try:
            with open(target_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            _set_security_headers(self)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            logger.error(f"Error serving result file {path}: {e}")
            self.send_error(500, "Internal Server Error")

    def _send_json(self, status: int, data: dict[str, Any]) -> None:
        """Helper to send JSON response."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        _set_security_headers(self)
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Start the DeceptionGuard UI server."""
    if host != "127.0.0.1":
        print(f"WARNING: Binding to non-localhost address {host}. Ensure this is intended.")

    # Ensure static directory exists
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    server = ThreadingHTTPServer((host, port), DeceptionGuardHandler)
    print(f"Starting DeceptionGuard Console on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()
