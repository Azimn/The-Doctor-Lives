"""Two-server redirect and proxy-denial controls for both Ollama research adapters."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import threading
import unittest
from unittest.mock import patch
from doctor_lives.open_inference import LocalOllama
from doctor_lives.semantic_intentions import LocalOllamaEmbeddings
from doctor_lives.local_ollama_transport import post_local_ollama

@contextmanager
def listener(mode, redirect_to=""):
    calls = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass
        def do_POST(self):
            calls.append(("POST", self.path))
            if mode == "redirect":
                self.send_response(302)
                self.send_header("Location", redirect_to)
                self.end_headers()
                return
            if mode == "oversize":
                body = b"x" * 150000
            elif self.path == "/api/generate":
                body = json.dumps({"response": json.dumps({"intentions": [
                    "I might read the research document.",
                    "I could write my notes.",
                    "I wish I could visit the village."]})}).encode()
            elif self.path == "/api/embed":
                size = int(self.headers["Content-Length"])
                incoming = json.loads(self.rfile.read(size))
                body = json.dumps({"embeddings": [[0.25, 0.75] for _ in incoming["input"]]}).encode()
            else:
                body = b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass
        def do_GET(self):
            calls.append(("GET", self.path))
            self.send_response(200)
            self.end_headers()
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port, calls
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

class LocalOllamaTransportDenial(unittest.TestCase):
    def test_positive_both_ports(self):
        with listener("ok") as (port, calls):
            endpoint = "http://127.0.0.1:%d" % port
            proposals = LocalOllama("local-test", endpoint).propose({})
            vectors = LocalOllamaEmbeddings("local-test", endpoint).embed_many(["one", "two"])
            self.assertEqual(len(proposals), 3)
            self.assertEqual(vectors, [[0.25, 0.75], [0.25, 0.75]])
            self.assertEqual(calls, [("POST", "/api/generate"), ("POST", "/api/embed")])

    def test_redirect_to_other_loopback_port_not_followed(self):
        with listener("ok") as (other_port, other_calls):
            for route in ("/api/generate", "/api/embed"):
                with self.subTest(route=route):
                    with listener("redirect", "http://127.0.0.1:%d%s" %
                                  (other_port, route)) as (port, calls):
                        endpoint = "http://127.0.0.1:%d" % port
                        with self.assertRaisesRegex(ValueError, "HTTP status 302"):
                            if route == "/api/generate":
                                LocalOllama("local-test", endpoint).propose({})
                            else:
                                LocalOllamaEmbeddings("local-test", endpoint).embed_many(["one"])
                        self.assertEqual(calls, [("POST", route)])
                        self.assertEqual(other_calls, [])

    def test_redirect_to_nonloopback_not_followed(self):
        for route in ("/api/generate", "/api/embed"):
            with self.subTest(route=route):
                with listener("redirect", "http://192.0.2.1:40001" + route) as (port, calls):
                    endpoint = "http://127.0.0.1:%d" % port
                    with self.assertRaisesRegex(ValueError, "HTTP status 302"):
                        if route == "/api/generate":
                            LocalOllama("local-test", endpoint).propose({})
                        else:
                            LocalOllamaEmbeddings("local-test", endpoint).embed_many(["one"])
                    self.assertEqual(calls, [("POST", route)])

    def test_proxy_environment_is_ignored(self):
        with listener("ok") as (proxy_port, proxy_calls):
            with listener("ok") as (port, calls):
                env = {"HTTP_PROXY": "http://127.0.0.1:%d" % proxy_port,
                       "HTTPS_PROXY": "http://127.0.0.1:%d" % proxy_port,
                       "ALL_PROXY": "http://127.0.0.1:%d" % proxy_port,
                       "NO_PROXY": ""}
                with patch.dict(os.environ, env):
                    endpoint = "http://localhost:%d" % port
                    self.assertEqual(len(LocalOllama("local-test", endpoint).propose({})), 3)
                    self.assertEqual(len(LocalOllamaEmbeddings(
                        "local-test", endpoint).embed_many(["one"])), 1)
                self.assertEqual(proxy_calls, [])
                self.assertEqual(calls, [("POST", "/api/generate"), ("POST", "/api/embed")])

    def test_host_route_and_response_size_guards(self):
        for host in ("example.org", "192.0.2.1"):
            with self.assertRaisesRegex(ValueError, "loopback"):
                post_local_ollama(host, 11434, "/api/generate", b"{}")
        with self.assertRaisesRegex(ValueError, "route"):
            post_local_ollama("127.0.0.1", 11434, "/api/delete", b"{}")
        with listener("oversize") as (port, calls):
            with self.assertRaisesRegex(ValueError, "bounded size"):
                post_local_ollama("127.0.0.1", port, "/api/generate", b"{}",
                                  max_response_bytes=1024)
            self.assertEqual(calls, [("POST", "/api/generate")])

if __name__ == "__main__":
    unittest.main()
