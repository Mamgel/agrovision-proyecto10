"""Pruebas del componente de IA y del preprocesamiento."""
import numpy as np

from ai_service.preprocessing import equalize_luminance, resize_keeping_aspect, preprocess


def test_equalize_returns_same_shape():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    out = equalize_luminance(img)
    assert out.shape == img.shape
    assert out.dtype == np.uint8


def test_resize_target():
    img = np.random.randint(0, 255, (300, 500, 3), dtype=np.uint8)
    out = resize_keeping_aspect(img, target=640)
    assert out.shape == (640, 640, 3)


def test_preprocess_pipeline():
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    out = preprocess(img, target=640)
    assert out.shape == (640, 640, 3)


def test_classifier_simulated(tmp_path):
    """Si no hay modelo, el clasificador debe retornar una respuesta simulada."""
    import cv2
    from ai_service.inference import LeafClassifier

    clf = LeafClassifier(model_path=str(tmp_path / "no_existe.pt"))
    assert not clf.is_loaded

    img = np.full((200, 200, 3), 100, dtype=np.uint8)
    p = str(tmp_path / "x.jpg")
    cv2.imwrite(p, img)
    result = clf.predict(p)

    assert "model_version" in result
    assert result["n_leaves_detected"] >= 0
    assert "inference_time_ms" in result
