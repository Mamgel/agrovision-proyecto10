# AgroVision: Sistema inteligente para agricultura. Monitoreo y detección de enfermedades foliares

**Autor:** Miguel Ángel Mosquera González
**Curso:** Proyecto final de la asignatura
**Proyecto elegido:** Proyecto 10 (Computer Vision aplicado a agricultura)
**Fecha:** 23 de noviembre de 2026

---

## 1. Introducción y justificación

La producción agrícola, especialmente en viveros y cultivos intensivos, depende en gran medida del estado sanitario de las hojas. La foliación es el principal órgano fotosintético y cualquier daño foliar reduce la capacidad productiva. Las manchas foliares, causadas por hongos, bacterias o virus, son una de las enfermedades más comunes, y su detección tardía incrementa pérdidas económicas y el uso ineficiente de recursos como agua y agroquímicos.

En muchas explotaciones, la evaluación del estado de las hojas se realiza de forma manual mediante inspección visual del personal técnico. Este procedimiento es subjetivo, lento y difícil de escalar.

AgroVision aborda esta problemática con un sistema de software integral que, además de incorporar un modelo de visión por computador para clasificar visualmente el estado foliar, ofrece gestión de fincas, lotes y cultivos, trazabilidad de las inferencias, revisión experta y un panel de incidencias. El sistema reutiliza y amplía el trabajo previo realizado en la asignatura de Procesamiento Digital de Imágenes, donde se entrenó un modelo YOLOv8l-seg sobre un dataset propio etiquetado en Roboflow.

## 2. Objetivos

**Objetivo general.** Desarrollar un producto de software integral que integre un componente de visión por computador para el monitoreo y la detección temprana de enfermedades foliares en cultivos, con trazabilidad completa, revisión experta y despliegue reproducible.

**Objetivos específicos.**

1. Construir un backend con FastAPI que exponga una API REST para gestionar fincas, lotes, cultivos, imágenes, inferencias e incidencias.
2. Implementar un frontend web con Gradio que permita a tres tipos de usuarios (usuario, operador, administrador) operar el sistema.
3. Integrar un servicio de IA desacoplado basado en el modelo YOLOv8l-seg entrenado previamente, manteniendo trazabilidad de la versión del modelo en cada inferencia.
4. Persistir todos los datos en una base relacional con un modelo de dominio claro y migraciones controladas.
5. Entregar pruebas automatizadas, despliegue con Docker y documentación completa que cumpla la rúbrica académica.

## 3. Alcance y actores

**Dentro del alcance.** Clasificación de hojas en tres categorías (sana, mancha, seca), gestión jerárquica de fincas, lotes y cultivos, carga y procesamiento de imágenes individuales, panel de incidencias con revisión experta, autenticación con roles.

**Fuera del alcance.** Procesamiento de video en tiempo real por parte del backend, aplicación móvil nativa, detección de otras enfermedades no incluidas en el dataset original, integración con sensores IoT de campo.

**Actores.**

- **Usuario final:** gestiona sus propias fincas, carga fotos y consulta resultados.
- **Operador agronómico:** además revisa inferencias, deja notas de experto y cierra incidencias.
- **Administrador:** acceso total, gestión de usuarios.

## 4. Requisitos

El backlog con 10 historias de usuario, criterios de aceptación y trazabilidad hacia la implementación y las pruebas se encuentra en `docs/backlog.md`. La matriz de trazabilidad conecta cada requisito con el endpoint que lo implementa y las pruebas automatizadas que lo validan.

**Requisitos no funcionales.**

- Autenticación JWT con expiración configurable.
- Validación de entrada en todos los endpoints (Pydantic).
- Manejo explícito de errores con códigos HTTP correctos.
- Pruebas automatizadas con pytest (unidades, integración, API).
- Documentación interactiva de API en `/docs` (OpenAPI/Swagger).
- Despliegue reproducible con Docker.
- Variables sensibles externalizadas en `.env`.

## 5. Arquitectura

