# Reducción 2 · miniestación industrial (5 V directos)

Versión **de validación por fases**, no la entrega final. La carpeta original del proyecto no se tocó.

## Qué hay
| Carpeta | Contenido |
|---|---|
| `1_LTspice` | Pruebas (`prueba_*.cir`), `reduccion2.inc` (lógica con LED de objeto, IRLZ44N), esquemáticos `BLOQUE_*.asc`, `resultado_logica.md`, capturas en `capturas/`, scripts |
| `2_Montaje_3D` | `Protoboards_3D_reduccion2.html` (un solo archivo, abre sin internet; 3 protoboards BX-4135 con carga pareja (A 37 filas: entrada, potencia, LED rojo · B 39: sensor IR y entradas · C 35: pestillo, decisión, LED de objeto), armado paso a paso y modo medición rojo/negro) y `generador/` |
| `3_Pruebas` | `Guia_de_pruebas_Reduccion2.md`: 31 mediciones por bloque con el agujero exacto de cada punta |
(La lista de compras no se hizo: ya hay materiales.)

## Qué se simuló (LTspice) y qué NO
- **Lógica** (16 combinaciones de E, G, P, F + pestillo + LED de objeto): coincide con M = E·G·F', N = M·P', L = M·P. Usa modelos de comportamiento de las compuertas, no chips 74HC reales.
- **Sensor IR**: p = 0.03 V sin objeto, 4.93 V con objeto.
- **Potencia** (IRLZ44N + Rs + puente 2N3904) con motor **supuesto** (12 Ω, 3 mH, Ke 0.035, carga 0.004 N·m): Rs = 10 Ω da 66 % (fuera de 40–60 %); **Rs = 15 Ω da 50 %** (12 a 18 Ω dan 60 a 41 %). Con el motor real hay que reajustar; la velocidad baja mucho más rápido de lo que parece al subir Rs (28 % con 22 Ω).
- **Alertas de la potencia (no resueltas):** (1) el arranque pide ~390 mA y el 2N3904 aguanta 200 mA (0.17 s por encima): usa un MOSFET como puente o confirma la corriente real del motor; la variante con MOSFET también se simuló (`prueba_potencia_Rs15_mos.cir`). (2) El IRLZ44N del LTspice es un **modelo propio aproximado**, no el del fabricante. (3) El motor Steren (6 V) no coincide con lo supuesto: **mide su corriente a 5 V** antes de dimensionar Rs.
- Valores esperados de la guía = cálculo/simulación, **no mediciones de la máquina**.

## 3D: verificaciones hechas
- 3 placas, 48 piezas, 112 cables, 37 redes: ninguna tira mezcla redes y ninguna red queda partida (`generador/verificar_3d.py`).
- Cada pata del 3D coincide con el netlist de los esquemáticos dibujados (todas las piezas discretas y las patas de los 4 chips: 0 diferencias; `generador/comparar_3d_vs_esquematico.py`).
- Cables a ras de la placa, sin saltos. `generador/chequeo_choques.py` (el del original): 0 cables atraviesan una pieza y 0 cruces entre cables (112 cables).
- Revisado a ojo en Chrome: chips con la muesca arriba, pata 1 arriba a la izquierda, VCC arriba a la derecha y GND abajo (ejemplo U9); paso a paso de la placa A con 43 pasos y pasos de PRUEBAS tras cada bloque; condensadores con + y -. Solo se miró con detalle U9, la placa C y el paso a paso de A; **el resto de las placas y piezas no se revisó una por una**.
- Errores del v2 que NO se repiten: muesca de los chips (plantilla v3), texto de pruebas del diodo (no hay D1), capacitor de 1 µF con polaridad, motor rotulado como Steren de 6 V a 5 V, TCRT con 4 postes (no caja negra), cables a ras, un solo juego de archivos dentro de la carpeta.
- Pendiente confirmar con la placa física: si los rieles de la BX-4135 están partidos a la mitad (el 3D dibuja puentes entre mitades, no lo asume).
- Abierto en Chrome (servidor local): carga sin errores de consola, modo medición marca roja y negra. No se revisó a ojo cada cable ni la vista de cada placa.
- Pendiente de confirmar con multímetro: patas del TCRT5000, toggle, micro-switch y pulsadores.

