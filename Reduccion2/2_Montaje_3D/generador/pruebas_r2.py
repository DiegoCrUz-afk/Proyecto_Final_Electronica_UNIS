"""Pruebas de cada bloque de la Reduccion 2 (una sola fuente de verdad: las usan el 3D, la guia de pruebas y el verificador de simulacion).
Cada prueba: mide, sirve, cond, red, black, mode, exp (+tabla), pasos (si no da, en orden), fuente, valida, sim (comprobaciones contra LTspice).
red/black: ["U1","8"] (pieza y pata) | {"rail":"v5","board":"B"} (agujero del riel) | {"txt":"..."} (algo fuera de la placa) | None (negro = riel GND de la placa de la roja)."""

BLOQUES = ["ALIM", "SENSOR_IR", "ENTRADAS", "PESTILLO", "LOGICA", "POTENCIA", "LED_ROJO"]
M = []


def m(id_, blk, t, red, black, mode, mide, sirve, cond, exp, pasos, fuente, tabla=None, valida=True, sim=None, rieles=False, nova=""):
    M.append(dict(id=id_, grp=blk, blk=blk, t=t, red=red, black=black, mode=mode, mide=mide, sirve=sirve, cond=cond, exp=exp, tabla=tabla,
                  pasos=pasos, bad=" ".join("%d) %s" % (i + 1, p) for i, p in enumerate(pasos)), fuente=fuente, valida=valida, sim=sim or [], rieles=rieles, nova=nova))


PASOS_CORTO = ["Cerca de 0 Ω: hay un corto. NO conectes la fuente.", "Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).",
               "Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba."]


def resist(id_, blk, red, extra=""):
    m(id_, blk, "Resistencia entre 5 V y GND (sin energía)", red, None, "Ω (resistencia)",
      "La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.",
      "Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.",
      "Fuente de 5 V DESCONECTADA. El bloque recién armado." + extra,
      "Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).", PASOS_CORTO, "regla de seguridad; valor exacto a medir")


# ---------------- 0 Alimentación de 5 V (placa A) ----------------
resist("m_r0", "ALIM", ["ENT.J1", "+5V"], " Todavía sin sensor, chips ni motor.")
m("m_vin", "ALIM", "5 V que entran (cargador USB o power bank)", ["ENT.J1", "+5V"], ["ENT.J1", "GND"], "V DC",
  "El voltaje que entrega la fuente de 5 V.", "Confirma que la fuente alimenta bien antes de armar lo demás.",
  "Fuente conectada y encendida. Nada más armado.", "5.0 V (entre 4.75 y 5.25 V)",
  ["Si marca 0 V: fuente apagada, cable USB flojo o polaridad invertida (si marca −5 V, están al revés + y −).", "Menos de 4.75 V: la fuente no alcanza; prueba otro cargador o power bank."], "especificación del enunciado (5 V ± 5 %)")
m("m_cin", "ALIM", "5 V en el condensador de 1000 µF", ["ENT.Cin", "+"], ["ENT.Cin", "-"], "V DC",
  "El voltaje en el condensador grande de la entrada.", "Confirma que el condensador está bien puesto y filtra la fuente.",
  "Fuente conectada.", "5.0 V, igual que la fuente (4.75 a 5.25 V)",
  ["Menos que la fuente: el condensador está al revés (la franja marca el −, y va a GND).", "Revisa que el cable del + llegue al riel de 5 V."], "igual que la fuente")
for b, i in (("B", 1), ("C", 2)):
    m("m_rail" + b, "ALIM", "5 V llegan a la placa " + b, {"rail": "v5", "board": b}, {"rail": "0", "board": b}, "V DC",
      "El voltaje entre el riel de 5 V y el de GND de la placa " + b + ".", "Confirma que la alimentación llega a las otras placas por los puentes de riel.",
      "Fuente conectada; puentes de riel puestos.", "5.0 V (entre 4.75 y 5.25 V)",
      ["0 V: falta el puente de 5 V o de GND hacia esta placa.", "Revisa que no se hayan cruzado el riel rojo y el azul.", "Pendiente: si los rieles de en medio de la BX-4135 están partidos a la mitad, hace falta un puente por mitad."],
      "igual que la fuente", rieles=True)

