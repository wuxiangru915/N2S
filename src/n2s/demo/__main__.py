"""Entry point: ``python -m n2s.demo``."""

import uvicorn

from n2s.demo.server import create_demo_app


if __name__ == "__main__":
    app = create_demo_app()
    print("Starting N2S demo server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
