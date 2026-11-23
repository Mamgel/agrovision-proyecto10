"""Endpoints de carga de imagenes y disparo de inferencias."""
import json
import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.config import settings
from backend.database import get_db
from backend.models import Crop, Image, Inference, Incident, User
from backend.schemas import ImageOut, InferenceOut

from ai_service.inference import get_classifier

router = APIRouter(prefix="/images", tags=["images"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _severity_from_counts(n_mancha: int, n_seca: int, total: int) -> str | None:
    """Regla simple para calcular severidad de la incidencia."""
    if total == 0:
        return None
    ratio = (n_mancha + n_seca) / total
    if ratio >= 0.5:
        return "alta"
    if ratio >= 0.25:
        return "media"
    if ratio > 0:
        return "baja"
    return None


@router.post("", response_model=ImageOut, status_code=status.HTTP_201_CREATED)
def upload_image(
    file: UploadFile = File(...),
    crop_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Sube una imagen asociada opcionalmente a un cultivo."""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extension {ext} no permitida")

    # Validar tamano
    file.file.seek(0, 2)
    size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande")

    # Validar cultivo si se especifica
    if crop_id is not None:
        crop = db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise HTTPException(status_code=404, detail="Cultivo no encontrado")
        if user.role != "admin" and crop.lot.farm.owner_id != user.id:
            raise HTTPException(status_code=403, detail="Sin permiso sobre el cultivo")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest = Path(settings.upload_dir) / unique_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)

    img = Image(
        crop_id=crop_id,
        file_path=str(dest),
        original_filename=file.filename,
        uploaded_by_id=user.id,
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.post("/{image_id}/analyze", response_model=InferenceOut)
def analyze_image(
    image_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Ejecuta el modelo de IA sobre una imagen cargada."""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    if user.role != "admin" and image.uploaded_by_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso")

    clf = get_classifier()
    result = clf.predict(image.file_path)

    sev = _severity_from_counts(result["n_mancha"], result["n_seca"], result["n_leaves_detected"])

    inf = Inference(
        image_id=image.id,
        model_version=result["model_version"],
        n_leaves_detected=result["n_leaves_detected"],
        n_sana=result["n_sana"],
        n_mancha=result["n_mancha"],
        n_seca=result["n_seca"],
        avg_confidence=result["avg_confidence"],
        inference_time_ms=result["inference_time_ms"],
        annotated_path=result.get("annotated_path"),
        raw_detections_json=json.dumps(result.get("detections", []), default=str),
    )
    db.add(inf)
    db.commit()
    db.refresh(inf)

    # Crear incidencia automatica si corresponde
    if sev:
        incident = Incident(
            inference_id=inf.id,
            severity=sev,
            description=f"Deteccion automatica: {result['n_mancha']} mancha, {result['n_seca']} seca, "
                        f"{result['n_sana']} sana (confianza media {result['avg_confidence']:.2f})",
        )
        db.add(incident)
        db.commit()

    return inf


@router.get("", response_model=list[ImageOut])
def list_images(
    crop_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Image)
    if crop_id is not None:
        query = query.filter(Image.crop_id == crop_id)
    if user.role != "admin":
        query = query.filter(Image.uploaded_by_id == user.id)
    return query.order_by(Image.uploaded_at.desc()).all()