# ---------------- 1 Sensor IR (placa B) ----------------
resist("m_r1", "SENSOR_IR", ["SEN.R1", "1"], " Sensor TCRT5000 sin conectar o conectado, da igual.")
m("m_vcc_U1", "SENSOR_IR", "Alimentación del LM393 (U1)", ["U1", "8"], ["U1", "4"], "V DC",
  "El voltaje entre VCC (pata 8) y GND (pata 4) del LM393.", "Confirma que el chip recibe energía.", "Fuente conectada.", "5.0 V (entre 4.75 y 5.25 V)",
  ["0 V: falta el cable de 5 V o de GND del chip.", "Revisa la muesca: la pata 1 va junto a la muesca, con el chip al revés VCC queda en GND.", "Cable flojo o agujero equivocado."], "igual que la fuente")
m("m_irled", "SENSOR_IR", "LED infrarrojo del TCRT5000", ["SEN.TCRT", "A"], ["SEN.TCRT", "K"], "V DC",
  "El voltaje en el LED infrarrojo del sensor (ánodo contra cátodo).", "Confirma que el LED del sensor está encendido (si no, el sensor no ve nada).",
  "Fuente conectada. TCRT5000 conectado.", "≈ 1.2 V (con la cámara del celular se ve una luz violeta)",
  ["5 V: no pasa corriente; A y K están al revés (confírmalo con el multímetro en modo diodo).", "0 V: falta 5 V o la resistencia Rled (270 Ω) está abierta.", "Las patas del TCRT5000 hay que confirmarlas con el multímetro."], "diseño original (no simulado en la Reducción 2)")
m("m_vb", "SENSOR_IR", "Base de Q2 (b)", ["SEN.Q2", "B"], None, "V DC",
  "El voltaje en la entrada del transistor que amplifica la señal del sensor.", "Confirma el divisor de polarización y que el sensor inyecta corriente.",
  "Fuente conectada. Primero SIN objeto y luego CON objeto frente al sensor (distancia: a medir).", "Ver tabla",
  ["0 V: falta R1 (47 kΩ) o el cable del TCRT al nodo b.", "5 V: falta R2 (10 kΩ) a GND.", "Revisa Q2: E, B, C del 2N3904 en el orden correcto."], "simulación LTspice (prueba_sensor_ir)",
  tabla=[["Sin objeto", "≈ 0.85 V"], ["Con objeto", "≈ 1.15 V"]],
  sim=[("prueba_sensor_ir", "vb_sin", 0.80, 0.90), ("prueba_sensor_ir", "vb_con", 1.10, 1.20)])
m("m_vc", "SENSOR_IR", "Colector de Q2", ["SEN.Q2", "C"], None, "V DC",
  "El voltaje en la salida del transistor amplificador.", "Confirma que el transistor amplifica: con objeto este voltaje baja.",
  "Fuente conectada. Sin objeto y con objeto.", "Ver tabla",
  ["5 V siempre: Q2 no conduce (revisa la base y el orden de patas).", "Cerca de 1 V siempre: Q2 saturado o falta la resistencia RE (150 Ω).", "Falta Rc (680 Ω)."], "simulación LTspice (prueba_sensor_ir)",
  tabla=[["Sin objeto", "≈ 4.2 V"], ["Con objeto", "≈ 2.9 V"]],
  sim=[("prueba_sensor_ir", "vc_sin", 4.10, 4.25), ("prueba_sensor_ir", "vc_con", 2.80, 2.95)])
m("m_vth", "SENSOR_IR", "Umbral del comparador (cursor del trimpot)", ["SEN.T1", "W"], None, "V DC",
  "El voltaje de referencia con el que el comparador decide si hay objeto.", "Confirma el ajuste del trimpot; debe quedar entre los dos voltajes del colector.",
  "Fuente conectada.", "≈ 3.3 V; debe quedar entre 2.9 V y 4.2 V. Gira el trimpot para ajustarlo.",
  ["0 V o 5 V fijo: el trimpot está en un extremo o falta Ra (10 kΩ) o Rb (26.8 kΩ; puedes usar 27 kΩ).", "Si el valor no cambia al girar: revisa las patas 1, W y 3 del trimpot."], "simulación LTspice (prueba_sensor_ir)",
  sim=[("prueba_sensor_ir", "vth", 3.20, 3.40)])
