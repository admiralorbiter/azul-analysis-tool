#!/usr/bin/env python3
"""
CLI server entrypoint for the Azul Solver & Analysis Toolkit.

This module is referenced by the console_script entry:
  azserver = api.server:main

It mirrors the behavior of start_server.py while living inside the
`api` package so packaging can include it cleanly.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from .app import create_app


def _parse_port(argv: list[str]) -> int:
    if len(argv) > 1:
        try:
            return int(argv[1])
        except ValueError:
            print(f"Invalid port number: {argv[1]}")
            sys.exit(1)
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass
    return 8000


def main() -> None:
    app = create_app()
    port = _parse_port(sys.argv)

    print("🚀 Starting Azul Solver & Analysis Toolkit...")
    print(f"📱 Web UI: http://localhost:{port}")
    print(f"🔧 API: http://localhost:{port}/api")
    print(f"💚 Health: http://localhost:{port}/healthz")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=True,
    )


if __name__ == "__main__":
    main()


