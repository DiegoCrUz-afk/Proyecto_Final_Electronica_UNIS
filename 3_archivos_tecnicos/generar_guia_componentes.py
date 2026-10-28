"""Genera 4_Documentacion/Guia_de_componentes.html: que es cada pieza de los esquematicos y para que sirve. Uso: python generar_guia_componentes.py"""
import html
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "4_Documentacion", "Guia_de_componentes.html")

LEER = [
    ("v5", "Riel de +5 V (lo genera el bloque regulador). Casi todo el circuito de control se alimenta de aquí."),
    ("vm", "Riel de +12 V que viene de la fuente (después del diodo). Alimenta el motor, la alarma y algunos amplificadores."),
    ("0 / GND", "Tierra, el punto de 0 V. Es el símbolo de tres rayas. Todas las tierras están unidas."),
    ("Etiqueta azul (nombre de red)", "Dos puntos con el mismo nombre están conectados aunque no haya un cable dibujado entre ellos. En la hoja completa de LTspice las señales entre bloques ya van con cable y la etiqueta queda solo para nombrarlas."),
    ("Compuertas lógicas en Multisim", "Las compuertas (4069, 4081, 4071) no muestran sus patas de alimentación: Multisim las alimenta solas con 5 V. No es una conexión que falte."),
    ("El 555 en Multisim", "Multisim no trae el 555 en este equipo, así que se dibujó con sus partes internas: 3 resistencias de 5 k, 2 comparadores, un pestillo con compuertas y un transistor que descarga el condensador. En LTspice es un solo bloque NE555."),
    ("Seguidores en Multisim", "Algunos op-amps que en LTspice tienen la salida unida a la entrada llevan una resistencia de 1 mΩ (Rz...) para poder dibujar el cable. No cambia nada."),
]

TIPOS = [
    ("Resistencia (R)", "Limita la corriente o forma divisores de voltaje. Se mide en ohms (Ω)."),
    ("Condensador (C)", "Guarda carga: filtra ruido, retrasa señales o fija tiempos. El electrolítico (con +) tiene polaridad."),
    ("Diodo (D)", "Deja pasar la corriente en un solo sentido. El Zener fija un voltaje; el LED da luz."),
    ("Transistor (Q)", "Interruptor o amplificador controlado por una pata (base o compuerta)."),
    ("Op-amp / comparador (X o U)", "Amplificador (LM358) o comparador (LM393): dice cuál de dos voltajes es mayor."),
    ("Compuerta (A o X)", "Lógica digital: AND, NAND, inversor. Trabaja con 0 V (0) y 5 V (1)."),
    ("Trimpot", "Resistencia ajustable con tornillo. En los esquemáticos aparece como dos resistencias (Rp1 y Rp2) con el cursor en medio."),
]

