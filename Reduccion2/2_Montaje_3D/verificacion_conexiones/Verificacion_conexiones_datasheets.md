# Verificación de las conexiones del 3D contra los datasheets

Fuentes (leídas el 10/11/2026): SN74HC00 (SCLS181H), SN74HC08 (SCLS081J), SN74HC14 (SCLS085L), LM393 (SLCS005AH) de Texas Instruments; 2N3904 (onsemi 2N3904/D, rev. 3); IRLZ44NPbF (International Rectifier PD-94831); 1N5817-1N5819 (Vishay 88525); TCRT5000 (Vishay 83760).

## 1. Patas de los circuitos integrados contra el datasheet

| CI | Modelo | Patas | Resultado |
|---|---|---|---|
| U1 | LM393 | 8 | OK |
| U8 | 74HC00 | 14 | OK |
| U9 | 74HC08 | 14 | OK |
| U11 | 74HC14 | 14 | OK |

## 2. Circuito completo simulado desde el netlist armado con el 3D

El netlist (`verificacion_conexiones/circuito_desde_3D.cir`) se genera **solo** con las piezas y redes del HTML y las patas del datasheet. Motor SUPUESTO (12 Ω, 3 mH), fototransistor simulado como corriente (2 µA / 50 µA), chips con modelos de comportamiento.

| Situación | p (sensor) | M | N | F | LED objeto (V) | LED rojo (V) | Velocidad (rpm) |
|---|---|---|---|---|---|---|---|
| Normal (E=1, G=1, sin objeto) | 0.03 | 4.98 | 4.80 | 0.00 | 5.00 | 0.00 | 898 |
| Con objeto | 4.93 | 4.98 | 0.00 | 0.00 | 2.00 | 0.00 | 469 |
| Objeto retirado | 0.03 | 4.98 | 4.80 | 0.00 | 5.00 | 0.00 | 897 |
| Cubierta abierta (G=0) | 0.03 | -0.00 | -0.00 | 0.00 | 5.00 | 0.00 | 151 |
| Falla guardada (FALLA pulsada y soltada) | 0.03 | 0.00 | 0.00 | 4.65 | 5.00 | 1.80 | 0 |
| Después de RESET | 0.03 | 4.98 | 4.80 | 0.00 | 5.00 | 0.00 | 897 |

| Comprobación | Resultado |
|---|---|
| p = 0 sin objeto y 5 V con objeto | OK |
| sin objeto: M = N = 1 | OK |
| con objeto: M = 1, N = 0 | OK |
| velocidad con objeto entre 35 y 65 por ciento de la normal (valor 52 por ciento) | OK |
| cubierta abierta: M = 0 y el motor frena | OK |
| falla guardada: F = 1, M = 0 y el LED rojo enciende | OK |
| después de RESET: F = 0 y el motor vuelve a correr | OK |
| LED de objeto: enciende con objeto y apaga sin objeto | OK |

## Resultado

Diferencias: 0. TODO COINCIDE con los datasheets y el circuito armado desde el 3D funciona en simulación.

Límites: los chips son modelos de comportamiento y el motor y el fototransistor son supuestos. Para el 2N3904, el IRLZ44N, el 1N5819 y el TCRT5000 el script confirma que los NOMBRES de pata del 3D (E-B-C, G-D-S, A-K, C-E) se conectan como dice el datasheet; la orientación física al insertar la pieza se confirma con el multímetro (TCRT5000: modo diodo).
