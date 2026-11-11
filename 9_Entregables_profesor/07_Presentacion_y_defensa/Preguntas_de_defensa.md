# Preguntas posibles en la defensa (con respuesta corta)

Las respuestas salen del diseño y de la simulación. En la defensa conviene decir también el valor que se midió en la máquina.

## Regulador y diodos
1. **¿Por qué el diodo 1N4007 en la entrada?** Protege si se conecta la fuente al revés: el diodo no conduce y no pasa corriente. Soporta 1 A.
2. **¿Cómo funciona el regulador?** El Zener fija 5.6 V en la base del BD139; el transistor es un seguidor de emisor, así que la salida es el Zener menos VBE (≈ 4.9 V).
3. **¿Cuánta potencia disipa el BD139?** En el peor caso (13 V y 120 mA): (13 − 4.9) × 0.12 ≈ 0.97 W. Por eso lleva disipador.
4. **¿Para qué el trimpot de 100 Ω con el Zener?** Para corregir la tolerancia del Zener y dejar la salida en 5 V ± 5 %.
5. **¿Por qué el diodo 1N5819 en el motor?** El motor es inductivo: al apagar el MOSFET la corriente tiene que seguir circulando. El diodo Schottky la recircula y protege el MOSFET.

## Amplificadores
6. **¿Qué ganancia tiene el amplificador BJT y por qué?** Av = −Rc/(RE + re) = −680/(150 + 21) ≈ −4. La resistencia RE sin puentear estabiliza la ganancia.
7. **¿Dónde está el punto Q?** Sin objeto, Ic ≈ 1.2 mA y Vc ≈ 4.2 V; con objeto, Vc ≈ 2.9 V. No llega a saturación.
8. **¿Para qué la histéresis del comparador?** Para que el ruido o una señal lenta no haga oscilar la salida. Se hace con una resistencia de 220 kΩ de la salida al umbral.
9. **¿Cómo se amplifica la señal del shunt?** Con un LM358 no inversor: ganancia 1 + 6.8k/1k = 7.8. Después hay un detector de picos y un filtro (≈ 0.1 s) para ignorar el arranque.
10. **¿Cómo se regula el umbral térmico?** Con un trimpot en el divisor de referencia del comparador, entre 44 y 57 °C aproximadamente.

## Lógica
11. **¿Cuáles son las funciones lógicas?** M = E·G·F', N = M·P', L = M·P, A = F.
12. **¿Cómo se guarda la falla?** Con un pestillo hecho con compuertas NAND 74HC00. La señal setn (activa en bajo, de corriente o temperatura) lo activa y solo el reset lo borra.
13. **¿Qué pasa si se pulsa el reset con la falla todavía presente?** No pasa nada: el reset solo actúa si ya desapareció la causa (reset_n = NAND(rst, setn)).
14. **¿Por qué dos inversores Schmitt por entrada?** Para limpiar la señal (rebotes del interruptor) y dejarla en lógica positiva.
15. **¿Hay entradas flotantes?** No: cada entrada tiene resistencia a tierra o pull-up.
16. **¿Quién tiene prioridad, la seguridad o el PWM?** La seguridad: la AND del bloque de potencia deja pasar el PWM solo si M = 1.

## PWM, potencia y lazo
17. **¿Cómo se genera el PWM?** Un 555 astable genera una rampa (1.67–3.33 V) y un LM393 la compara con vctrl. f ≈ 6.9 kHz.
18. **¿Por qué un MOSFET y qué pasa si falla el 5 V?** Es un IRFZ44N de canal N. Si falla el 5 V la compuerta queda a 0 V y se apaga.
19. **¿Cómo se mide la velocidad?** Un optointerruptor con un disco de 20 ranuras da pulsos; un 555 monoestable (220 µs) y un filtro RC los convierten en voltaje: 1.1 mV por Hz.
20. **¿Cómo se cierra el lazo?** vctrl = 10 × (vref − vspd) + 2.6 V. Si la velocidad baja, el error sube y el PWM se alarga. Sin integrador queda un error pequeño (2 % en simulación).
21. **¿Cómo se logra la velocidad reducida?** Q5 pone un segundo trimpot en paralelo en el divisor de referencia, y vref baja a ≈ 49 %.

## Pruebas y seguridad
22. **¿Cómo probaron la sobrecorriente sin dañar el motor?** Con el método controlado de la Guía de pruebas (límite de corriente en la fuente y sin bloquear el motor).
23. **¿Qué diferencia hay entre simulación y medición?** Se explican con el motor real (que no es el modelo) y con la tolerancia de los componentes; por eso se calibran los trimpots.
24. **¿Qué se cambió durante el proyecto?** Se reemplazó el LM2907 por un 555 monoestable; se eliminó la modulación del LED IR; el MOSFET se excita con un par complementario; el reset tiene versión manual y automática.
25. **¿Por qué no se usa protoboard en el producto final?** El enunciado lo pide: el montaje final debe ir soldado en placa perforada o PCB. La protoboard se usó para armar y probar cada bloque.