El sistema se compone de cuatro capas claramente separadas que se comunican a través de interfaces explícitas. El frontend Gradio consume la API REST del backend FastAPI por HTTP; el backend delega la inferencia al servicio de IA mediante una función interna; la persistencia se hace con SQLAlchemy sobre PostgreSQL en producción y SQLite en desarrollo.

Los diagramas detallados se encuentran en `docs/diagrams/`:

- `context.md`: diagrama C4 de contexto.
- `components.md`: diagrama de componentes internos.
- `data_model.md`: modelo entidad-relación de las siete tablas.
- `sequence.md`: secuencia del caso principal (análisis de imagen).
- `ai_pipeline.md`: pipeline del componente de IA.

Decisiones arquitectónicas clave:

1. **Desacoplamiento del servicio de IA.** Permite sustituir el modelo sin modificar el backend ni el frontend.
2. **ORM relacional en lugar de ODM documental.** La trazabilidad jerárquica (finca → lote → cultivo → imagen → inferencia → incidencia) encaja naturalmente en un modelo relacional.
3. **Un solo proceso que levanta API y UI.** Simplifica el despliegue académico sin perder la posibilidad de separarlos en producción.

## 6. Componente de IA

### 6.1 Reutilización del trabajo previo

El componente de IA se basa en el modelo YOLOv8l-seg entrenado previamente en la asignatura de Procesamiento Digital de Imágenes. Esta decisión es deliberada por tres razones:

1. **Validación empírica previa.** El modelo ya fue entrenado, evaluado y documentado con un informe formal y una matriz de confusión analizada por clase.
2. **Compatibilidad total.** Las tres clases (sana, mancha, seca) y el tamaño de entrada (640×640) se mantienen idénticos.
3. **Enfoque del proyecto 10 en el producto de software.** La rúbrica pide un sistema integral, no un modelo nuevo; aprovechar un modelo ya validado libera tiempo para la calidad del software.

### 6.2 Dataset y entrenamiento

- **Dataset propio:** 350 imágenes capturadas con cámara de teléfono móvil y etiquetadas en Roboflow con la herramienta Smart Polygon para segmentación por instancias.
- **Tres clases:** 0=sana, 1=mancha, 2=seca.
- **Augmentations (solo en entrenamiento):** Flip horizontal y vertical, rotación ±15°, cambio de brillo ±20%.
- **Partición final:** 732 train (87.35%), 71 val (8.47%), 35 test (4.18%).
- **Preprocesamiento:** conversión BGR → LAB, ecualización del canal L, retorno a BGR, resize a 640×640 con padding.
- **Modelo:** YOLOv8l-seg (45.9 M parámetros, 210 GFLOPs).
- **Entrenamiento:** Google Colab, NVIDIA Tesla T4 (16 GB), 50 épocas, AdamW, batch default, 0.85 horas totales.

### 6.3 Métricas del modelo

| Métrica | Boxes | Mask |
|---|---|---|
| Precisión | 0.780 | 0.821 |
| Recall | 0.740 | 0.711 |
| mAP50 | 0.802 | 0.801 |
| mAP50-95 | 0.685 | **0.686** |

Por clase (Mask):

| Clase | Precisión | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| Mancha | 0.865 | 0.716 | 0.820 | 0.700 |
| Sana | 0.716 | 0.498 | 0.622 | 0.481 |
| Seca | 0.883 | 0.918 | 0.961 | 0.877 |

Tiempos en GPU T4: inferencia 21.2 ms/imagen, preprocesamiento 0.3 ms/imagen.

### 6.4 Análisis de errores

El informe original identificó cuatro familias de errores principales:

1. **Confusión entre hoja sana y hoja con manchas** por variaciones cromáticas leves y sombras parciales.
2. **Falsos positivos en el fondo** cuando el fondo tiene tonos verdes similares a las hojas.
3. **Fallos en hojas parcialmente visibles** por anotaciones ambiguas.
4. **Segmentación defectuosa bajo sombras intensas.**

Estos hallazgos se incorporan al sistema AgroVision con dos medidas concretas:

- **Revisión experta obligatoria** antes de cerrar una incidencia.
- **Confianza media y detecciones crudas disponibles** en la respuesta de la API para que el experto pueda juzgar.

