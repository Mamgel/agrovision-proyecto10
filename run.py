"""Lanzador unificado: arranca la API FastAPI en un hilo y Gradio en otro.

Uso:
    python run.py            # ambos
    python run.py api        # solo API
    python run.py frontend   # solo frontend (requiere API corriendo aparte)
"""
import sys
import threading
import time

import uvicorn

from backend.config import settings


def run_api():
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level="info",
    )


def run_frontend():
    from frontend.gradio_app import launch
    launch()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    if mode == "api":
        run_api()
    elif mode == "frontend":
        run_frontend()
    else:
        t = threading.Thread(target=run_api, daemon=True)
        t.start()
        time.sleep(3)
        run_frontend()
