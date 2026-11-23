# AgroVision

Sistema inteligente para agricultura: monitoreo y detección de enfermedades foliares.

**Autor:** Miguel Ángel Mosquera González
**Curso:** Proyecto final, Proyecto 10
**Enfoque:** Computer Vision (segmentación por instancias con YOLOv8l-seg)

AgroVision es un producto de software integral que permite a productores y técnicos de viveros gestionar sus fincas, lotes y cultivos, cargar imágenes de hojas y obtener de forma automática la clasificación visual de su estado sanitario (sana, mancha foliar, seca), manteniendo trazabilidad, historial y un panel de incidencias con revisión experta.

El componente de inteligencia artificial reutiliza el modelo YOLOv8l-seg entrenado en un proyecto previo de la asignatura Procesamiento Digital de Imágenes, con un `mAP50-95 ≈ 0.686` sobre validación.

---

## Características principales

- Gestión de fincas, lotes y cultivos con roles (admin, operador, usuario).
- Carga de imágenes y disparo del clasificador visual (segmentación por instancias).
- Historial de inferencias con marca de revisión por experto.
- Panel de incidencias con severidad calculada automáticamente y ciclo de vida (abierta → en revisión → cerrada).
- API REST documentada (OpenAPI/Swagger en `/docs`).
- Frontend web con Gradio.
- Pruebas automatizadas con pytest.
- Despliegue reproducible con Docker + docker-compose.

---

## Estructura del repositorio

```
agrovision/
├── backend/            FastAPI (routers, modelos, auth, schemas)
├── ai_service/         Modelo YOLOv8l-seg y preprocesamiento
│   ├── models/         best.pt (no versionado por tamaño)
│   ├── notebooks/      Entrenamiento original
│   └── src/            Código de inferencia
├── frontend/           Cliente Gradio
├── tests/              pytest (auth, farms, images, ai_service)
├── docs/               Documentación: diagramas, backlog, riesgos, informe
├── data/               Imágenes y uploads (ignorado)
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── run.py              Lanzador (API + Gradio)
└── README.md
```

---

## Instalación rápida (modo desarrollo, sin Docker)

### 1. Clonar y preparar entorno

```powershell
git clone <repo>
cd agrovision

python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
cp .env.example .env         # copiar y editar si hace falta
```

### 2. Colocar el modelo entrenado

Copia el archivo `best.pt` (pesos del modelo YOLOv8l-seg entrenado en el proyecto PDI) en:

```
ai_service/models/best.pt
```

Si no está, la API sigue funcionando en modo simulado y los tests siguen pasando, pero las métricas no son reales.

### 3. Lanzar la aplicación

```powershell
python run.py
```

Se abren dos servicios:

- API FastAPI: http://127.0.0.1:8000 (docs en `/docs`)
- Frontend Gradio: http://127.0.0.1:7860

También se pueden lanzar por separado:

```powershell
python run.py api         # solo API
python run.py frontend    # solo Gradio
```

---

## Despliegue con Docker

```bash
docker compose up --build
```

Sirve PostgreSQL (puerto 5432), la API (8000) y Gradio (7860). El modelo y los uploads se montan desde el host.

---

## Uso básico

1. Abre http://127.0.0.1:7860.
2. Pestaña **Registrarse**: crea un usuario (si quieres probar roles, repite con `admin` y `operador`).
3. Pestaña **Ingresar**: inicia sesión.
4. Pestaña **Fincas → Lotes → Cultivos**: crea la jerarquía en ese orden.
5. Pestaña **Análisis de imagen**: sube una foto de hoja, opcionalmente asociada a un cultivo. Se guarda la imagen, se ejecuta el modelo y se genera automáticamente una incidencia si el porcentaje de hojas con manchas o secas supera cierto umbral.
6. Pestaña **Historial**: revisa las inferencias y márcalas como validadas por experto.
7. Pestaña **Incidencias**: filtra por estado y severidad, cambia el ciclo de vida.

La documentación interactiva de la API está en http://127.0.0.1:8000/docs.

---

## Pruebas

```powershell
pytest -q
```

Cubre: autenticación, control de acceso por roles, CRUD de fincas y lotes, carga de imágenes, inferencia (modo simulado y con modelo), preprocesamiento.

---

## Variables de entorno (.env)

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Cadena de conexión. SQLite por defecto, Postgres en Docker |
| `SECRET_KEY` | Secreto JWT |
| `MODEL_PATH` | Ruta al `best.pt` |
| `CONFIDENCE_THRESHOLD` | Umbral mínimo de confianza para la detección |
| `UPLOAD_DIR` | Carpeta donde se guardan las imágenes |
| `API_PORT`, `GRADIO_PORT` | Puertos |

---

## Reproducibilidad del modelo

El modelo YOLOv8l-seg fue entrenado en Google Colab con GPU NVIDIA Tesla T4, usando un dataset propio versionado en Roboflow (838 imágenes tras augmentations, 732 train / 71 val / 35 test, tres clases: sana, mancha, seca). El notebook de entrenamiento está en `ai_service/notebooks/` y el `data.yaml` en el repositorio de Roboflow correspondiente. Detalles en `docs/Informe_Final.md`.

---

## Documentación adicional

- `docs/Informe_Final.md`: informe final del proyecto.
- `docs/backlog.md`: historias de usuario y criterios de aceptación.
- `docs/diagrams/`: diagramas de contexto, componentes, modelo de datos, secuencia y pipeline IA.
- `docs/risks.md`: análisis de riesgos.
- `docs/user_manual.md`: manual de usuario.
