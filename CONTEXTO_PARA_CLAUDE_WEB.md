# Contexto completo del proyecto (para pegar en un chat nuevo de Claude)

Pega este documento como primer mensaje (o súbelo como archivo) y di en qué necesitas ayuda. Todo lo de aquí es lo que se sabe hasta el 10/11/2026.

## 1. Quién soy y cómo quiero que me respondas
- Soy Diego Rodrigo Cruz Duarte, estudiante de Electrónica en la UNIS (Guatemala), segundo semestre 2026.
- Respuestas en **español, cortas y sencillas**, nivel estudiante. Tablas cuando sirvan. Sin frases tipo "como IA".
- No inventes datos: si no sabes algo (por ejemplo la pata de un componente), dilo y dime cómo comprobarlo con el multímetro.
- Antes de hacer algo grande o que cambie cosas, pregúntame. Cuidado con acciones que puedan dañar mi PC.
- Todo archivo del proyecto va dentro de la carpeta del proyecto, sin duplicados "v2".

## 2. El proyecto
**Miniestación industrial automatizada**: banda transportadora de escritorio, **sin microcontroladores**, solo analógico + compuertas 74HC. Enunciado oficial: `Enunciado_del_profesor.docx` (en la carpeta del proyecto).

Qué hace: un sensor infrarrojo detecta un objeto → con objeto la velocidad baja a 40–60 % de la normal. Velocidad regulada con encoder (lazo cerrado). El motor se detiene si E = 0 (interruptor), G = 0 (cubierta abierta) o F = 1 (falla de corriente o temperatura). Las fallas quedan guardadas hasta pulsar reset. Alarma sonora (buzzer) y luminosa (LED rojo).

Requisitos clave del enunciado: motor DC 12 V ≤ 500 mA; fuente externa 12 V ≥ 2 A; 5 V ± 5 % (Vin 11–13 V, 30–120 mA) con Zener + BJT de paso; un amplificador BJT emisor común (sensor óptico) y uno con operacional (shunt de corriente); PWM sin controlador programable + MOSFET; sobrecorriente, umbral térmico 45–55 °C, cubierta, enclavamiento y reset manual; "montaje final soldado, sin protoboard como producto final".

Entrega final: máquina, esquemático, simulaciones y capturas, informe ≤ 15 páginas, BOM con costo, video 3–5 min, presentación y defensa individual. 10 pruebas en vivo.

## 3. Lógica (variables E, G, P, F → M, N, L, A)
E = habilitado, G = cubierta cerrada, P = objeto, F = falla guardada. M = permiso del motor, N = velocidad normal, L = reducida, A = alarma.
**M = E·G·F'**, **N = M·P'**, **L = M·P**, **A = F**. Las 16 combinaciones se probaron en LTspice: todas coinciden.
Pestillo de falla con NAND 74HC00; entradas con 10 kΩ a GND, filtro RC (10 kΩ + 100 nF) y dos inversores Schmitt 74HC14; reset automático al encender (1 µF + 47 kΩ + 1N4148). El reset solo actúa si ya no hay falla (reset_n = NAND(rst, setn)). `setn` = señal activa en bajo de las fallas de corriente o temperatura.

## 4. Los 11 bloques (valores de diseño, nombres = señales del esquemático)
Nodos: vm (12 V después de D1), v5 (5 V), 0 (GND).
- **Entrada:** jack 12 V → 1N4007 (D1, banda = cátodo hacia vm) → vm; Cin 1000 µF.
- **1 Regulador:** Rz 510 Ω, Zener 5.6 V (1N4734A), trimpot 100 Ω en serie con el Zener, BD139 de paso (disipador, ≈ 0.9 W peor caso), Cout 100 µF, 100 nF. v5 ≈ 4.84–4.95 V simulado.
- **2 Sensor IR:** TCRT5000, Rled 270 Ω; Q2 2N3904 emisor común (R1 47k, R2 10k, Rc 680, RE 150; ganancia ≈ −4); comparador LM393 con histéresis (Rh 220k); umbral con trimpot 10k. p ≈ 0 V sin objeto, ≈ 4.9 V con objeto.
- **3 Sobrecorriente:** shunt 0.5 Ω, LM358 ganancia 7.8 (Rg 1k, Rf 6.8k), detector de picos 1N4148 + 100 nF + 22k, filtro 10k + 10 µF, LM393 con ref ≈ 2 V; dispara ≈ 0.7 A.
- **4 Temperatura:** NTC 10k (B 3950) + Rfix 10k; LM393; trimpot 10k; umbral ajustable 44–57 °C; histéresis ≈ 2.6 °C.
- **5 Lógica:** 74HC00 ×1, 74HC08 (×2 chips en total con potencia), 74HC14.
- **6 PWM:** NE555 astable (Ra 1k, Rb 10k, Ct 10 nF → 6.9 kHz) + LM393 compara rampa (1.67–3.33 V) con vctrl.
- **7 Potencia:** AND 74HC08 (PWM · M), par 2N3904/2N3906, Rg 47 Ω, Rpd 10k, IRFZ44N, diodo 1N5819, shunt 0.5 Ω.
- **8 Encoder y F-V:** opto ranurado + disco de 20 ranuras, LM393, 555 monoestable (220 µs), filtro RC doble 10k + 1 µF. vspd = 1.1 mV/Hz.
- **9 Referencia de velocidad:** Rt 68k + trimpot 10k → vref ≈ 0.53 V; Q5 (2N3904) con L pone otro trimpot en paralelo → ≈ 0.26 V.
- **10 Amplificador de error:** LM324/LM358, vctrl = 10·(vref − vspd) + 2.6 V.
- **11 Alarma:** 2N3904 saturado → buzzer 12 V; LED rojo con 470 Ω.
Chips: LM393 ×5, LM358, LM324, NE555 ×2, 74HC00, 74HC08 ×3, 74HC14.
Simulaciones (LTspice, motor supuesto 12 Ω, 3 mH): 1394 rpm normal, 789 rpm con objeto (56 %), cubierta abierta corta M en 1 ms, falla enclavada, reset ok.

