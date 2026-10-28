# Guía de pruebas y mediciones

Las pruebas siguen la sección 9 del enunciado (10 pruebas en vivo) y los criterios de la sección 6. La columna "Esperado" sale de cálculo o de simulación en LTspice con un motor supuesto; la columna "Medido" se llena en el laboratorio. No se anota nada en "Medido" que no se haya medido.

Puntos de prueba que conviene dejar con pin o terminal en la protoboard: `v5`, `vm`, `tin`, `p`, `sh`, `setn`, `f`, `vspd`, `vref`, `vctrl`, `pwm`, `gate` (compuerta del MOSFET), `enc`.

Equipo disponible: Rigol DP832 (fuente variable para Vin de 11 a 13 V), Analog Discovery 3, NI ELVIS II, multímetro.

## Seguridad antes de empezar
- Solo fuente externa de 12 V. Nada conectado a la red de 110/120 V.
- Revisar la polaridad de los electrolíticos (Cin, Cout, Cd y los de 1 µF si son electrolíticos) antes de energizar.
- Limitar la corriente de la fuente (por ejemplo 0.6 A) en las primeras pruebas.
- No bloquear el motor a propósito ni usar llama. Para la sobrecorriente y la temperatura se usan los métodos controlados de abajo.

## Prueba 10 - Regulación y PWM (hacer primero)
| Qué medir | Condición | Esperado | Medido |
|---|---|---|---|
| v5 | Vin 11, 12 y 13 V; carga de 30, 75 y 120 mA (resistencia de carga en v5) | 4.75 a 5.25 V (simulación: 4.84 a 4.95 V sin ajuste) | |
| Temperatura del BD139 | 13 V, 120 mA, 5 min | Disipador tibio, sin quemar (≈ 0.9 W en peor caso) | |
| PWM (osciloscopio en `pwm`) | Operación normal | ≈ 6.9 kHz | |
| Compuerta (`gate`) | Operación normal | 0 a ≈ 4.4 V | |
| Vds del MOSFET | Operación normal | máx. ≈ 11.5 V (simulación) | |

Si v5 queda fuera de 5 V ± 5 %, ajustar el trimpot Rtr (100 Ω) y repetir con las seis combinaciones.

## Prueba 01 - Operación normal
Condición: E = 1, cubierta cerrada, sin objeto.
- Esperado (simulación con motor supuesto): arranque en ≈ 0.08 s, estable, M = 1, N = 1, L = 0. Velocidad normal: se anota la medida real.
- Medir: `vspd` (≈ 1.1 mV por Hz; con 20 ranuras, 500 Hz da ≈ 0.55 V), rpm = frecuencia del encoder × 60 / 20.

## Prueba 02 - Detección de objeto
- Pasar un objeto frente al sensor IR 10 veces. Documentar distancia y tipo de objeto. Criterio: 9 de 10.
- Esperado: `p` pasa de ≈ 0 V a ≈ 5 V; L = 1; la velocidad baja al 40-60 % de la normal (simulación: 56 %).
- Calibración: el trimpot del umbral del bloque 2.

| Intento | Detectó (sí/no) | Distancia | Objeto |
|---|---|---|---|
| 1 a 10 | | | |

## Prueba 03 - Amplificador BJT (sensor IR)
| Medida | Esperado (cálculo/simulación) | Medido |
|---|---|---|
| Vb (base de Q2) | ≈ 0.82 V | |
| Vc sin objeto / con objeto | 4.2 V / 2.9 V (hFE 200) | |
| Ganancia de pequeña señal | ≈ −3.95 (11.9 dB), fase 180° | |
| Entrada y salida en el osciloscopio (inyectar senoidal en `tin`) | Salida invertida | |

## Prueba 04 - Etapa operacional (shunt)
- Medir en `sh` (antes) y en la salida del LM358 (después).
- Esperado: ganancia 1 + 6.8k / 1k = 7.8. Con 0.3 A por el shunt de 0.5 Ω: ≈ 0.15 V antes, ≈ 1.2 V después.

| Corriente del motor | V en `sh` | V después del LM358 | Ganancia medida |
|---|---|---|---|
| | | | |

## Prueba 05 - Realimentación
- Lazo abierto: desconectar `vctrl` del amplificador de error y alimentarlo desde un trimpot; fijar la misma velocidad inicial.
- Aplicar la perturbación ligera y repetible (por ejemplo, una pequeña fricción siempre igual en la banda, sin bloquear el motor).
- Esperado (simulación): lazo cerrado baja ≈ 6.5 %, lazo abierto ≈ 25.9 %. Criterio de aceptación: error ≤ 20 % de la referencia.

| Caso | Velocidad sin carga | Velocidad con carga | Caída % | Tiempo de estabilización |
|---|---|---|---|---|
| Lazo abierto | | | | |
| Lazo cerrado | | | | |

## Prueba 06 - Seguridad de cubierta
- Abrir la cubierta con el motor en marcha.
- Esperado: M cae a 0 (simulación: 1 ms), el motor se detiene y la corriente es 0. Al cerrar, el motor reanuda (la cubierta no enclava).
- Comprobar también con el cable del interruptor desconectado: debe contar como "abierta".

## Prueba 07 - Falla de corriente
Método controlado (sin bloquear el motor): bajar el trimpot de la referencia del bloque 3 hasta que el umbral quede cerca de la corriente de trabajo; o inyectar con la fuente de laboratorio un voltaje en `sh` por una resistencia.
- Esperado: `setn` baja, f = 1, alarma encendida (LED y buzzer), M = 0. La falla se queda aunque se quite la causa.
- Registrar la corriente de disparo medida (simulación: ≈ 0.71 A con el motor supuesto; hay que recalibrar con el motor real) y verificar que el arranque no dispara.

## Prueba 08 - Umbral térmico
- Calentar el NTC de forma moderada (agua tibia o aire caliente suave) con un termómetro de referencia al lado.
- Esperado: dispara en el umbral elegido entre 45 y 55 °C (el trimpot cubre ≈ 44 a 57 °C; histéresis ≈ 2.6 °C).

| Umbral ajustado | Temperatura de disparo medida | Referencia usada |
|---|---|---|
| | | |

## Prueba 09 - Reset seguro
- Con la falla activa y la causa todavía presente (caliente), pulsar reset: la falla debe seguir.
- Dejar enfriar (o quitar la causa) y pulsar reset: la falla se limpia y el motor reanuda.
- Al encender el equipo, el reset automático limpia el pestillo.

## Integridad (20 minutos)
Operación continua 20 min. Anotar temperatura del BD139, del MOSFET y del motor; revisar conexiones.

## Ondas a capturar (para el informe)
Señal del colector del BJT (`c`), salida amplificada del shunt, pulsos del encoder (`enc`), PWM (`pwm`), compuerta (`gate`) y `vctrl`.

## Para el video (3 a 5 min)
Mostrar: operación normal, objeto (velocidad reducida), cubierta abierta, una protección con alarma y reset.
