# Guion del video (3 a 5 minutos)

El enunciado pide: demostrar los modos de operación y **al menos una protección**. Este guion dura unos 4 minutos. Se graba con el celular, con la máquina armada y el osciloscopio o el Analog Discovery a la vista.

Antes de grabar: fuente de 12 V con límite de corriente (por ejemplo 0.6 A), v5 medido entre 4.75 y 5.25 V, trimpots ajustados, un objeto de prueba a la mano y la cubierta puesta (el micro-switch presionado).

| Tiempo | Qué se ve | Qué se dice |
|---|---|---|
| 0:00 – 0:20 | La máquina completa, de lejos y luego de cerca | "Soy Diego Cruz. Esta es mi miniestación industrial: una banda que detecta objetos, regula su velocidad y se protege sola. No usa microcontroladores." |
| 0:20 – 0:45 | Las protoboards y el diagrama de bloques en una hoja | "Tiene 11 bloques: regulador de 5 V, sensor infrarrojo, lógica con compuertas, PWM con MOSFET, encoder, lazo de velocidad y protecciones." |
| 0:45 – 1:15 | Multímetro en v5 y la fuente de 12 V | "Primero la regulación: con 12 V de entrada la salida es de (valor medido) V." Cambiar la fuente a 11 V y 13 V y mostrar el valor. |
| 1:15 – 1:45 | Interruptor E arriba; la banda arranca | "Con el interruptor E activado, la cubierta cerrada y sin falla, el motor arranca a velocidad normal." Mostrar la velocidad (vspd o rpm). |
| 1:45 – 2:15 | Pasar un objeto frente al sensor | "Cuando el sensor detecta un objeto, la lógica cambia a velocidad reducida (entre 40 y 60 % de la normal)." Mostrar el cambio de velocidad. |
| 2:15 – 2:30 | Pantalla del osciloscopio: PWM y compuerta | "Esta es la señal PWM y la compuerta del MOSFET." |
| 2:30 – 2:55 | Abrir la cubierta (soltar el micro-switch) | "Seguridad de cubierta: al abrirla, el motor se detiene aunque el lazo pida más potencia. Al cerrarla, reanuda." |
| 2:55 – 3:40 | **Protección:** provocar la falla de forma controlada (por ejemplo, calentar el NTC con la mano o con el aire tibio del secador; nunca llama ni bloquear el motor) | "Cuando el NTC pasa el umbral de temperatura, se guarda la falla: el motor se detiene y suenan el buzzer y el LED." |
| 3:40 – 4:10 | Quitar la causa, mostrar que la alarma sigue; pulsar reset | "Aunque ya se enfrió, la falla sigue guardada. Solo con el botón de reset se apaga y la máquina vuelve a andar." |
| 4:10 – 4:30 | Cierre | "Todo el diseño está calculado, simulado en LTspice y comprobado con mediciones. Gracias." |

Consejos:
- Grabar en horizontal y con buena luz. Si se equivoca, repetir solo esa escena.
- Para la protección de corriente (opcional, si hay tiempo): usar el método controlado de la Guía de pruebas, nunca bloquear el motor a propósito.
- Mostrar números reales medidos (los de la Guía de pruebas), no solo los de la simulación.
