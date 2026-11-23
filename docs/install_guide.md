# Guía de instalación

## Requisitos previos

- Python 3.11 o superior
- Git
- (Opcional) Docker Desktop si se va a correr con `docker compose`
- Al menos 4 GB de RAM libres para cargar YOLOv8l-seg

## Opción A: instalación local

```powershell
git clone <repo>
cd agrovision

python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Linux/Mac

pip install -U pip
pip install -r requirements.txt

copy .env.example .env         # Windows
# cp .env.example .env         # Linux/Mac
```

Coloca el modelo entrenado:

```powershell
# Copiar best.pt a ai_service/models/
copy ..\ruta\a\best.pt ai_service\models\best.pt
```

Lanza:

```powershell
python run.py
```

Abre:

- API: http://127.0.0.1:8000
- Docs OpenAPI: http://127.0.0.1:8000/docs
- UI Gradio: http://127.0.0.1:7860

## Opción B: con Docker

```bash
cp .env.example .env
docker compose up --build
```

Para detener:

```bash
docker compose down
```

Si quieres limpiar todo (incluyendo la base):

```bash
docker compose down -v
```

## Verificación

Ejecuta las pruebas:

```powershell
pytest -q
```

Debe terminar con todos los tests en verde.

Verifica el endpoint de salud:

```bash
curl http://127.0.0.1:8000/health
```

Respuesta esperada:

```json
{"status":"ok","model_loaded":true,"model_version":"yolov8l-seg:best","env":"development"}
```

Si `model_loaded` sale `false`, significa que `best.pt` no está en `ai_service/models/`.

## Resolución de problemas

**Error al instalar `opencv-contrib-python`.**
En Windows a veces falta el redistribuible de Visual C++. Instalar desde https://aka.ms/vs/17/release/vc_redist.x64.exe.

**Puerto 8000 ocupado.**
Cambia `API_PORT` en `.env` o libera el puerto.

**Error importando `ultralytics`.**
Verifica versión de Python (3.11 recomendado). Reinstala: `pip install --force-reinstall ultralytics==8.3.33`.

**`ModuleNotFoundError: No module named 'backend'`.**
Ejecuta siempre desde la raíz del proyecto (`python run.py`) y con el `.venv` activo.