m("m_p", "SENSOR_IR", "p: salida del sensor (U1 pata 1)", ["U1", "1"], None, "V DC",
  "El voltaje de salida del sensor, que dice si ve un objeto o no.", "Confirma que el bloque completo funciona: 0 sin objeto, 5 con objeto.",
  "Fuente conectada. Sin objeto y con objeto.", "Ver tabla",
  ["Siempre igual: ajusta el trimpot o revisa el TCRT5000 y el cable al nodo b.", "Siempre 0 V: revisa el LM393 (pata 3 al umbral, pata 2 al colector).", "Siempre 5 V: falta la resistencia Rpu (10 kΩ) o Rh está en corto."], "simulación LTspice (prueba_sensor_ir)",
  tabla=[["Sin objeto", "≈ 0.03 V (casi 0)"], ["Con objeto", "≈ 4.9 V"]],
  sim=[("prueba_sensor_ir", "p_sin_objeto", 0.0, 0.1), ("prueba_sensor_ir", "p_con_objeto", 4.8, 5.0)])

# ---------------- 2 Entradas E, G y RESET con 74HC14 (placa B) ----------------
resist("m_r2", "ENTRADAS", ["U11", "14"], " Con el sensor ya verificado.")
m("m_vcc_U11", "ENTRADAS", "Alimentación del 74HC14 (U11)", ["U11", "14"], ["U11", "7"], "V DC",
  "El voltaje entre VCC (pata 14) y GND (pata 7).", "Confirma que el chip recibe energía.", "Fuente conectada.", "5.0 V (entre 4.75 y 5.25 V)",
  ["0 V: falta 5 V o GND del chip.", "Muesca al revés: pata 14 con GND y pata 7 con 5 V dañan el chip.", "Cable flojo."], "igual que la fuente")
SI_NO_E = ["Revisa Rpe (10 kΩ a GND) y los cables del toggle: la pata central es COM y va a 5 V.", "Revisa Rse y Cef (filtro) y los inversores de U11.", "Cable flojo o agujero equivocado."]
m("m_ein", "ENTRADAS", "E: entrada del toggle", ["ENT.TBE", "E"], None, "V DC",
  "El voltaje que llega del interruptor E.", "Confirma que el interruptor está bien cableado.", "Fuente conectada. Toggle encendido y apagado.", "Ver tabla",
  SI_NO_E, "simulación LTspice (prueba_logica: E = 1 o 0)", tabla=[["Toggle encendido", "≈ 5 V"], ["Toggle apagado", "0 V"]])
m("m_e", "ENTRADAS", "E limpio (salida del 74HC14, U11)", ["U11", "4"], None, "V DC",
  "La señal E ya limpia, después del filtro y los dos inversores.", "Confirma el filtro y el 74HC14 de esta entrada.", "Igual que arriba.", "Igual que E: 5 V encendido, 0 V apagado.",
  ["Si E llega bien pero esta no cambia: revisa Rse, Cef y las patas 1 a 4 de U11.", "Chip al revés o sin alimentación."], "simulación LTspice (prueba_logica)")
m("m_gin", "ENTRADAS", "G: micro-switch de la cubierta", ["ENT.TBG", "G"], None, "V DC",
  "El voltaje que llega del micro-switch de la cubierta.", "Confirma que el micro-switch está bien cableado.", "Fuente conectada. Palanca presionada (cubierta cerrada) y suelta.", "Ver tabla",
  ["0 V siempre: usa COM y NO (no COM y NC). Las patas del micro-switch se confirman con el multímetro.", "5 V siempre: usaste COM y NC o falta Rpg (10 kΩ a GND).", "Cable flojo."], "simulación LTspice (prueba_logica: G = 1 o 0)",
  tabla=[["Palanca presionada (cubierta cerrada)", "≈ 5 V"], ["Palanca suelta (cubierta abierta)", "0 V"]])
