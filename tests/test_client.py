import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from dsco_exec import Client, DscoExecError


class Handler(BaseHTTPRequestHandler):
    seen = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Handler.seen.append((self.path, self.headers["Authorization"], body))
        if body["arguments"].get("quantity") == -1:
            out = {"success": True, "result": {"isError": True, "content": [{"type": "text", "text": "bad quantity"}]}}
        else:
            out = {"success": True, "result": {"structuredContent": {"algorithm": "twap", "children": []}}}
        data = json.dumps(out).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(data))); self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


@pytest.fixture
def server():
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


def test_twap_posts_namespaced_tool_with_bearer(server):
    plan = Client("sk-dsco-test", base_url=server).twap("buy", 100, "2026-10-08T13:30:00Z", "2026-10-08T20:00:00Z", slices=4)
    path, auth, body = Handler.seen[-1]
    assert path == "/api/v1/tools/execute" and auth == "Bearer sk-dsco-test"
    assert body["tool"] == "distributed-execution:twap_schedule" and body["arguments"]["slices"] == 4
    assert plan["algorithm"] == "twap"


def test_error_results_raise(server):
    with pytest.raises(DscoExecError, match="bad quantity"):
        Client("k", base_url=server).twap("buy", -1, "a", "b")


def test_missing_key(monkeypatch):
    monkeypatch.delenv("DSCO_API_KEY", raising=False)
    with pytest.raises(DscoExecError):
        Client()
