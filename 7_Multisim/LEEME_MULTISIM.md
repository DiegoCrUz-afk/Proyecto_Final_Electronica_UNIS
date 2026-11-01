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

## Cambio del 31/10/2026: sin Cac
Se quito el capacitor Cac (1 uF) y la resistencia de prueba Rtin (100 Meg a tierra) de SISTEMA_COMPLETO.ms14 y de BLOQUE_SENSOR_IR.ms14. Cac solo era una entrada de prueba AC: su otra pata (tin) no iba a ningun lado, y en la maquina real el fototransistor entra directo al nodo b. Se comprobo con la lista de conexiones de Multisim (report_netlist) que lo unico que cambia es que desaparecen esas dos piezas. La version nueva tambien esta como SISTEMA_COMPLETO_corregido_v7.ms14 en la carpeta de pruebas.

## Cambio del 01/11/2026: diodo de entrada y Cin en SISTEMA_COMPLETO.ms14
La hoja completa ahora lleva el diodo de entrada `Din` (D1N4007, como los demas diodos usa la plantilla 1N4001GP con el nombre del proyecto) y `Cin` (1000 uF): V12 (+) -> Din -> vm, y Cin entre vm y tierra. Estan abajo a la izquierda, junto a V12. Solo cambian 3 redes de 99 (la nueva `vin`, `vm` y tierra). El respaldo de la hoja anterior esta en C:\ms_work\respaldo_antes_Din_Cin. Los BLOQUE_*.ms14 no cambian (el diodo y Cin son de la entrada, no del regulador).
Las piezas que SOLO sirven para simular (fuentes V12, Ve, Vg, Vr, Venc, Iph; Rn = NTC fijo; Rmot = motor fijo; Rbanda + Dbanda = LED de banda; 3 Rz de 1 mohm; piezas internas de los 2 NE555) no son parte del circuito real; el LED de banda solo existe en Multisim.

## SISTEMA_SOLO_CIRCUITO.ms14 (01/11/2026)
Es el circuito completo SIN piezas de simulacion, igual que en el 3D y en `2_LTspice\SISTEMA_SOLO_CIRCUITO.asc`: no lleva fuentes (V12, Ve, Vg, Vr, Venc, Iph), NTC fijo, motor fijo, LED de banda ni las 3 resistencias de 1 mohm. Lleva el diodo de entrada Din y Cin con su tierra, y los dos NE555 son piezas LM555CM reales (U1 = generador de PWM, U2 = encoder), ya cableados. No sirve para simular el sistema entero; para eso esta `SISTEMA_COMPLETO.ms14` (y LTspice).
Los puntos libres donde se conectan las cosas de afuera llevan un texto: Interruptor E, Cubierta G, Boton de reset R, NTC, Fototransistor TCRT5000 (sus dos extremos) y Entrada 12 V (jack). Tambien estan marcadas las salidas que no se usan: N de la logica (Aa3LOG, 1Y) y OUT del 555 del PWM (U1, pata 3). El motor (MOTOR_NEGATIVO, red dm) y la salida del encoder (ENCODER_SALIDA, red enc) tambien quedan como puntos libres, sin texto.
Como se comprobo: con la lista de conexiones de Multisim, sus 79 redes son iguales a las 82 redes de LTspice (`SISTEMA_SOLO_CIRCUITO.asc`); las 3 de LTspice que no aparecen son patas sueltas a proposito (Din A, Aa3LOG 1Y, U1 OUT). Ningun cable pasa sobre una pata de otra red ni queda encima de otro cable. NO se simulo en el motor de Multisim. Abre en cerca de 70 segundos.
