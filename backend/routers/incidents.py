"""Endpoints del panel de incidencias."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.models import Image, Incident, Inference, User
from backend.schemas import IncidentCreate, IncidentOut, IncidentUpdate

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "operador")),
):
    inf = db.query(Inference).filter(Inference.id == payload.inference_id).first()
    if not inf:
        raise HTTPException(status_code=404, detail="Inferencia no encontrada")
    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    status_filter: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Incident)
    if status_filter:
        query = query.filter(Incident.status == status_filter)
    if severity:
        query = query.filter(Incident.severity == severity)
    if user.role != "admin":
        query = query.join(Inference).join(Image).filter(Image.uploaded_by_id == user.id)
    return query.order_by(Incident.created_at.desc()).all()


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "operador")),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    incident.status = payload.status
    if payload.description is not None:
        incident.description = payload.description
    if payload.status == "cerrada":
        incident.closed_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident
