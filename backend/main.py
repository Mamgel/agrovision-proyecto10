"""Punto de entrada FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.routers import auth, farms, crops, images, inferences, incidents
from backend.schemas import HealthOut
from ai_service.inference import get_classifier

app = FastAPI(
    title="AgroVision API",
    description="Sistema inteligente para agricultura: monitoreo y detección de enfermedades foliares",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health", response_model=HealthOut, tags=["system"])
def health():
    clf = get_classifier(raise_if_missing=False)
    return HealthOut(
        status="ok",
        model_loaded=clf.is_loaded,
        model_version=clf.model_version,
        env=settings.env,
    )


app.include_router(auth.router)
app.include_router(farms.router)
app.include_router(farms.lots_router)
app.include_router(crops.router)
app.include_router(images.router)
app.include_router(inferences.router)
app.include_router(incidents.router)

# Servir imagenes anotadas (opcional)
app.mount("/static", StaticFiles(directory=settings.upload_dir, check_dir=False), name="static")
