# Análisis de riesgos

| # | Riesgo | Categoría | Impacto | Probabilidad | Mitigación |
|---|---|---|---|---|---|
| R1 | El modelo clasifica incorrectamente una hoja sana como mancha (falso positivo) | Precisión IA | Medio | Media | Toda inferencia automática requiere revisión experta antes de cerrar incidencia; el experto puede marcar y dejar nota |
| R2 | El modelo falla con fondos vegetales similares a hojas (confusión con el entorno) | Sesgo dataset | Medio | Media | Documentado en el informe anterior; línea de mejora: ampliar dataset con fondos neutros y aplicar filtros HSV post-inferencia |
| R3 | Un usuario accede a datos de otro | Seguridad / privacidad | Alto | Baja | Filtro por `owner_id` en todos los endpoints; roles explícitos con `require_role` |
| R4 | Fuga de credenciales en el repositorio | Seguridad | Alto | Baja | `.env` en `.gitignore`, `.env.example` sin secretos reales, JWT con `SECRET_KEY` configurable |
| R5 | Subida de archivos maliciosos (ej. ejecutables disfrazados) | Seguridad | Medio | Media | Validación estricta de extensión, límite de 10 MB, nombres aleatorios con UUID |
| R6 | Sobrecarga del modelo con muchas solicitudes simultáneas | Rendimiento | Medio | Media | El modelo se carga una vez como singleton; para producción, escalar el servicio IA aparte detrás de una cola |
| R7 | Pérdida de datos por caída de la base | Disponibilidad | Alto | Baja | Volumen persistente en Docker, backups programados en producción |
| R8 | Explicabilidad: el usuario no entiende por qué el modelo decidió "mancha" | Explicabilidad | Medio | Alta | Se devuelve la imagen anotada con máscaras, confianza y bounding box; permite revisión visual |
| R9 | Variaciones de iluminación degradan la precisión | Precisión IA | Medio | Alta | Preprocesamiento con ecualización del canal L en LAB; se documenta el requisito de luz frontal moderada |
| R10 | Uso indebido para decidir sin supervisión humana | Ético / legal | Alto | Baja | Interfaz obliga a revisión experta antes de cerrar incidencias; se declara explícitamente que el sistema es un apoyo a la decisión, no un reemplazo |
| R11 | Dependencia de un único modelo entrenado por el equipo | Operación | Medio | Media | El servicio IA está desacoplado: se puede sustituir por otro modelo cambiando el `.pt` y la lógica de interpretación de clases |
| R12 | Datos personales en imágenes (si aparecen personas) | Privacidad | Alto | Baja | Las imágenes se guardan localmente y no se publican; la política del sistema prohíbe cargar fotos con personas identificables |

## Plan de contingencia

- **Si el modelo falla de forma sistemática en un cultivo nuevo:** retornar al modo simulado y exigir solo revisión experta, hasta re-entrenar el modelo con datos del nuevo cultivo.
- **Si la base se corrompe:** restaurar último backup y re-ejecutar las inferencias de las imágenes ya cargadas en el filesystem.
- **Si un usuario reporta una decisión errónea:** el operador puede marcar la inferencia como no revisada y cerrar la incidencia asociada como "falso positivo" en el campo de descripción.
