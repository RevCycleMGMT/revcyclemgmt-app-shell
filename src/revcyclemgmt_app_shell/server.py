"""Local HTTP server for the app shell proof."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .views import render_route

ROOT = Path(__file__).resolve().parents[2]


class AppShellHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        parsed = urlsplit(self.path)
        if parsed.path.startswith("/assets/"):
            self.serve_asset(parsed.path.removeprefix("/assets/"))
            return
        status, content_type, body = render_route(parsed.path, parsed.query)
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_asset(self, name: str) -> None:
        path = ROOT / "docs" / "assets" / name
        if not path.exists() or path.suffix.lower() != ".svg":
            self.send_response(404)
            self.end_headers()
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: object) -> None:
        return


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Serve the RevCycleMGMT app shell proof.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), AppShellHandler)
    print(f"Serving RevCycleMGMT app shell at http://{args.host}:{args.port}/app/intake")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