### 6.5 Baseline y comparación

Como baseline simple se usa una heurística basada en el canal HSV (proporción de píxeles verdes), implementada en el modo simulado del clasificador cuando no hay modelo cargado (`ai_service/inference.py::_simulated_result`). La comparación es cualitativa: el baseline solo distingue presencia global de follaje; el modelo entrenado distingue instancias individuales y las clasifica. Esta diferencia justifica el uso del modelo profundo.

### 6.6 Integración en el sistema

El servicio `LeafClassifier` se carga como singleton al arrancar el backend y expone un único método: `predict(image_path)`. El endpoint `POST /images/{id}/analyze` recibe la imagen, llama al servicio, interpreta los conteos por clase y genera una incidencia automática si el porcentaje de hojas afectadas supera los umbrales definidos (baja: 0-25%, media: 25-50%, alta: > 50%).

La respuesta incluye la versión exacta del modelo (`model_version`) para trazabilidad, de forma que si en el futuro se sustituye el modelo, cada inferencia histórica queda vinculada a la versión con la que fue hecha.

## 7. Implementación del software

### 7.1 Backend

Desarrollado con FastAPI y SQLAlchemy. Siete routers: `auth`, `farms`, `lots`, `crops`, `images`, `inferences`, `incidents`. Autenticación JWT con python-jose, hashing de contraseñas con bcrypt (passlib). Control de acceso basado en roles con dependencias (`require_role`).

Endpoints principales:

- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `POST/GET/DELETE /farms`, `POST/GET /lots`
- `POST/GET /crops`
- `POST /images`, `POST /images/{id}/analyze`, `GET /images`
- `GET /inferences`, `PATCH /inferences/{id}/review`
- `POST/GET/PATCH /incidents`
- `GET /health`

### 7.2 Frontend

Gradio con pestañas para cada caso de uso. Un cliente HTTP ligero (`ApiClient` basado en httpx) maneja el token JWT y las llamadas a la API.

### 7.3 Persistencia

SQLAlchemy ORM con 7 tablas (ver `docs/diagrams/data_model.md`). SQLite para desarrollo (`sqlite:///./agrovision.db`), PostgreSQL 16 para producción vía Docker. Las migraciones se gestionan con `Base.metadata.create_all` para simplificar; en un proyecto más grande se usaría Alembic.

## 8. Pruebas

Suite pytest en `tests/`:

- `test_auth.py`: 6 pruebas de registro, login, token, roles.
- `test_farms.py`: 3 pruebas de CRUD y control de acceso.
- `test_images.py`: 3 pruebas de carga y análisis.
- `test_ai_service.py`: 4 pruebas de preprocesamiento y clasificador (incluyendo modo simulado).

Total: 16 pruebas. Se ejecutan en CI (GitHub Actions) en cada push.

## 9. DevOps y despliegue

- `Dockerfile` basado en `python:3.11-slim` con las dependencias del sistema para OpenCV.
- `docker-compose.yml` con dos servicios: PostgreSQL y la aplicación.
- `.env.example` con todas las variables necesarias y valores por defecto para desarrollo.
- `.github/workflows/ci.yml` corre las pruebas en cada push y pull request.
- `.gitignore` excluye `data/uploads/`, `*.pt`, `.env`, bases SQLite.

## 10. Evaluación global

### Cumplimiento de la rúbrica

| Criterio | Peso | Cumplimiento |
|---|---|---|
| Requisitos y análisis | 15% | 10 historias con criterios de aceptación y trazabilidad explícita |
| Arquitectura y diseño | 15% | 5 diagramas Mermaid, decisiones documentadas |
| Implementación software | 20% | Backend + frontend + persistencia funcional, 7 routers, 7 tablas |
| Componente de IA | 20% | Modelo YOLOv8l-seg entrenado con métricas reales (mAP50-95 ≈ 0.686), servicio desacoplado |
| Pruebas y calidad | 15% | 16 pruebas pytest cubriendo auth, CRUD, IA, roles |
| DevOps, seguridad, reproducibilidad | 10% | Docker, docker-compose, CI, JWT, roles, .env |
| Documentación y sustentación | 5% | README, informe, manual, diagramas, backlog |

