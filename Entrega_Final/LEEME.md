# Entrega final · diseño de 12 V

Miniestación industrial automatizada (banda transportadora sin microcontroladores), alimentada con 12 V. UNIS · Electrónica · noviembre de 2026.

| Carpeta | Qué hay |
|---|---|
| `1_Informe` | Informe técnico (`.docx` y `.pdf`) solo de este diseño |
| `2_Esquematicos` | `SISTEMA_COMPLETO.asc` y `SISTEMA_SOLO_CIRCUITO.asc` (LTspice, con su `.png`) y un `.asc` y `.png` por bloque |
| `3_Simulaciones` | Archivos `.cir`, capturas de ondas y prueba de la lógica (16 combinaciones, mapas de Karnaugh) |
| `4_BOM_y_datasheets` | `BOM.xlsx` (con fórmulas), `BOM.md` y `BOM.csv` con precios de La Electrónica (12/11/2026), columna Origen (Comprado o Inventario) y dos totales; PDF de las hojas de datos en `Datasheets` |
| `5_Fotos_y_Video` | Imágenes del modelo 3D (`Modelo_3D`) y carpeta `Video` para el video de la demostración |
| `6_Presentacion` | Presentación en PDF |

## Estado
- Diseñado, calculado y simulado en LTspice (11 bloques).
- Armado completo en protoboard (5 protoboards, 252 cables, 120 piezas). En la primera prueba (09/11/2026), con una fuente de límite 0.6 A, el voltaje cayó (9.98 V en el jack) y la causa no se identificó. Los resultados del informe son de cálculo y simulación.

## Hojas de datos (`4_BOM_y_datasheets\Datasheets`)
La tienda vende varias piezas con marca propia (LCC) y el mismo número de parte del fabricante original; se usa la hoja de datos del fabricante de ese número de parte.
SN74HC00, SN74HC08, SN74HC14, LM393, LM358, LM324, NE555 (Texas Instruments) · 2N3904, 2N3906, BD139 (onsemi) · IRFZ44N (Infineon) · 1N4148, 1N4007, 1N5819, Zener 1N4734A, TCRT5000 (Vishay) · ITR9608 (Everlight) · Trimpot 3296 (Bourns).
Sin hoja de datos de fabricante: buzzer, motor N20, NTC (productos de la tienda).

## Cómo abrir los esquemáticos
Abrir `2_Esquematicos\SISTEMA_COMPLETO.asc` o `SISTEMA_SOLO_CIRCUITO.asc` con LTspice y usar Run. Los `.inc` y `.asy` de la misma carpeta deben quedarse junto a los `.asc`.
