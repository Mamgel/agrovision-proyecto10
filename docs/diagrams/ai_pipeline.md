# Pipeline del componente de IA

```mermaid
flowchart LR
    I[Imagen BGR<br/>cualquier tamaño] --> EQ[Ecualización canal L en LAB<br/>cv2.equalizeHist]
    EQ --> RS[Resize con padding<br/>640 x 640]
    RS --> M[YOLOv8l-seg<br/>Ultralytics]
    M --> P[Post-proceso<br/>NMS interno]
    P --> C{Conteo por clase<br/>0 sana, 1 mancha, 2 seca}
    C --> OUT[Resultado estructurado]
    M --> A[Imagen anotada<br/>res.plot()]

    OUT --> DB[(INSERT inferences)]
    A --> FS[(data/uploads)]
```

## Detalle del modelo

- **Modelo:** YOLOv8l-seg (variante large de la familia YOLOv8 para segmentación por instancias)
- **Entrenamiento:** 50 épocas, batch size default, optimizador AdamW, learning rate adaptativo (Ultralytics)
- **Hardware de entrenamiento:** Google Colab con NVIDIA Tesla T4 (16 GB)
- **Dataset:** 350 imágenes propias + augmentations (Roboflow), total 838 imágenes
  - Train: 732 (87.35%)
  - Val: 71 (8.47%)
  - Test: 35 (4.18%)
- **Clases:** 0=sana, 1=mancha, 2=seca
- **Resolución de entrada:** 640×640 px
- **Métricas:** mAP50 ≈ 0.80 (máscara), mAP50-95 ≈ 0.686 (máscara)
- **Tiempo de inferencia:** 21.2 ms por imagen en GPU T4, 0.3 ms de preprocesamiento
- **Pérdidas:** Box loss, Class loss, DFL loss, Mask loss (todas convergieron sin divergencia)

## Decisiones clave de diseño

1. **Segmentación por instancias en lugar de clasificación simple.** Permite medir propiedades por hoja (área, porcentaje afectado) en lugar de solo detectar presencia global.
2. **Ecualización del canal L en LAB.** Separa luminancia de color para que la ecualización no altere el matiz verde característico del follaje.
3. **640×640 como tamaño de entrada.** Balance recomendado por Ultralytics entre precisión y velocidad; suficiente para lesiones foliares típicas.
4. **Augmentations solo en entrenamiento.** Flip horizontal/vertical, rotación ±15°, cambio de brillo ±20%. Validación y test se mantienen sin transformar.
5. **Modelo desacoplado del backend.** El servicio `LeafClassifier` tiene una interfaz simple (`predict(path)`) que el backend consume. Sustituir el modelo requiere reemplazar un archivo.