### Trazabilidad extremo a extremo

El flujo principal (usuario sube imagen → se analiza → se genera incidencia → se revisa y cierra) está cubierto por:

- Historias HU-06, HU-07 y HU-10.
- Endpoints `/images`, `/images/{id}/analyze`, `/incidents`.
- Pruebas `test_images.py::test_upload_and_analyze_without_model` y `test_ai_service.py::test_classifier_simulated`.
- Diagrama de secuencia en `docs/diagrams/sequence.md`.
- Manual de usuario sección 3.

## 11. Riesgos

Análisis completo en `docs/risks.md`. Los riesgos más críticos tienen que ver con la precisión del modelo (falsos positivos en hojas sanas y fondos verdes) y la privacidad de las imágenes cargadas. Se mitigan con revisión experta obligatoria, filtros HSV post-inferencia (línea de trabajo futuro) y almacenamiento local sin publicación externa.

## 12. Trabajo futuro

Las líneas de mejora identificadas en el informe PDI original se mantienen vigentes:

1. **Depuración del dataset** mediante limpieza del fondo y separación entre foco principal y contexto secundario.
2. **Ampliación y balanceo del dataset** con mayor variabilidad cromática, de especies y de condiciones lumínicas.
3. **Imágenes con fondo neutro** como complemento para distinguir mejor las propiedades intrínsecas de cada clase.

En lo que respecta al producto de software, las líneas inmediatas son:

- Migraciones gestionadas con Alembic en lugar de `create_all`.
- Cola de inferencias asíncrona (Celery + Redis) para evitar bloqueos en picos de uso.
- Métricas de observabilidad (Prometheus + Grafana) para monitorear tiempos de inferencia en producción.
- Aplicación móvil que consuma la misma API REST y permita captura in situ.

## 13. Declaración de uso de IA generativa

Para la aceleración del desarrollo de este proyecto se usó un asistente de IA generativa en las siguientes tareas:

- Generación inicial del código base (backend FastAPI, routers, modelos SQLAlchemy, frontend Gradio) a partir de la especificación del Proyecto 10 y del informe PDI previo.
- Redacción inicial de documentos (README, manual de usuario, backlog, diagramas Mermaid).
- Generación inicial de pruebas unitarias e integración.

El autor revisó, ajustó y validó cada archivo, es responsable del código entregado y del contenido técnico del informe. El modelo entrenado y el informe original del proyecto PDI son trabajo propio y de su equipo original, debidamente citado.

## 14. Conclusiones

AgroVision demuestra que es posible convertir un modelo de computer vision validado académicamente en un producto de software integral en tiempo acotado, siempre que se disponga de un trabajo previo bien documentado. La arquitectura desacoplada permite sustituir el modelo sin tocar el resto del sistema, lo cual deja abierta la posibilidad de mejoras futuras sobre el componente IA mientras el producto sigue operando.

El principal aporte del proyecto es la incorporación de trazabilidad (versión del modelo en cada inferencia, historial por usuario, revisión experta obligatoria para cerrar incidencias) y de una capa de software que respeta los criterios académicos de modularidad, reproducibilidad y calidad.

## 15. Referencias

Las referencias técnicas del modelo YOLOv8l-seg, del dataset Roboflow, del preprocesamiento en LAB y de las métricas mAP/IoU se encuentran en el informe original del proyecto PDI (`Informe_Final_PDI.pdf`, bibliografía 1-16). A esas se suman las siguientes referencias técnicas usadas en la construcción del sistema:

- FastAPI. Documentación oficial. https://fastapi.tiangolo.com
- SQLAlchemy 2.0. Documentación oficial. https://docs.sqlalchemy.org
- Gradio. Documentación oficial. https://www.gradio.app/docs
- Docker Compose. Documentación oficial. https://docs.docker.com/compose/
- JWT (JSON Web Tokens) RFC 7519. https://datatracker.ietf.org/doc/html/rfc7519
