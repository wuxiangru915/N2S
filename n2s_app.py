"""
N2S demo entry point (Mock LLM by default, no API key required).

Usage:
    .venv/Scripts/python.exe n2s_app.py

Then open http://localhost:8000
"""

import uvicorn

from n2s.demo.server import create_demo_app


app = create_demo_app()


if __name__ == "__main__":
    print("Starting N2S demo server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