## 5. Montaje real (protoboards)
5 protoboards: **A, B, C** son las 3 de una PRO'S KIT BX-4135 (comparten rieles); **D, E** sueltas.
- A: entrada, regulador, potencia, alarma. B: sensor IR, sobrecorriente, temperatura. C: lógica, LED de objeto, referencia de velocidad. D: amplificador de error, PWM. E: encoder.
- 252 cables numerados y 120 piezas, todo verificado contra el esquemático (11 bloques, 328 pines).
- Los agujeros se nombran como está impreso: placa-letra-fila, por ejemplo `A-F56`.

**Dispositivos externos (cables a la placa):**
| Dispositivo | Cable | Agujero | Pin | Va a |
|---|---|---|---|---|
| TCRT5000 | 220 | B-J49 | A (ánodo LED) | 270 Ω a 5 V |
| | 221 | B-J48 | K | GND |
| | 222 | B-J47 | C | 5 V |
| | 223 | B-J46 | E | base de Q2 |
| NTC 10k | 238 / 239 | B-F13 / B-F11 | 2 patas | 5 V / `tnode` |
| Pulsador reset | 236 / 237 | C-B33 / C-B31 | A1 / B2 (diagonal) | 5 V / `RST` |
| Toggle E | 232 / 233 | C-J28 / C-J26 | COM (central) / lateral | 5 V / `E` |
| Micro-switch G | 234 / 235 | C-G36 / C-G34 | COM(2) / NO(3) | 5 V / `G` |
| Opto encoder | 224 / 225 / 226 / 227 | E-F33 / F32 / E33 / E32 | A / K / C / E | 220 Ω a 5 V / GND / `enc` / GND |
Las patas exactas del TCRT5000, el toggle y el micro-switch hay que confirmarlas con multímetro (diodo / continuidad).

Puntos de medición clave: `setn` en C-J50 (5 V normal, 0 V en falla); v5 en A-J44; vm en A-J52; base de Q1 en A-J42; jack en A-F56.

**Entradas de usuario (lógica):** TBE = interruptor de palanca (E); TBG = micro-switch "cubierta" (G, se simula presionando la palanca con cartón); RST = pulsador de reset. M = E·G·F'; N = M·P'; L = M·P; A = F. Las fallas (`setn`: sobrecorriente o temperatura) quedan guardadas; el reset solo borra si la causa ya no está; hay reset automático al encender.

**Referencia de velocidad (REFVEL):** trimpot T1 = velocidad normal (vref ≈ 0.53 V); T2 = velocidad reducida (≈ 0.26 V), se pone en paralelo cuando Q5 conduce (señal L). Si el trimpot es 103 (10k) sirve; uno de 104 se ajusta a ≈ 10k; uno de 102 solo no sirve (necesita una fija de 8.2k–9.1k en serie).

**Modo medición del 3D (`6_Montaje_3D`):** botón "Empezar por la entrada" → bloque por bloque (ENTRADA, REG5V, SENSOR_IR, SOBRECORRIENTE, TEMPERATURA, LÓGICA, LED OBJETO, REFVEL, ENCODER, ERROR, PWM, POTENCIA, ALARMA). Muestra dónde poner la punta roja y la negra, el valor esperado (46 puntos en total), y si no sale igual da la causa probable. No modifica piezas ni cables.

