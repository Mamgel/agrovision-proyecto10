"""Endpoints de gestion de cultivos."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.models import Crop, Farm, Lot, User
from backend.schemas import CropCreate, CropOut

router = APIRouter(prefix="/crops", tags=["crops"])


@router.post("", response_model=CropOut, status_code=status.HTTP_201_CREATED)
def create_crop(
    payload: CropCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "operador")),
):
    lot = db.query(Lot).filter(Lot.id == payload.lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    if user.role != "admin" and lot.farm.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre el lote")
    crop = Crop(**payload.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router.get("", response_model=list[CropOut])
def list_crops(
    lot_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Crop)
    if lot_id is not None:
        query = query.filter(Crop.lot_id == lot_id)
    if user.role != "admin":
        query = query.join(Lot).join(Farm).filter(Farm.owner_id == user.id)
    return query.all()


@router.get("/{crop_id}", response_model=CropOut)
def get_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    if user.role != "admin" and crop.lot.farm.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return crop
