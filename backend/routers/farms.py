"""Endpoints CRUD de fincas y lotes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.models import Farm, Lot, User
from backend.schemas import FarmCreate, FarmOut, LotCreate, LotOut

router = APIRouter(prefix="/farms", tags=["farms"])


@router.post("", response_model=FarmOut, status_code=status.HTTP_201_CREATED)
def create_farm(
    payload: FarmCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "operador")),
):
    farm = Farm(**payload.model_dump(), owner_id=user.id)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("", response_model=list[FarmOut])
def list_farms(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role == "admin":
        return db.query(Farm).all()
    return db.query(Farm).filter(Farm.owner_id == user.id).all()


@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if user.role != "admin" and farm.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Sin acceso a esta finca")
    return farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "operador")),
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if user.role != "admin" and farm.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    db.delete(farm)
    db.commit()


# ---------- Lotes anidados ----------
lots_router = APIRouter(prefix="/lots", tags=["lots"])


@lots_router.post("", response_model=LotOut, status_code=status.HTTP_201_CREATED)
def create_lot(
    payload: LotCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "operador")),
):
    farm = db.query(Farm).filter(Farm.id == payload.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if user.role != "admin" and farm.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre la finca")
    lot = Lot(**payload.model_dump())
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@lots_router.get("", response_model=list[LotOut])
def list_lots(
    farm_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Lot)
    if farm_id is not None:
        query = query.filter(Lot.farm_id == farm_id)
    if user.role != "admin":
        query = query.join(Farm).filter(Farm.owner_id == user.id)
    return query.all()