**Datos de diseño útiles para diagnosticar:** vm ≈ 11.1–11.3 V (después de D1); v5 ≈ 4.84–4.95 V; sobrecorriente dispara ≈ 0.7 A; PWM 6.9 kHz; IRFZ44N con ≈ 4.3 V en la compuerta (medir Vds, si > 0.3 V cambiar el MOSFET); vctrl = 10·(vref − vspd) + 2.6 V.

## 6. Estado actual (qué está hecho)
- Diseño, cálculos y simulación completos; esquemáticos LTspice y Multisim.
- 3D v3 de las protoboards paso a paso y con **modo medición** (en `6_Montaje_3D`), lista de conexiones, 3D de la banda, piezas de corte láser (DWG, cartón de 1 mm).
- Carpeta `9_Entregables_profesor`: informe técnico (PDF + Word, 10 páginas + anexos), capturas de señales, tabla de verdad con Karnaugh, BOM (lista de compras La Electrónica ≈ Q495), guía de pruebas, guion de video, presentación de 12 diapositivas y 25 preguntas de defensa.
- Repo en GitHub: https://github.com/DiegoCrUz-afk/Proyecto_Final_Electronica_UNIS (rama main). Lo más nuevo (3D con dispositivos reales y modo medición, entregables, piezas láser) **todavía no está subido**.

## 7. Problema actual (primera prueba con la fuente)
Al encender, el voltaje cae: jack 9.98 V (debería ser 12), luego valores 9 V fijo, 4.5 V y bajando, 3.5 V bajando, 3.1 V, 1.23 V, 0.6 V, 3.26 V y bajando, 3.5 V bajando rápido (sin etiquetar a qué punto corresponde cada uno). Sospecha: fuente en límite de corriente (puesta en 0.6 A) por un corto o una pieza mal puesta (electrolítico o diodo al revés, chip invertido). Plan: apagar, medir resistencia 12 V–GND y 5 V–GND, revisar polaridades, tocar piezas calientes, probar solo la placa A sin cables a las otras. Falta saber: qué fuente usa, qué corriente marca, qué punto era cada número.

Plan de diagnóstico (en orden): 1) apagar y mirar si la fuente está en CC (límite de corriente); 2) con la fuente apagada, medir resistencia 12 V–GND y 5 V–GND (no debe ser ~0 Ω); 3) revisar polaridades: 1000 µF, 100 µF, 10 µF, 1 µF, banda de D1 hacia vm, Zener, chips con la muesca bien; 4) tocar con cuidado BD139, electrolíticos y chips para ver si algo calienta; 5) probar solo la placa A, sin los cables hacia B, C, D, E ni el motor; 6) ir conectando una placa a la vez y medir con el modo medición del 3D.

## 8. Pendientes y alertas
- **Falta:** armar y probar la máquina, mediciones reales, fotos del montaje, grabar el video.
- **Montaje final soldado:** el enunciado pide placa perforada o PCB; el plan actual es todo en protoboard. Preguntar al profesor.
- **Motor:** el enunciado pide 12 V ≤ 500 mA; el motor elegido (Steren MOT-125, eje D, 6 V, 100:1) no coincide. No conectarlo a 12 V sin limitar el PWM. Hay que medir su corriente y recalibrar sobrecorriente y referencia.
- Sin pulsador: falta foto del pulsador 6×6×15 de 4 patas.
- Posibles revisiones: pasar la polaridad de los 1 µF y el LED de objeto (680 Ω) al esquemático y a la lista de compras; regenerar el PDF de materiales por protoboard.

- Video: guion de 4 min en `06_Video\Guion_del_video.md` (debe mostrar los modos y al menos una protección, por ejemplo la falla de temperatura con reset). Defensa: 25 preguntas con respuesta en `07_Presentacion_y_defensa\Preguntas_de_defensa.md`. Pruebas en vivo: `05_Pruebas_y_mediciones\Guia_de_pruebas.md`.
- Las patas del TCRT5000, optointerruptor, toggle y micro-switch hay que confirmarlas con multímetro antes de conectar.
- Solo estoy midiendo: no modificar las protoboards ni los cables del 3D de las placas A y B.

## 9. Dónde está cada cosa (carpeta `Documents\Proyecto_Final_Electronica_UNIS\`)
`1_Arquitectura`, `2_LTspice` (esquemáticos), `3_archivos_tecnicos` (scripts y modelos: `sistema.inc` es la fuente de verdad del circuito), `4_Documentacion`, `5_Compras_y_Pruebas` (lista de compras y guía de pruebas), `6_Montaje_3D`, `7_Multisim`, `8_Maqueta_corte_laser`, `9_Entregables_profesor`, `CONTEXTO_SESION.md` (historial detallado), `CONTEXTO_PROYECTO.md`.