m("m_g", "ENTRADAS", "G limpio (U11 pata 8)", ["U11", "8"], None, "V DC",
  "La señal G ya limpia.", "Confirma el filtro y el 74HC14 de esta entrada.", "Igual que arriba.", "Igual que G.",
  ["Revisa Rsg, Cgf y las patas 9 y 8 de U11.", "Chip sin alimentación."], "simulación LTspice (prueba_logica)")
m("m_rin", "ENTRADAS", "RST: pulsador de reset", ["ENT.TBR", "RST"], None, "V DC",
  "El voltaje que llega del pulsador RESET.", "Confirma que el pulsador está bien cableado.", "Fuente conectada. Pulsador suelto y pulsado.", "Ver tabla",
  ["5 V siempre: usaste dos patas del mismo lado del pulsador (usa las de la diagonal) o falta Rpr (10 kΩ a GND).", "0 V al pulsar: revisa los cables del pulsador.", "Cable flojo."], "simulación LTspice (prueba_logica: RESET)",
  tabla=[["Suelto", "0 V"], ["Pulsado", "≈ 5 V"]])
m("m_rst", "ENTRADAS", "RST limpio (U11 pata 12)", ["U11", "12"], None, "V DC",
  "La señal de reset ya limpia.", "Confirma el filtro y el 74HC14 de esta entrada.", "Igual que arriba.", "0 V en reposo; ≈ 5 V mientras pulsas (también un pulso corto al encender).",
  ["Revisa Rsr, Crf y las patas 13 y 12 de U11.", "Chip sin alimentación."], "simulación LTspice (prueba_logica)")

# ---------------- 3 Pestillo de falla con 74HC00 (placa C) ----------------
resist("m_r3", "PESTILLO", ["U8", "14"], " Bloques anteriores verificados.")
m("m_vcc_U8", "PESTILLO", "Alimentación del 74HC00 (U8)", ["U8", "14"], ["U8", "7"], "V DC",
  "El voltaje entre VCC (pata 14) y GND (pata 7).", "Confirma que el chip recibe energía.", "Fuente conectada.", "5.0 V (entre 4.75 y 5.25 V)",
  ["0 V: falta 5 V o GND del chip.", "Revisa la muesca (chip al revés).", "Cable flojo."], "igual que la fuente")
m("m_setn", "PESTILLO", "setn: señal de falla (activa en bajo)", ["LOG.Rsn", "2"], None, "V DC",
  "El voltaje de la línea que avisa una falla (0 V = hay falla).", "Confirma el pulsador FALLA y su resistencia de 10 kΩ a 5 V.",
  "Fuente conectada. Pulsador FALLA suelto y pulsado.", "Ver tabla",
  ["0 V siempre: el pulsador FALLA está en corto o mal puesto (va entre setn y GND).", "5 V al pulsar: cable del pulsador flojo.", "Falta Rsn (10 kΩ a 5 V)."], "simulación LTspice (prueba_logica)",
  tabla=[["FALLA suelto", "5 V"], ["FALLA pulsado", "≈ 0 V"]],
  sim=[("prueba_logica", "setn_l1_falla_pulsada", 0.0, 0.1), ("prueba_logica", "setn_l3_falla_suelta_sin_reset", 4.9, 5.1)])
m("m_f", "PESTILLO", "F: la falla guardada (U8 pata 6)", ["U8", "6"], None, "V DC",
  "Si el pestillo tiene una falla guardada (5 V) o no (0 V).", "Confirma que la falla se guarda y que solo el RESET la borra.",
  "Fuente conectada. Sigue la secuencia de la tabla en orden.", "Ver tabla",
  ["No se guarda al soltar FALLA: revisa las compuertas de U8 (patas 4 a 6 y 8 a 10).", "No se borra con RESET: la falla sigue pulsada (el reset solo actúa si ya no hay falla).", "Siempre 5 V: revisa el reset automático (Cpor 1 µF, Rpor 47 kΩ, Dpor 1N4148)."], "simulación LTspice (prueba_logica)",
  tabla=[["1. Recién encendido (reset automático)", "0 V"], ["2. Pulsas FALLA y sueltas", "≈ 5 V (queda guardada)"], ["3. Pulsas RESET con FALLA todavía pulsada", "sigue ≈ 5 V"],
         ["4. Sueltas FALLA y pulsas RESET", "0 V"]])
