"""Endpoints de consulta e historial de inferencias."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.models import Inference, Image, User
from backend.schemas import ExpertReviewRequest, InferenceOut

router = APIRouter(prefix="/inferences", tags=["inferences"])


@router.get("", response_model=list[InferenceOut])
def list_inferences(
    reviewed: bool | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Inference)
    if reviewed is not None:
        query = query.filter(Inference.expert_reviewed == reviewed)
    if user.role != "admin":
        query = query.join(Image).filter(Image.uploaded_by_id == user.id)
    return query.order_by(Inference.created_at.desc()).all()


@router.get("/{inf_id}", response_model=InferenceOut)
def get_inference(
    inf_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inf = db.query(Inference).filter(Inference.id == inf_id).first()
    if not inf:
        raise HTTPException(status_code=404, detail="Inferencia no encontrada")
    if user.role != "admin" and inf.image.uploaded_by_id != user.id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return inf


@router.patch("/{inf_id}/review", response_model=InferenceOut)
def review_inference(
    inf_id: int,
    payload: ExpertReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "operador")),
):
    """Marca una inferencia como revisada por experto."""
    inf = db.query(Inference).filter(Inference.id == inf_id).first()
    if not inf:
        raise HTTPException(status_code=404, detail="Inferencia no encontrada")
    inf.expert_reviewed = payload.expert_reviewed
    if payload.expert_notes is not None:
        inf.expert_notes = payload.expert_notes
    db.commit()
    db.refresh(inf)
    return inf
