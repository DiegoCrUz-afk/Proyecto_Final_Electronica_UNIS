# Entregables para el profesor

**Integrantes del grupo:** Sharly Abraham Alvarado Alvarez, Kenneth Raúl Bernales Yee, Diego Rodrigo Cruz Duarte, José Javier de León Aguilar, Oscar Mauricio Fletes Marroquín, Jorge André Gil Leonardo, Jose Eduardo Piedrasanta García, Josué Darío Sacol Cojón.

Esta carpeta junta todo lo que pide el enunciado (sección 7.1, paquete de entrega final). Lo que ya está listo se puede entregar tal cual; lo que depende de la máquina armada se anota abajo.

| # | Lo que pide el profesor | Dónde está | Estado |
|---|---|---|---|
| 1 | Máquina física funcional y segura | (la máquina) | **Falta armarla y probarla** |
| 2 | Esquemático completo y legible, editable | `02_Simulacion_y_capturas\LTspice\SISTEMA_COMPLETO.asc` (+ `.png`) y `Multisim\SISTEMA_COMPLETO.ms14`; un dibujo por bloque en el Anexo B del informe | Listo |
| 3 | Archivos originales de simulación y capturas | `02_Simulacion_y_capturas\` (LTspice, Multisim, `ondas\`, `logica\`) | Listo (simulación) |
| 4 | Informe técnico (máx. 15 páginas sin anexos) | `01_Informe_tecnico\Informe_tecnico.pdf` y `.docx` (10 páginas + anexos) | Listo con cálculos y simulación; agregar mediciones reales |
| 5 | BOM con costo, hojas de datos y fotos del montaje | `04_BOM_y_hojas_de_datos\Lista_de_compras_La_Electronica.pdf`; hojas de datos en el Anexo D del informe | BOM listo; **faltan las fotos del montaje** |
| 6 | Video de 3 a 5 minutos | `06_Video\Guion_del_video.md` (guion) | **Falta grabarlo** |
| 7 | Presentación breve y defensa individual | `07_Presentacion_y_defensa\Presentacion.pdf` y `Preguntas_de_defensa.md` | Listo |

Documentación obligatoria de la lógica (RF-04): tabla de verdad de 16 combinaciones, funciones booleanas, mapas de Karnaugh y simulación de compuertas están en la sección 4 del informe y en `02_Simulacion_y_capturas\logica\`.

## Contenido de las carpetas
- `01_Informe_tecnico`: informe en PDF y Word (editable) y el diagrama de bloques en HTML.
- `02_Simulacion_y_capturas`: LTspice (esquemáticos por bloque y completo), Multisim, capturas de señales (`ondas`: BJT, PWM, compuerta, MOSFET, encoder, sistema completo) y prueba de las 16 combinaciones lógicas (`logica`). La carpeta `3_archivos_tecnicos` dentro de esta contiene los modelos que usan los esquemáticos de LTspice (no moverla).
- `03_Montaje_y_maqueta`: 3D de las protoboards paso a paso, lista de conexiones, 3D de la banda y piezas de corte láser (DWG).
- `04_BOM_y_hojas_de_datos`: lista de compras con precios.
- `05_Pruebas_y_mediciones`: guía con las 10 pruebas en vivo y las tablas para anotar lo medido.
- `06_Video`: guion del video.
- `07_Presentacion_y_defensa`: diapositivas y preguntas posibles.

## Qué hay que agregar cuando la máquina esté armada
1. Medir con la Guía de pruebas y anotar en la columna "Medido".
2. Agregar al informe (sección 6) las tablas y las capturas reales del osciloscopio, y compararlas con la simulación.
3. Tomar fotos del montaje y ponerlas en el anexo del informe.
4. Grabar el video con el guion.
5. Revisar los precios de la lista de compras antes de entregar.

Los resultados del informe son de simulación con un motor supuesto de 12 V (no es el motor definitivo). Con el motor real hay que recalibrar el trimpot de sobrecorriente y la referencia de velocidad.

## Cómo se regeneran los archivos
Scripts en `3_archivos_tecnicos\entregables\` (Python 3.13 con `py -3.13`): `logica_tabla.py`, `capturas_ondas.py`, `generar_informe.py`, `exportar_pdf.ps1` y `generar_presentacion.py`.