m("m_fn", "PESTILLO", "F' (U8 pata 8): lo contrario de F", ["U8", "8"], None, "V DC",
  "La señal contraria a F: 5 V = todo bien.", "Confirma la segunda compuerta del pestillo, la que habilita el motor.",
  "Igual que la prueba anterior.", "5 V sin falla; 0 V con falla guardada.", ["Debe ser lo contrario de F; si no, revisa la compuerta de U8 que da F'."], "simulación LTspice (prueba_logica)",
  sim=[("prueba_logica", "fn_l1_falla_pulsada", 0.0, 0.1), ("prueba_logica", "fn_l4_reset_con_falla_suelta", 4.9, 5.1)])

# ---------------- 4 Lógica de decisión con 74HC08, SIN motor (placa C) ----------------
resist("m_r4", "LOGICA", ["U9", "14"], " Motor y potencia desconectados.")
m("m_vcc_U9", "LOGICA", "Alimentación del 74HC08 (U9)", ["U9", "14"], ["U9", "7"], "V DC",
  "El voltaje entre VCC (pata 14) y GND (pata 7).", "Confirma que el chip recibe energía.", "Fuente conectada. Motor desconectado.", "5.0 V (entre 4.75 y 5.25 V)",
  ["0 V: falta 5 V o GND del chip.", "Revisa la muesca (chip al revés).", "Cable flojo."], "igual que la fuente")
m("m_M", "LOGICA", "M: permiso del motor (U9 pata 6)", ["U9", "6"], None, "V DC",
  "Si la máquina tiene permiso de mover el motor.", "Confirma M = E·G·F' (el motor solo corre con E = 1, G = 1 y sin falla).",
  "Fuente conectada. MOTOR DESCONECTADO. Cambia E, G y FALLA según la tabla.", "Ver tabla",
  ["0 V con todo bien: revisa E, G y F' en la entrada de U9.", "Revisa la muesca y las patas 4 a 6 de U9.", "Cable flojo."], "simulación LTspice (prueba_logica: 16 de 16 combinaciones)",
  tabla=[["E = 1, G = 1, sin falla", "5 V"], ["E = 0, o G = 0, o hay falla", "0 V"]])
m("m_N", "LOGICA", "N: velocidad normal (U9 pata 8)", ["U9", "8"], None, "V DC",
  "Si debe correr a velocidad normal (permiso y sin objeto).", "Confirma N = M·P'.", "Motor desconectado. Con permiso (M = 5 V); sin objeto y con objeto.", "Ver tabla",
  ["Siempre 0 V: revisa p' (U8 pata 11) y U9 (patas 9, 10 y 8).", "Cable flojo."], "simulación LTspice (prueba_logica)",
  tabla=[["M = 5 V y sin objeto", "5 V"], ["M = 5 V y con objeto", "0 V"], ["M = 0 V", "0 V"]])
m("m_L", "LOGICA", "L: velocidad reducida (U9 pata 11), sin uso en el hardware", ["U9", "11"], None, "V DC",
  "Si debería ir lento (permiso y objeto).", "Confirma L = M·P. Esta salida no va a ninguna pieza; solo sirve para probar la lógica.",
  "Motor desconectado. M = 5 V; sin objeto y con objeto.", "Ver tabla",
  ["Siempre 0 V: revisa p y las patas 12, 13 y 11 de U9."], "simulación LTspice (prueba_logica)",
  tabla=[["M = 5 V y con objeto", "5 V"], ["M = 5 V y sin objeto", "0 V"], ["M = 0 V", "0 V"]])
