"""Esquemas Pydantic para validacion de entrada/salida."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="usuario", pattern="^(admin|operador|usuario)$")


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


# ---------- Farm ----------
class FarmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = None
    area_ha: Optional[float] = Field(None, gt=0)


class FarmOut(FarmCreate):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Lot ----------
class LotCreate(BaseModel):
    farm_id: int
    name: str = Field(..., min_length=1, max_length=100)
    area_m2: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None


class LotOut(LotCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Crop ----------
class CropCreate(BaseModel):
    lot_id: int
    species: str = Field(..., min_length=1, max_length=100)
    variety: Optional[str] = None
    planting_date: Optional[datetime] = None


class CropOut(CropCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Image ----------
class ImageOut(BaseModel):
    id: int
    crop_id: Optional[int]
    file_path: str
    original_filename: str
    uploaded_by_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ---------- Inference ----------
class InferenceOut(BaseModel):
    id: int
    image_id: int
    model_version: str
    n_leaves_detected: int
    n_sana: int
    n_mancha: int
    n_seca: int
    avg_confidence: float
    inference_time_ms: float
    annotated_path: Optional[str]
    expert_reviewed: bool
    expert_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ExpertReviewRequest(BaseModel):
    expert_reviewed: bool
    expert_notes: Optional[str] = None


# ---------- Incident ----------
class IncidentCreate(BaseModel):
    inference_id: int
    severity: str = Field(..., pattern="^(baja|media|alta)$")
    description: Optional[str] = None


class IncidentUpdate(BaseModel):
    status: str = Field(..., pattern="^(abierta|en_revision|cerrada)$")
    description: Optional[str] = None


class IncidentOut(BaseModel):
    id: int
    inference_id: int
    severity: str
    status: str
    description: Optional[str]
    created_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- Health ----------
class HealthOut(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    env: str
