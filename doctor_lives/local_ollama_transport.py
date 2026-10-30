"""Bounded direct loopback Ollama transport. No proxy or redirect following."""
from __future__ import annotations

import http.client

def post_local_ollama(hostname: str, port: int, route: str, payload: bytes,
                      *, timeout: float = 90, max_response_bytes: int = 128000) -> bytes:
    if hostname not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("Ollama transport requires a loopback host")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("Ollama transport requires an explicit local port")
    if route not in ("/api/generate", "/api/embed"):
        raise ValueError("Ollama transport route is not reviewed")
    if not isinstance(payload, bytes):
        raise TypeError("Ollama request must be JSON bytes")
    if type(max_response_bytes) is not int or not 1 <= max_response_bytes <= 2000000:
        raise ValueError("Invalid bounded Ollama response limit")
    address = "::1" if hostname == "::1" else "127.0.0.1"
    connection = http.client.HTTPConnection(address, port, timeout=timeout)
    try:
        connection.request("POST", route, body=payload,
                           headers={"Content-Type": "application/json", "Accept": "application/json"})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("Local Ollama refused HTTP status %d" % response.status)
        data = response.read(max_response_bytes + 1)
        if len(data) > max_response_bytes:
            raise ValueError("Local Ollama response exceeds bounded size")
        return data
    finally:
        connection.close()
