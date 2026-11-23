"""Modelo de dominio: tablas de la base de datos."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    """Usuarios del sistema. Roles: admin, operador, usuario."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="usuario")  # admin | operador | usuario
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farms = relationship("Farm", back_populates="owner", cascade="all, delete")
    images = relationship("Image", back_populates="uploaded_by")


class Farm(Base):
    """Finca o unidad productiva."""
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=True)
    area_ha = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="farms")
    lots = relationship("Lot", back_populates="farm", cascade="all, delete")


class Lot(Base):
    """Lote dentro de una finca."""
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    name = Column(String(100), nullable=False)
    area_m2 = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="lots")
    crops = relationship("Crop", back_populates="lot", cascade="all, delete")


class Crop(Base):
    """Cultivo sembrado en un lote."""
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    species = Column(String(100), nullable=False)
    variety = Column(String(100), nullable=True)
    planting_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lot = relationship("Lot", back_populates="crops")
    images = relationship("Image", back_populates="crop", cascade="all, delete")


class Image(Base):
    """Imagen cargada para analisis."""
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    crop = relationship("Crop", back_populates="images")
    uploaded_by = relationship("User", back_populates="images")
    inferences = relationship("Inference", back_populates="image", cascade="all, delete")


class Inference(Base):
    """Resultado de una inferencia del modelo IA sobre una imagen."""
    __tablename__ = "inferences"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    model_version = Column(String(50), nullable=False)
    n_leaves_detected = Column(Integer, default=0)
    n_sana = Column(Integer, default=0)
    n_mancha = Column(Integer, default=0)
    n_seca = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    inference_time_ms = Column(Float, default=0.0)
    annotated_path = Column(String(500), nullable=True)
    raw_detections_json = Column(Text, nullable=True)
    expert_reviewed = Column(Boolean, default=False)
    expert_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("Image", back_populates="inferences")
    incidents = relationship("Incident", back_populates="inference", cascade="all, delete")


class Incident(Base):
    """Incidencia detectada que requiere atencion (mancha o seca)."""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    inference_id = Column(Integer, ForeignKey("inferences.id"), nullable=False)
    severity = Column(String(20), nullable=False)  # baja | media | alta
    status = Column(String(20), nullable=False, default="abierta")  # abierta | en_revision | cerrada
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    inference = relationship("Inference", back_populates="incidents")
