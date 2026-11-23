# Backlog - Historias de usuario

Proyecto 10: AgroVision. Sistema inteligente para agricultura.

Cada historia tiene prioridad (A alta, B media, C baja), descripción, criterios de aceptación y notas de trazabilidad hacia la implementación y las pruebas.

---

## HU-01 (A) Registro de usuario

**Como** usuario nuevo
**quiero** registrarme con un nombre, correo y contraseña
**para** poder acceder al sistema con mi propia cuenta.

**Criterios de aceptación**
- El correo no puede repetirse.
- La contraseña tiene mínimo 6 caracteres.
- Al registrarme, se me asigna por defecto el rol `usuario`.
- Recibo confirmación en pantalla.

Implementación: `backend/routers/auth.py::register`
Prueba: `tests/test_auth.py::test_register_and_login`, `test_register_duplicate`

---

## HU-02 (A) Inicio de sesión con JWT

**Como** usuario registrado
**quiero** iniciar sesión con usuario y contraseña
**para** obtener un token que me permita usar la API y la interfaz.

**Criterios**
- Las credenciales incorrectas devuelven 401.
- El token expira a los 60 minutos por defecto.
- El token incluye el rol del usuario.

Implementación: `backend/auth.py`
Prueba: `tests/test_auth.py::test_login_invalid`

---

## HU-03 (A) Crear finca

**Como** operador o administrador
**quiero** registrar una finca con nombre, ubicación y área
**para** organizar los lotes que trabajo.

**Criterios**
- El nombre es obligatorio.
- El área debe ser un número positivo si se indica.
- Solo roles `admin` y `operador` pueden crear.

Implementación: `backend/routers/farms.py::create_farm`
Prueba: `tests/test_farms.py::test_farm_crud`, `test_user_cannot_create_farm`

---

## HU-04 (A) Crear lote asociado a una finca

**Como** operador
**quiero** crear lotes dentro de una finca
**para** segmentar el terreno.

**Criterios**
- No se permite crear un lote si la finca no existe.
- No puedo crear lotes en fincas de otros, salvo si soy admin.

Implementación: `backend/routers/farms.py::create_lot`
Prueba: `tests/test_farms.py::test_lot_requires_farm`

---

## HU-05 (B) Crear cultivo en un lote

**Como** operador
**quiero** registrar el cultivo sembrado en cada lote (especie, variedad, fecha)
**para** llevar trazabilidad por cultivo.

**Criterios**
- La especie es obligatoria.
- Debe existir el lote referenciado.

Implementación: `backend/routers/crops.py`
Prueba: `tests/test_farms.py` (y manualmente por la UI)

---

## HU-06 (A) Cargar imagen de hoja

**Como** usuario autenticado
**quiero** subir una foto de hoja asociada opcionalmente a un cultivo
**para** poder analizar su estado sanitario.

**Criterios**
- Solo acepta `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`.
- El tamaño máximo es 10 MB.
- Se guarda con un nombre único (UUID).
- Se registra quién la subió y cuándo.

Implementación: `backend/routers/images.py::upload_image`
Prueba: `tests/test_images.py::test_upload_and_analyze_without_model`, `test_rejects_bad_extension`

---

## HU-07 (A) Analizar imagen con el modelo IA

**Como** usuario
**quiero** disparar el clasificador visual sobre una imagen cargada
**para** saber cuántas hojas hay sanas, con mancha y secas.

**Criterios**
- La API responde con el conteo por clase, confianza media y tiempo de inferencia.
- Si no hay modelo cargado, se responde en modo simulado etiquetado como tal.
- Se guarda la inferencia y su versión del modelo.
- Si el porcentaje de hojas con mancha o seca supera cierto umbral, se crea incidencia automática.

Implementación: `backend/routers/images.py::analyze_image`, `ai_service/inference.py`
Prueba: `tests/test_images.py::test_upload_and_analyze_without_model`, `tests/test_ai_service.py`

---

## HU-08 (B) Historial de inferencias

**Como** usuario
**quiero** consultar el historial de análisis que he realizado
**para** hacer seguimiento al estado de mis cultivos.

**Criterios**
- Los usuarios solo ven sus propias inferencias.
- Los admin ven todas.
- Se puede filtrar por revisadas por experto.

Implementación: `backend/routers/inferences.py::list_inferences`
Prueba: manual vía UI y API.

---

## HU-09 (B) Revisión experta

**Como** operador o administrador
**quiero** marcar una inferencia como revisada y dejar notas
**para** validar los resultados del modelo y tener trazabilidad agronómica.

**Criterios**
- Solo `admin` y `operador` pueden marcar revisiones.
- La nota del experto queda registrada.

Implementación: `backend/routers/inferences.py::review_inference`
Prueba: manual vía UI.

---

## HU-10 (A) Panel de incidencias

**Como** operador
**quiero** ver un panel con las incidencias abiertas por mancha o sequedad
**para** priorizar la intervención en campo.

**Criterios**
- Se listan todas las incidencias filtrables por estado y severidad.
- Puedo cerrarlas, dejarlas en revisión o reabrirlas.
- Al cerrarse queda registrado el instante.
- La severidad se calcula automáticamente: baja (0-25% hojas afectadas), media (25-50%), alta (>50%).

Implementación: `backend/routers/incidents.py`
Prueba: manual vía UI y API.

---

## Trazabilidad requisito - prueba

| HU | Endpoint | Prueba automatizada |
|---|---|---|
| HU-01 | POST /auth/register | test_auth.py::test_register_and_login, test_register_duplicate |
| HU-02 | POST /auth/login | test_auth.py::test_login_invalid, test_me_with_token |
| HU-03 | POST /farms | test_farms.py::test_farm_crud, test_user_cannot_create_farm |
| HU-04 | POST /lots | test_farms.py::test_lot_requires_farm |
| HU-06 | POST /images | test_images.py::test_upload_and_analyze_without_model, test_rejects_bad_extension |
| HU-07 | POST /images/{id}/analyze | test_images.py::test_upload_and_analyze_without_model, test_ai_service.py |
| HU-08/09/10 | /inferences, /incidents | Validación manual vía UI y Swagger |
