# Multisim: un archivo .ms14 por bloque (abrir con doble clic, luego Run)
Cada archivo trae el bloque con piezas nativas de Multisim (resistencias, transistores, op-amps, compuertas) y una fuente DC de prueba, acomodado como el esquematico de LTspice (rieles arriba y abajo).
Los 11 bloques salen con piezas nativas y acomodo ordenado (se abrieron uno por uno en Multisim para comprobarlo). El NE555 de PWM_GEN y ENCODER_FV se dibujo con sus partes internas (divisor 3 x 5k, 2 comparadores, latch con compuertas y transistor de descarga) porque el 555 nativo no esta en este paquete; esas partes estan en un cuadro aparte debajo del bloque. Si falta una pieza en Multisim se puede crear con el Component Wizard.
El circuito completo (todos los bloques juntos) y su simulacion estan en LTspice: 2_LTspice\SISTEMA_COMPLETO.asc.
Resultados por bloque en el motor de Multisim (regulador 4.96-5.10 V, sensor, logica 16/16, sobrecorriente 0.64-0.72 A, PWM 6.8 kHz, encoder 1.1 mV/Hz): coinciden con LTspice.

Para ver la simulacion dentro de Multisim: conectar un osciloscopio (Simulate > Instruments) al nodo de salida (pwm, vspd, setn, etc.) y pulsar Run.

SISTEMA_COMPLETO.ms14: los 11 bloques juntos en una sola hoja (una fila, de izquierda a derecha: regulador, sensor, sobrecorriente, temperatura, logica, alarma, potencia, PWM, error, referencia, encoder), con tres rieles compartidos (v5 arriba, vm arriba, GND abajo) y las senales entre bloques con cable. Trae fuente de 12 V y entradas de prueba fijas (E y G en 1, objeto presente, NTC a 25 C). SISTEMA_COMPLETO_multisim.png es la hoja completa en imagen. Esta version (31/10/2026) se genero y luego se ordeno a mano en Multisim: resistencias y capacitores en horizontal, los cables de alimentacion de los amplificadores y compuertas separados para que ningun cable quede encima de otro, y ya incluye el LED de la banda. Las fuentes de prueba Ve, Vg, Vr y Venc (entradas de prueba) estan debajo de la hoja, fuera del marco blanco; baja con la barra de desplazamiento para verlas.

Nota sobre el dibujo: Multisim traza los cables solo (los dos programas se generan con el mismo circuito), por eso todavia hay cables largos que se cruzan. Las fuentes de prueba V12 e Iph estan a la izquierda de la hoja. Para leer el circuito con calma usar los dibujos de LTspice (2_LTspice y 4_Documentacion\img); los de Multisim sirven para simular. Venc (encoder) aparece como fuente senoidal de 5 kHz: para probar pulsos, cambiarla en sus propiedades a fuente de pulsos.

Visibilidad: los cables de SISTEMA_COMPLETO.ms14 son finos (ancho 1) y no llevan el nombre de la red escrito (eso hacia lento a Multisim). Para saber a donde va un cable, haz clic en el: se resalta. Se puede cambiar en Opciones > Propiedades de la hoja > Circuito (ancho del cable y mostrar nombres de red). Los nombres de red de la hoja completa llevan el bloque como prefijo (log_, pot_, ala_...); v5, vm y 0 son comunes.

La salida N de la compuerta Aa3LOG (N = M.P', velocidad normal) no tiene cable porque ninguna otra etapa la usa: la velocidad normal es lo que queda cuando L = 0. Es una salida de la logica que pide el enunciado.

## Si Multisim va lento
- Abre los BLOQUE_*.ms14 de uno en uno; SISTEMA_COMPLETO.ms14 es muy ancho y pesa mas (carga en unos 70 segundos).
- Los archivos ya no llevan el nombre de red escrito sobre cada cable (eso lo hacia lento).
- Si Multisim se cierra solo al crear un cable en SISTEMA_COMPLETO.ms14, es un fallo interno conocido (Od101dll.dll); guarda con Ctrl+S antes de tocar nada.
- En Multisim: desactiva el autoguardado (Options > Global Options > Save) y cierra Grapher y las demas hojas.

## LED de la banda
En BLOQUE_POTENCIA y al final (derecha) de SISTEMA_COMPLETO hay un LED (Dbanda) con resistencia de 1 kohm (Rbanda) en paralelo con el motor (Rmot). LED encendido = el motor recibe corriente = la banda esta funcionando. Con el PWM mas alto, brilla mas.
