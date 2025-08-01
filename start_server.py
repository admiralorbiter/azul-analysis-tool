#!/usr/bin/env python3
"""
Simple startup script for the Azul Solver & Analysis Toolkit.
Runs the Flask server with integrated UI on a single port.
"""

import sys
import os
from api.app import create_app

def main():
    """Start the Flask server with integrated UI."""
    app = create_app()
    
    # Get port from command line or use default
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    print(f"🚀 Starting Azul Solver & Analysis Toolkit...")
    print(f"📱 Web UI: http://localhost:{port}")
    print(f"🔧 API: http://localhost:{port}/api")
    print(f"💚 Health: http://localhost:{port}/healthz")
    print(f"📖 API Info: http://localhost:{port}/api")
    print(f"\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True
    )

if __name__ == '__main__':
    main() 