BLOQUES = [
    ("1 · Regulador de 5 V (REG5V)", "Convierte los 12 V de la fuente en 5 V estables para el control.", [
        ("Rz", "Resistencia 510 Ω", "Da corriente al Zener y a la base del transistor."),
        ("DZ", "Diodo Zener 1N4734 (5.6 V)", "Fija 5.6 V en la base de Q1."),
        ("Rtr", "Resistencia 10 Ω (en el diseño, trimpot de 100 Ω)", "Sube unos mV la salida para llegar a 5.0 V."),
        ("Q1", "Transistor BD139 (NPN de potencia)", "Seguidor de emisor: la salida es 5.6 V − 0.7 V = 4.9 V y entrega la corriente."),
        ("Cout", "Electrolítico 100 µF", "Estabiliza la salida cuando cambia el consumo."),
        ("C2", "Cerámico 100 nF", "Filtra ruido de alta frecuencia."),
    ]),
    ("2 · Sensor óptico infrarrojo (SENSOR_IR)", "Detecta si hay un objeto sobre la banda y entrega p = 1 cuando lo hay.", [
        ("Rled + Dled", "270 Ω + LED infrarrojo", "El LED del sensor TCRT5000 ilumina el objeto; Rled limita su corriente (~14 mA)."),
        ("(fototransistor)", "Parte del TCRT5000, externo", "Recibe el reflejo. Su corriente entra a la base de Q2 (nodo b)."),
        ("R1, R2", "47 kΩ y 10 kΩ", "Polarizan la base de Q2."),
        ("Cac", "Condensador 1 µF", "Deja pasar los cambios de la señal y bloquea la luz ambiente constante."),
        ("Q2", "Transistor 2N3904", "Amplifica la señal del fototransistor (emisor común, ganancia ≈ 4)."),
        ("RE, Rc", "150 Ω y 680 Ω", "Fijan la ganancia de Q2."),
        ("Ra, Rp1, Rp2, Rb", "10 k, trimpot 10 k, 26.8 k", "Divisor que crea el umbral del comparador; el trimpot lo ajusta."),
        ("Xu1", "Comparador LM393", "Compara la señal de Q2 con el umbral y da p = 1 con objeto."),
        ("Rpu", "10 kΩ", "Pull-up: sube la salida a 5 V cuando el LM393 no la baja."),
        ("Rh", "220 kΩ", "Histéresis: evita que p parpadee cerca del umbral."),
    ]),
    ("3 · Sobrecorriente (SOBRECORRIENTE)", "Vigila la corriente del motor; si sube de ~0.67 A baja setn (falla).", [
        ("Xu2", "Amplificador LM358", "Amplifica 7.8 veces el voltaje del shunt (nodo sh)."),
        ("Rg, Rf", "1 kΩ y 6.8 kΩ", "Fijan la ganancia 1 + 6.8k/1k = 7.8."),
        ("D1, Cpk, Rbl", "Diodo 1N4148, 100 nF, 22 kΩ", "Detector de picos: guarda el valor máximo de la corriente."),
        ("Rd, Cd", "10 kΩ y 10 µF", "Retardo de ~0.1 s: el arranque del motor no dispara la falla, una sobrecarga sostenida sí."),
        ("Ra, Rp1, Rp2, Rb", "10 k, trimpot 10 k, 10 k", "Referencia ajustable (ref) para el disparo."),
        ("Xu3", "Comparador LM393", "Si dl supera ref, baja setn."),
    ]),
    ("4 · Sobretemperatura (TEMPERATURA)", "Si el NTC se calienta (45 a 55 °C) baja setn.", [
        ("NTC (externo)", "Termistor 10 kΩ", "Baja su resistencia al calentarse; va de v5 a tnode."),
        ("Rfix", "10 kΩ", "Completa el divisor con el NTC: tnode sube al calentarse."),
        ("Ra, Rp1, Rp2, Rb", "22 k, trimpot 10 k, 68 k", "Referencia ajustable (temperatura de disparo)."),
        ("Rh", "1 MΩ", "Histéresis de ~2.6 °C."),
        ("Xu4", "Comparador LM393", "Si tnode supera ref, baja setn."),
    ]),
    ("5 · Lógica (LOGICA)", "Decide si el motor puede andar (M), si hay falla (F) y enciende N, L y A.", [
        ("Rpe, Rpg, Rpr", "10 kΩ a tierra", "Pull-down: si el cable se rompe la entrada queda en 0 (seguro)."),
        ("Rse/Cef, Rsg/Cgf, Rsr/Crf", "10 kΩ + 100 nF", "Antirrebote de 1 ms para E, G y reset."),
        ("Xi1 … Xi6", "Inversores Schmitt 74HC14 (dibujados 4069 en Multisim)", "Dos seguidos dejan la señal limpia."),
        ("Cpor, Rpor, Dpor", "1 µF, 47 kΩ, 1N4148", "Reset automático al encender."),
        ("Rsn", "10 kΩ", "Mantiene setn en 1 cuando nadie la baja."),
        ("Xg1, Xg2, Xg3", "NAND 74HC00", "Pestillo: F recuerda la falla hasta pulsar reset."),
        ("Xg4", "NAND 74HC00", "Obtiene P' (objeto negado)."),
        ("Xa1 … Xa4", "AND 74HC08", "Calculan M = E·G·F', N = M·P', L = M·P, A = F."),
    ]),
    ("6 · Generador de PWM (PWM_GEN)", "Genera pulsos de ~7 kHz; el ancho depende de vctrl.", [
        ("X5 (NE555)", "Temporizador 555", "Oscila y hace subir y bajar el voltaje del nodo tri (rampa 1.7 a 3.3 V)."),
        ("Ra5, Rb5, Ct", "1 k, 10 k, 10 nF", "Fijan la frecuencia: f = 1.44 / ((Ra+2Rb)·Ct) ≈ 6.9 kHz."),
        ("Ccv", "10 nF", "Filtra el pin de control del 555."),
        ("Xu6", "Comparador LM393", "pwm = 1 mientras vctrl > tri: a mayor vctrl, pulsos más anchos."),
        ("Rpu", "10 kΩ", "Pull-up de la salida pwm."),
    ]),
    ("7 · Seguridad, excitador y MOSFET (POTENCIA)", "Mueve el motor con el PWM, pero solo si M = 1.", [
        ("Xa5", "AND 74HC08", "pwmg = pwm · M: la seguridad manda sobre el PWM."),
        ("Q3 (2N3904) y Q4 (2N3906)", "Par complementario", "Cargan y descargan rápido la compuerta del MOSFET."),
        ("Rg", "47 Ω", "Limita la corriente de la compuerta."),
        ("Rpd", "10 kΩ", "Pull-down: con el control apagado el MOSFET queda apagado."),
        ("M1", "MOSFET IRFZ44N", "Interruptor de potencia del motor."),
        ("Dfw", "Diodo Schottky 1N5819", "Volante: absorbe el pico del motor al apagar M1."),
        ("Rsh", "0.5 Ω, 5 W (shunt)", "Mide la corriente del motor: sh = corriente × 0.5 Ω."),
    ]),
    ("8 · Encoder y convertidor frecuencia-voltaje (ENCODER_FV)", "Convierte los pulsos del disco en un voltaje proporcional a la velocidad (1.1 mV por Hz).", [
        ("Rled + Dled", "220 Ω + LED", "LED del optointerruptor."),
        ("Rpe", "10 kΩ", "Pull-up del fototransistor del optointerruptor (nodo enc)."),
        ("Ru1, Ru2", "10 kΩ + 10 kΩ", "Umbral del comparador (eref = 2.5 V)."),
        ("Xu7", "Comparador LM393", "Limpia los pulsos del encoder."),
        ("Rpq, Rhe", "10 kΩ y 1 MΩ", "Pull-up e histéresis del comparador."),
        ("Cd, Rtg, Dcl", "1 nF, 10 kΩ, 1N4148", "Derivador: da un pulso corto en cada flanco; el diodo protege el 555."),
        ("X7 (NE555)", "555 monoestable", "Un pulso fijo de 220 µs por cada pulso del encoder."),
        ("Rt7, Ct7, Ccvm", "20 k, 10 nF, 10 nF", "Fijan el ancho del pulso: 1.1·Rt·Ct = 220 µs."),
        ("Xb1", "Compuerta buffer", "Pulsos limpios de 0 a 5 V."),
        ("Rfv, Cfv, Rfv2, Cfv2", "10 k + 1 µF (dos veces)", "Filtro doble: promedia los pulsos y da vspd (voltaje de velocidad)."),
    ]),
    ("9 · Referencia de velocidad (REFVEL)", "Da el voltaje de velocidad deseada (vref); con L = 1 baja a la mitad.", [
        ("Rt", "68 kΩ", "Parte alta del divisor."),
        ("Rp1", "Trimpot 10 kΩ", "Ajusta la velocidad normal (~0.53 V)."),
        ("Rb5, Q5", "10 kΩ y 2N3904", "Con L = 1, Q5 conduce y conecta Rp2."),
        ("Rp2", "Trimpot 10 kΩ", "Ajusta la velocidad reducida (50 % de la normal)."),
        ("Cr", "100 nF", "Filtra vref."),
    ]),
    ("10 · Amplificador de error (ERROR_AMP)", "Compara velocidad deseada y real: vctrl = 10·(vref − vspd) + Voff.", [
        ("Xbr, Xbs, Xbo", "Op-amps LM358 como seguidores", "Aíslan vref, vspd y Voff (no cargan las otras etapas)."),
        ("Rv1, Rv2, Cv", "4.7 k, 5.1 k, 100 nF", "Crean Voff ≈ 2.6 V, el punto de partida del PWM."),
        ("R1, R3", "10 kΩ", "Entradas del restador."),
        ("R4, Rf6", "100 kΩ (= Kerr·10 k)", "Fijan la ganancia 10."),
        ("Cf6", "10 nF", "Estabiliza el amplificador."),
        ("Xu2b", "Op-amp LM358", "Resta y multiplica: da oa."),
        ("Ro, Cvc", "1 kΩ y 100 nF", "Filtran la salida vctrl."),
    ]),
    ("11 · Alarma (ALARMA)", "Cuando hay falla (F = 1) enciende un LED y un buzzer.", [
        ("Rl, Dl", "470 Ω + LED rojo", "Indicador luminoso de falla."),
        ("Rb", "1 kΩ", "Limita la corriente de base de Q6."),
        ("Q6", "Transistor 2N3904", "Interruptor que enciende el buzzer."),
        ("Rbz", "400 Ω (en la simulación)", "Representa el buzzer activo de 12 V (~30 mA)."),
    ]),
]


