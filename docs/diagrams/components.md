# Diagrama de componentes

```mermaid
flowchart TB
    subgraph Frontend
        G[Gradio App<br/>frontend/gradio_app.py]
        C[ApiClient httpx]
    end

    subgraph Backend FastAPI
        R1[Router auth]
        R2[Router farms + lots]
        R3[Router crops]
        R4[Router images]
        R5[Router inferences]
        R6[Router incidents]
        AU[Auth JWT<br/>backend/auth.py]
        DB[SQLAlchemy ORM<br/>backend/models.py]
    end

    subgraph AI Service
        PP[Preprocessing<br/>ai_service/preprocessing.py]
        INF[LeafClassifier<br/>ai_service/inference.py]
        W[YOLOv8l-seg<br/>best.pt]
    end

    subgraph Persistencia
        DB1[(PostgreSQL / SQLite)]
        FS[(Filesystem<br/>data/uploads)]
    end

    G --> C
    C -->|HTTP REST| R1
    C --> R2
    C --> R3
    C --> R4
    C --> R5
    C --> R6

    R1 --> AU
    R2 --> DB
    R3 --> DB
    R4 --> DB
    R4 --> FS
    R4 --> PP
    PP --> INF
    INF --> W
    DB --> DB1
    R5 --> DB
    R6 --> DB
```

## Notas de diseño

- La capa de IA está desacoplada del resto de la lógica de negocio: el endpoint de análisis solo conoce la interfaz `LeafClassifier.predict()`. Esto permite sustituir el modelo (por ejemplo, migrar a YOLOv11 o Mask R-CNN) sin tocar el backend ni el frontend.
- La capa de persistencia usa SQLAlchemy, lo que permite cambiar de SQLite (desarrollo) a PostgreSQL (producción) con solo cambiar `DATABASE_URL` en el `.env`.
- La autenticación se hace con JWT (python-jose) y las contraseñas se guardan hasheadas con bcrypt (passlib).