m("m_led", "LOGICA", "LED de objeto", ["LOG.Dlo", "A"], ["LOG.Dlo", "K"], "V DC",
  "El voltaje en el LED verde de objeto (ánodo contra cátodo).", "Confirma que el LED enciende cuando el sensor ve un objeto.",
  "Fuente conectada. Sin objeto y con objeto.", "Ver tabla",
  ["Nunca enciende: LED al revés (la pata larga es el ánodo A) o Rlo (680 Ω) abierta.", "Siempre encendido: p' (U8 pata 11) siempre en 0 V; revisa el sensor.", "Cable flojo."], "simulación LTspice (prueba_logica)",
  tabla=[["Con objeto", "≈ 2.0 V (enciende, unos 4.4 mA)"], ["Sin objeto", "≈ 5 V (apagado)"]],
  sim=[("prueba_logica", "lo_a_111", 1.9, 2.1), ("prueba_logica", "lo_a_110", 4.9, 5.05)])

# ---------------- 5 Potencia con motor (placa A) ----------------
resist("m_r5", "POTENCIA", ["POT.Cb", "+"], " MOTOR DESCONECTADO (sin los cables M+ y M−).")
m("m_gate", "POTENCIA", "Compuerta del IRLZ44N (señal m)", ["POT.M1", "G"], None, "V DC",
  "El voltaje en la compuerta del MOSFET que da corriente al motor.", "Confirma que el permiso M llega al MOSFET.",
  "Fuente conectada. MOTOR DESCONECTADO. M = 0 y M = 1.", "Ver tabla",
  ["Siempre 0 V: M = 0 o el cable de m no llega desde la placa C.", "Rpd (10 kΩ a GND) no debe estar en corto.", "Revisa el orden G-D-S del IRLZ44N."], "simulación LTspice (prueba_potencia_Rs15_bjt; el chip real puede dar un poco menos)",
  tabla=[["M = 0", "0 V"], ["M = 1", "≈ 5 V"]], sim=[("prueba_potencia_Rs15_bjt", "vgate_on", 4.9, 5.1)])
m("m_qb", "POTENCIA", "Puente 2N3904: base contra emisor", ["POT.Qp", "B"], ["POT.Qp", "E"], "V DC",
  "El voltaje de la base del transistor que puentea a Rs.", "Confirma que N enciende el puente (sin objeto) y lo apaga (con objeto).",
  "Fuente conectada. MOTOR DESCONECTADO. N = 1 y N = 0.", "Ver tabla",
  ["0 V siempre: falta Rb (1 kΩ) o el cable de n desde la placa C.", "Revisa E, B y C del 2N3904.", "El 2N3904 aguanta 200 mA y el arranque pide más (ver informe): puede ser un problema con el motor puesto."], "simulación LTspice (prueba_potencia_Rs15_bjt)",
  tabla=[["N = 1 (sin objeto)", "≈ 0.9 V (entre 0.7 y 0.95 V)"], ["N = 0 (con objeto)", "≈ 0 V"]],
  sim=[("prueba_potencia_Rs15_bjt", "vbe_normal", 0.70, 0.95), ("prueba_potencia_Rs15_bjt", "vbe_lento", -0.05, 0.05)])
m("m_imot", "POTENCIA", "Corriente del motor a 5 V", ["ENT.TBM", "M+"], {"txt": "el hilo M+ del motor (no está en la placa)"}, "A DC (en serie)",
  "La corriente que realmente pide el motor Steren a 5 V.", "Con este dato se elige Rs y se decide si el 2N3904 alcanza.",
  "Fuente conectada. M = 1. El multímetro en serie: abre el cable M+ y pon el multímetro en medio.", "A medir. La simulación usa un motor SUPUESTO (12 Ω, ≈ 134 mA en marcha y ≈ 390 mA al arrancar).",
  ["Más de 200 mA al arrancar: el 2N3904 queda corto; usa un MOSFET como puente.", "Muy distinta de 134 mA: hay que reajustar Rs."], "a medir (motor real)", valida=False, nova="motor real")
