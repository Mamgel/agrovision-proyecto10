"""Servicio de inferencia que envuelve el modelo YOLOv8l-seg entrenado."""
import time
import uuid
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from backend.config import settings
from ai_service.preprocessing import preprocess

# Clases exactamente como fueron etiquetadas en Roboflow para el proyecto PDI
CLASES = {0: "sana", 1: "mancha", 2: "seca"}


class LeafClassifier:
    """Wrapper del modelo YOLOv8l-seg entrenado en el proyecto PDI."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.model_version = "none"
        self.is_loaded = False
        self._load()

    def _load(self) -> None:
        if not Path(self.model_path).exists():
            # El modelo aun no esta disponible: inferencia simulada
            self.model_version = "not_loaded"
            return
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            self.model_version = f"yolov8l-seg:{Path(self.model_path).stem}"
            self.is_loaded = True
        except Exception as exc:  # noqa: BLE001
            print(f"[AI] No se pudo cargar el modelo: {exc}")
            self.model_version = f"load_error:{type(exc).__name__}"

    def predict(self, image_path: str, conf: Optional[float] = None) -> dict:
        """Ejecuta inferencia sobre una imagen y retorna metricas estructuradas."""
        conf = conf if conf is not None else settings.confidence_threshold
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise ValueError(f"No se pudo leer la imagen: {image_path}")

        img_pre = preprocess(img_bgr)
        if not self.is_loaded or self.model is None:
            return self._simulated_result(img_bgr, image_path)

        t0 = time.perf_counter()
        results = self.model.predict(img_pre, conf=conf, verbose=False)
        dt_ms = (time.perf_counter() - t0) * 1000.0

        res = results[0]
        counts = {0: 0, 1: 0, 2: 0}
        confidences = []
        detections = []
        if res.boxes is not None and len(res.boxes) > 0:
            for i, box in enumerate(res.boxes):
                cls = int(box.cls.item())
                c = float(box.conf.item())
                counts[cls] = counts.get(cls, 0) + 1
                confidences.append(c)
                xyxy = box.xyxy[0].tolist()
                detections.append({
                    "class_id": cls,
                    "class_name": CLASES.get(cls, "desconocido"),
                    "confidence": round(c, 4),
                    "bbox": [round(x, 2) for x in xyxy],
                })

        annotated_path = self._save_annotated(res, image_path)

        return {
            "model_version": self.model_version,
            "n_leaves_detected": sum(counts.values()),
            "n_sana": counts.get(0, 0),
            "n_mancha": counts.get(1, 0),
            "n_seca": counts.get(2, 0),
            "avg_confidence": round(float(np.mean(confidences)) if confidences else 0.0, 4),
            "inference_time_ms": round(dt_ms, 2),
            "annotated_path": annotated_path,
            "detections": detections,
        }

    def _save_annotated(self, res, original_path: str) -> str:
        """Guarda la imagen anotada con las mascaras superpuestas."""
        try:
            annotated = res.plot()
            out_name = f"annot_{uuid.uuid4().hex}.jpg"
            out_dir = Path(settings.upload_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / out_name
            cv2.imwrite(str(out_path), annotated)
            return str(out_path)
        except Exception:
            return ""

    def _simulated_result(self, img_bgr: np.ndarray, image_path: str) -> dict:
        """Resultado simulado cuando no hay modelo cargado.

        Util para desarrollo y para que la API responda sin bloquearse.
        Las metricas se marcan con el prefijo 'simulated' en model_version.
        """
        h, w = img_bgr.shape[:2]
        # Heuristica trivial basada en canal verde para no retornar ceros
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        green_ratio = float(((hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 85)).mean())
        n_total = max(1, int(green_ratio * 5))
        return {
            "model_version": f"simulated:{self.model_version}",
            "n_leaves_detected": n_total,
            "n_sana": max(0, n_total - 1),
            "n_mancha": 1 if green_ratio < 0.3 else 0,
            "n_seca": 0,
            "avg_confidence": 0.5,
            "inference_time_ms": 5.0,
            "annotated_path": "",
            "detections": [],
        }


_classifier: Optional[LeafClassifier] = None


def get_classifier(raise_if_missing: bool = False) -> LeafClassifier:
    """Singleton del clasificador para no recargar el modelo en cada request."""
    global _classifier
    if _classifier is None:
        _classifier = LeafClassifier(settings.model_path)
        if raise_if_missing and not _classifier.is_loaded:
            raise RuntimeError(f"Modelo no cargado en {settings.model_path}")
    return _classifier
