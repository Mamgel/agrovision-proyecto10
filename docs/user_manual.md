# Manual de usuario - AgroVision

## 1. Acceso

1. Abre el navegador en `http://127.0.0.1:7860`.
2. Si es tu primera vez, pulsa la pestaña **Registrarse**, llena usuario, correo, contraseña y selecciona rol. Pulsa **Registrar**.
3. Vuelve a la pestaña **Ingresar**, escribe tu usuario y contraseña, y pulsa **Iniciar sesión**.

## 2. Jerarquía de datos

El sistema se organiza así: Finca → Lote → Cultivo → Imagen → Inferencia → Incidencia.

Primero crea una finca, luego sus lotes, luego los cultivos de cada lote, y finalmente puedes cargar imágenes asociadas a un cultivo.

### Crear finca
Pestaña **Fincas**. Llena nombre, ubicación y área en hectáreas. Pulsa **Crear finca**.

### Crear lote
Pestaña **Lotes**. Indica el ID de la finca (lo ves en la tabla anterior), nombre del lote, área en metros cuadrados y descripción opcional. Pulsa **Crear lote**.

### Crear cultivo
Pestaña **Cultivos**. Indica el ID del lote, especie (por ejemplo `cafeto`) y variedad. Pulsa **Crear cultivo**.

## 3. Analizar una imagen

1. Pestaña **Análisis de imagen**.
2. Sube la foto de la hoja. Recomendaciones:
   - Luz frontal moderada, sin sombras duras ni contraluces.
   - La hoja debe ocupar la mayor parte del encuadre.
   - Evita fondos con otras hojas detrás.
3. (Opcional) Indica el ID del cultivo al que pertenece la foto.
4. Pulsa **Analizar**.
5. El sistema devuelve:
   - Conteo de hojas detectadas y por clase (sana, mancha, seca).
   - Confianza media de las detecciones.
   - Tiempo que tomó la inferencia.
   - Versión exacta del modelo que corrió.
   - La imagen anotada con las máscaras y los bounding boxes.

Si el porcentaje de hojas afectadas supera un umbral, el sistema crea automáticamente una incidencia abierta.

## 4. Revisar el historial

Pestaña **Historial**. Pulsa **Actualizar historial** para ver todos los análisis que has hecho.

Si eres operador o admin, puedes seleccionar una inferencia por su ID y marcarla como revisada, agregando notas del experto en el campo correspondiente.

## 5. Gestionar incidencias

Pestaña **Incidencias**.

Filtra por **estado** (abierta, en revisión, cerrada) y **severidad** (baja, media, alta). Pulsa **Listar**.

Para actualizar una incidencia, indica su ID, el nuevo estado y un comentario. Pulsa **Actualizar**.

## 6. Roles del sistema

| Rol | Puede hacer |
|---|---|
| usuario | Crear sus propias fincas, lotes, cultivos; cargar imágenes; analizar; ver su propio historial e incidencias |
| operador | Todo lo anterior + marcar inferencias como revisadas + gestionar incidencias |
| admin | Todo lo anterior + ver todos los datos del sistema + gestionar usuarios |

## 7. Preguntas frecuentes

**¿Por qué el modelo dice `simulated:...`?**
Porque no se cargó el archivo `best.pt` del modelo en `ai_service/models/`. Pide al administrador que lo deposite ahí y reinicie el sistema.

**¿Qué pasa si subo una foto borrosa?**
El modelo intenta su mejor interpretación, pero la confianza media será baja. Se recomienda rechazar el análisis y repetir la foto.

**¿Puedo descargar los resultados?**
La API en `/docs` permite obtener los datos en JSON. La imagen anotada queda guardada en `data/uploads/` como `annot_<uuid>.jpg`.