m("m_dm", "POTENCIA", "dm: lado negativo del motor (contra GND)", ["POT.Dfw", "A"], None, "V DC",
  "El voltaje en el lado negativo del motor.", "Muestra cuánto voltaje pierde el motor en el MOSFET y en Rs.",
  "Fuente conectada. MOTOR CONECTADO.", "Ver tabla (motor supuesto: valores a medir con el Steren)",
  ["Siempre 5 V con M = 1: el IRLZ44N no conduce (¿es de nivel lógico?, ¿patas G-D-S al revés?).", "Mide primero la corriente del motor (prueba anterior)."], "simulación LTspice con motor SUPUESTO; NO validado con el motor real",
  tabla=[["Motor parado (M = 0)", "≈ 5 V"], ["Sin objeto (N = 1)", "≈ 0.1 V (a medir)"], ["Con objeto (N = 0)", "≈ 1.9 V (a medir; depende del motor)"]],
  valida=False, nova="motor real", sim=[("prueba_potencia_Rs15_bjt", "vdm_parado", 4.9, 5.1), ("prueba_potencia_Rs15_bjt", "vce_normal", 0.08, 0.12)])

# ---------------- 6 LED rojo y ajuste de la velocidad lenta (placa A) ----------------
resist("m_r6", "LED_ROJO", ["ALA.Rl", "1"], " Potencia y motor ya verificados.")
m("m_alled", "LED_ROJO", "LED rojo de falla", ["ALA.Dl", "A"], ["ALA.Dl", "K"], "V DC",
  "El voltaje en el LED rojo (ánodo contra cátodo).", "Confirma que la alarma luminosa enciende cuando hay una falla guardada.",
  "Fuente conectada. Sin falla y con falla guardada (pulsa FALLA y suelta).", "Ver tabla",
  ["Hay falla y no enciende: LED al revés (la pata larga es el ánodo A) o Rl (470 Ω) abierta.", "Siempre encendido: F está en 1; revisa el pestillo (bloque 3)."], "diseño original (≈ 6 mA); no simulado en la Reducción 2",
  tabla=[["Sin falla", "0 V (apagado)"], ["Con falla guardada", "≈ 2 V (enciende; a medir)"]])
m("m_rs", "LED_ROJO", "Caída en Rs (entre dm y ds)", ["POT.Rs", "1"], ["POT.Rs", "2"], "V DC",
  "El voltaje que se pierde en la resistencia Rs.", "Es lo que baja la velocidad cuando hay objeto.",
  "Fuente conectada. Motor conectado. Sin objeto y con objeto.", "Ver tabla (motor supuesto)",
  ["Siempre alta: el 2N3904 no puentea a Rs (revisa Rb y n).", "No sube con objeto: Rs en corto.", "Se ajusta por prueba: prueba 10, 15 y 22 Ω."], "simulación LTspice con motor SUPUESTO; NO validado con el motor real",
  tabla=[["Sin objeto", "≈ 0.1 V"], ["Con objeto", "≈ 1.9 V (con Rs = 15 Ω y el motor supuesto; a medir)"]],
  valida=False, nova="motor real", sim=[("prueba_potencia_Rs15_bjt", "vrs_lento", 1.7, 2.0)])
m("m_vel", "LED_ROJO", "Velocidad lenta contra velocidad normal", {"txt": "no se mide con multímetro"}, {"txt": "cuenta las vueltas del eje con el celular (video) o un tacómetro"}, "vueltas por segundo",
  "Cuántas vueltas da el eje con objeto comparado con sin objeto.", "Confirma que con objeto la velocidad baja a 40-60 % de la normal.",
  "Fuente conectada. Motor conectado. Mide sin objeto y con objeto.", "Entre 40 % y 60 % de la velocidad normal. Valor exacto: a medir.",
  ["Menos de 40 %: baja Rs (prueba 10 Ω).", "Más de 60 %: sube Rs (prueba 22 Ω).", "Con la simulación (motor supuesto): 10 Ω da 66 %, 15 Ω da 50 % y 22 Ω da 29 %; con el motor real saldrá distinto."],
  "a medir (motor real); simulación solo orientativa", valida=False, nova="motor real")
