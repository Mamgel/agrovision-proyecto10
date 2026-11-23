"""Preprocesamiento clasico: RGB->HSV y ecualizacion del canal L en LAB.

Esta etapa se mantiene identica al pipeline del proyecto PDI original
para preservar la consistencia con el modelo entrenado.
"""
import cv2
import numpy as np


def equalize_luminance(image_bgr: np.ndarray) -> np.ndarray:
    """Convierte a LAB, ecualiza el canal L y regresa a BGR.

    Mejora el contraste global sin alterar el matiz. Es el preprocesado
    usado en el entrenamiento del modelo YOLOv8l-seg del proyecto PDI.
    """
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_eq = cv2.equalizeHist(l)
    lab_eq = cv2.merge((l_eq, a, b))
    return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)


def resize_keeping_aspect(image_bgr: np.ndarray, target: int = 640) -> np.ndarray:
    """Redimensiona a target x target con padding para mantener relacion de aspecto."""
    h, w = image_bgr.shape[:2]
    scale = target / max(h, w)
    nh, nw = int(h * scale), int(w * scale)
    resized = cv2.resize(image_bgr, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((target, target, 3), dtype=np.uint8)
    y0, x0 = (target - nh) // 2, (target - nw) // 2
    canvas[y0:y0 + nh, x0:x0 + nw] = resized
    return canvas


def preprocess(image_bgr: np.ndarray, target: int = 640) -> np.ndarray:
    """Pipeline completo: ecualizacion + redimensionado."""
    img = equalize_luminance(image_bgr)
    img = resize_keeping_aspect(img, target)
    return img