def tabla(rows):
    h = "<table><tr><th>Pieza</th><th>Qué es</th><th>Para qué sirve</th></tr>"
    for a, b, c in rows:
        h += "<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % (html.escape(a), html.escape(b), html.escape(c))
    return h + "</table>"


def main():
    p = ["<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Guía de componentes</title><style>"
         "body{font-family:Arial,sans-serif;max-width:980px;margin:24px auto;padding:0 16px;color:#222;line-height:1.45}"
         "h1{font-size:24px}h2{font-size:18px;margin-top:30px;border-bottom:2px solid #444;padding-bottom:3px}"
         "table{border-collapse:collapse;width:100%;margin:8px 0}td,th{border:1px solid #bbb;padding:5px 8px;text-align:left;vertical-align:top;font-size:14px}"
         "th{background:#eee}.n{color:#555;font-size:14px}</style></head><body>",
         "<h1>Guía de componentes de la miniestación</h1>",
         "<p class='n'>Qué es cada pieza de los esquemáticos (LTspice y Multisim) y para qué sirve. Los nombres (R1, Q2, Xu1...) son los mismos que se ven en los dibujos; en la hoja completa llevan el sufijo del bloque (por ejemplo Ra_SEN en LTspice o RaSEN en Multisim).</p>",
         "<h2>Cómo leer los esquemáticos</h2><table><tr><th>Lo que ves</th><th>Qué significa</th></tr>"]
    for a, b in LEER:
        p.append("<tr><td><b>%s</b></td><td>%s</td></tr>" % (html.escape(a), html.escape(b)))
    p.append("</table><h2>Tipos de pieza</h2><table><tr><th>Pieza</th><th>Qué hace</th></tr>")
    for a, b in TIPOS:
        p.append("<tr><td><b>%s</b></td><td>%s</td></tr>" % (html.escape(a), html.escape(b)))
    p.append("</table>")
    for t, d, rows in BLOQUES:
        p.append("<h2>%s</h2><p>%s</p>%s" % (html.escape(t), html.escape(d), tabla(rows)))
    p.append("<h2>Fuente y motor (solo para simular)</h2>" + tabla([
        ("V12, D1, Cin", "Fuente de 12 V, diodo 1N4007 y condensador 1000 µF", "Alimentación de entrada; el diodo protege contra polaridad inversa."),
        ("Ve, Vg, Vr", "Fuentes de prueba", "Simulan el interruptor E, la cubierta G y el botón de reset."),
        ("Iph, Bn, Vtc", "Fuentes de prueba", "Simulan el fototransistor (objeto) y el NTC (temperatura)."),
        ("Lm, Rm, Eb, Cw, Bw, Vtl", "Modelo del motor", "Inductancia, resistencia, fuerza contraelectromotriz, inercia y carga del motor supuesto."),
    ]))
    p.append("</body></html>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print("creado", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