## Qué demuestra y qué queda en fase 2
Demuestra: sensor con BJT en emisor común, lógica combinacional y enclavamiento de falla con reset manual, corte por E y G, velocidad reducida con objeto. Pendiente: regulador Zener + BJT, shunt con operacional y sobrecorriente, temperatura, buzzer, PWM y lazo con encoder, montaje soldado y motor de 12 V ≤ 500 mA. Hay que **avisar al profesor** que se presenta por fases y preguntar por el montaje soldado.

## Regenerar
`1_LTspice\scripts\` (gen_logica, check_logica, gen_potencia, graficas, gen_esquematicos) · `2_Montaje_3D\generador\exportar_r2.py` (usa `py -3.13`; la plantilla sale de `adaptar_plantilla.py`) · `3_Pruebas\gen_guia.py`.

## Actualización: pruebas por bloque y cables ordenados (10/11/2026)
- **7 bloques en orden de armado:** 0 Alimentación, 1 Sensor IR, 2 Entradas (74HC14), 3 Pestillo (74HC00), 4 Lógica (74HC08, sin motor) y LED de objeto, 5 Potencia con motor, 6 LED rojo y ajuste de la velocidad lenta. **40 pruebas**, cada una con: qué se mide, para qué sirve, condición previa, punta roja y negra (agujero exacto) y modo, valor esperado (con tabla si cambia), y qué revisar en orden. Cada bloque empieza con la prueba de resistencia 5 V–GND.
- **Una sola fuente de datos:** `2_Montaje_3D/generador/pruebas_r2.py` alimenta el modo medición del 3D y la guía (`3_Pruebas/gen_guia.py`). `3_Pruebas/check_sim_vs_guia.py` comprueba que los valores de la guía caen dentro de lo que dan los .log de LTspice (`Verificacion_sim_vs_guia.md`: 0 fuera de rango).
- **A medir / NO validado:** corriente del Steren, caída en Rs con objeto, velocidad con objeto, resistencias 5 V–GND exactas, LED rojo (valor del diseño original), TCRT5000 (valor del diseño original). Todo lo del motor está marcado NO validado.
- **Hallazgo de simulación:** el Vbe del 2N3904 puente sale ≈ 0.89 V, no 0.7 V.
- **Cables:** antes 112 (largo 3034, 283 giros, 2.53 giros por cable); ahora 107 (largo 3015, 287 giros, 2.68 por cable). Bajó la cantidad, el largo casi igual, los giros NO mejoraron. Numerados por bloque en orden de armado y coloreados por función (5 V rojo, GND negro, señal por color de bloque). Se probaron 1200 acomodos por bloque (antes 60). Chequeo de choques: 0 cables atraviesan piezas y 0 cruces; verificar_3d OK; 3D = esquemático con 0 diferencias.
- **Las posiciones de las piezas cambiaron** respecto a la versión anterior (también las del sensor y la lógica) porque el reparto en 7 bloques y el mejor acomodo las movieron. La Reducción 2 todavía no está armada.
- Rs se dibuja ahora con su valor real (antes salía "0.5 Ω 5 W", del shunt del original).

## Actualización: rieles y verificación contra datasheets (10/11/2026)
- **Arreglo del 3D:** las placas B y C ahora dibujan sus dos pares de rieles también cuando la placa vecina está oculta ("Solo B", paso a paso). Antes faltaba el par de la izquierda.
- **Verificación contra datasheets** (`2_Montaje_3D/verificacion_conexiones/Verificacion_conexiones_datasheets.md`, script `generador/verificar_contra_datasheets.py`): las patas de los 4 CI coinciden con los datasheets de TI; el circuito completo armado solo desde el 3D funciona en simulación (52 % de velocidad con objeto, motor supuesto). Límites: chips como modelos de comportamiento, motor y fototransistor supuestos; la orientación física de las piezas se confirma con multímetro (TCRT5000 en modo diodo).
