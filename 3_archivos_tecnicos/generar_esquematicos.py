"""Genera los esquematicos de bloque (.asc) de LTspice para el proyecto.
Cada bloque es un .asc "puro" (sin fuentes de prueba): los pines de entrada/salida del bloque llevan * y el mismo
archivo se usa como hoja jerarquica del sistema completo. Los nombres de componentes y nodos coinciden con los
subcircuitos de sistema.inc (lo que se simula); comprobar_esquematicos.py verifica esa coincidencia.
Uso: python generar_esquematicos.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asc_lib import Schematic

DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "2_LTspice")


# ---------- colocacion con coordenadas de pin conocidas ----------
def vr(s, ref, val, xc, yt):          # resistencia vertical: pin1 arriba (xc,yt), pin2 abajo (xc,yt+80)
    return s.add("res", ref, val, xc - 16, yt - 16)


def hr(s, ref, val, xl, yc):          # resistencia horizontal: pin2 a la izquierda (xl,yc), pin1 a la derecha (xl+80,yc)
    return s.add("res", ref, val, xl + 96, yc - 16, "R90")


def vc(s, ref, val, xc, yt, pol=False):   # capacitor vertical: pin1 arriba (xc,yt), pin2 abajo (xc,yt+64)
    return s.add("polcap" if pol else "cap", ref, val, xc - 16, yt)


def hc(s, ref, val, xl, yc):          # capacitor horizontal: pin2 izquierda (xl,yc), pin1 derecha (xl+64,yc)
    return s.add("cap", ref, val, xl + 64, yc - 16, "R90")


def vd(s, ref, val, xc, yt, sym="diode"):  # diodo vertical: anodo arriba, catodo abajo
    return s.add(sym, ref, val, xc - 16, yt)


def vd_up(s, ref, val, xc, yb, sym="diode"):  # diodo vertical con el catodo ARRIBA (xc,yb-64) y el anodo abajo (xc,yb)
    return s.add(sym, ref, val, xc + 16, yb, "R180")


def hd(s, ref, val, xl, yc, sym="diode"):  # diodo horizontal: anodo izquierda (xl,yc), catodo derecha (xl+64,yc)
    return s.add(sym, ref, val, xl, yc + 16, "R270")


def npn(s, ref, model, x, y):         # C (x+64,y)  B (x,y+48)  E (x+64,y+96)
    return s.add("npn", ref, model, x, y)


def cmp_(s, ref, model, x, y):        # In+ (x-32,y+80) In- (x-32,y+48) V+ (x,y+32) V- (x,y+96) OUT (x+32,y+64)
    return s.add("OpAmps/opamp2", ref, model, x, y)


def gate(s, kind, ref, x, y):         # entradas (x-32,y-16),(x-32,y+16) o (x-32,y); salida (x+32,y); vcc (x,y-32)
    return s.add(kind, ref, kind, x, y)


def G(s, kind, ref, x, y, ins, out, vcc="v5"):
    """Compuerta con sus pines etiquetados por un cable corto (las etiquetas no tapan el dibujo)."""
    c = s.add(kind, ref, kind, x, y)
    m = {len(ins) + 1: out, len(ins) + 2: vcc}
    for i, n in enumerate(ins):
        m[i + 1] = n
    s.net(c, m, stub=24)
    return c


def fl(s, x, y, name):
    """Etiqueta de nodo en un punto. 'nombre*' = pin del bloque. '0' = tierra."""
    io = name.endswith("*")
    name = name.rstrip("*")
    s.flags.append((x, y, name))
    if io:
        s.iopins.append((x, y, "BiDir"))


def titulo(s, x, y, t, sub=()):
    s.text(x, y, t, size=3)
    for k, l in enumerate(sub):
        s.text(x, y + 30 + 18 * k, l, size=2)


def nota(s, x, y, lineas):
    for k, l in enumerate(lineas):
        s.text(x, y + 20 * k, l, size=2)


PARAMS = {"BLOQUE_SENSOR_IR": ".param kir=0.55", "BLOQUE_SOBRECORRIENTE": ".param koc=0.2",
          "BLOQUE_TEMPERATURA": ".param ktm=0.5", "BLOQUE_REFVEL": ".param kvn=0.8 kvr=0.7",
          "BLOQUE_ERROR_AMP": ".param Kerr=10"}


def guardar(s, nombre):
    import asc_route
    if nombre in PARAMS:      # posicion del trimpot / ganancia: la hoja es autonoma
        s.text(-100, 760, PARAMS[nombre], size=2, directive=True)
    n_ok, n_mal = asc_route.autoroute(s)
    if n_mal:
        print("  %s: redes sin cablear (quedan con etiqueta): %s" % (nombre, n_mal))
    r = asc_route.buses(s)
    print("  %s: rieles (unidos con cable, con etiqueta): %s" % (nombre, r))
    p = os.path.join(DEST, nombre + ".asc")
    s.save(p)
    return p


def trimpot(s, ref, val, xc, yt, cursor):
    """Trimpot como dos resistencias apiladas (Rp1 arriba, Rp2 abajo); el cursor es el nodo del medio."""
    a = vr(s, ref + "1", "{%s*(1-%s)}" % (val, cursor), xc, yt)
    b = vr(s, ref + "2", "{%s*%s}" % (val, cursor), xc, yt + 80)
    s.text(xc + 110, yt + 60, "trimpot " + val, size=2)
    return a, b


# ---------- Bloque 1: regulador ----------
def b_reg5v():
    s = Schematic(900, 500)
    titulo(s, -60, -130, "BLOQUE 1 - REGULADOR DE 5 V", ["vm (12 V despues del diodo) -> v5 (5 V). El Zener fija 5.6 V en la base de Q1 y la salida es esa tension menos 0.7 V.",
                                                         "Rtr (trimpot de 100 ohm) sube la salida unas decenas de mV para llevarla a 5.0 V."])
    vr(s, "Rz", "510", 0, 0)                         # (0,0)-(0,80)
    fl(s, 0, 0, "vm*")
    z = s.add("zener", "DZ", "D1N4734", 16, 144, "R180")   # anodo (0,144) catodo (0,80)
    vr(s, "Rtr", "10", 0, 144)
    fl(s, 0, 224, "0")
    fl(s, 0, 80, "bz")
    q = npn(s, "Q1", "QBD139", 96, 32)               # C (160,32) B (96,80) E (160,128)
    s.wire((0, 80), (96, 80))
    s.wire((0, 0), (160, 0), (160, 32))
    s.wire((160, 128), (400, 128))
    fl(s, 400, 128, "v5*")
    vc(s, "Cout", "100u", 240, 128, pol=True)
    fl(s, 240, 192, "0")
    vc(s, "C2", "100n", 320, 128)
    fl(s, 320, 192, "0")
    nota(s, -60, 300, ["DZ = Zener 1N4734A (5.6 V, 1 W).  Q1 = BD139 con disipador: en el peor caso (13 V, 120 mA) disipa ~0.9 W.",
                       "Cout (100 uF) y C2 (100 nF) filtran la salida. La resistencia Rz (510 ohm) deja ~9 mA en el Zener."])
    return guardar(s, "BLOQUE_REG5V")


# ---------- Bloque 2: sensor IR ----------
def b_sensor():
    s = Schematic(1100, 700)
    titulo(s, -180, -150, "BLOQUE 2 - SENSOR OPTICO IR", ["El fototransistor (TCRT5000) inyecta su corriente en el nodo b. Q2 (emisor comun) la amplifica.",
                                                          "El comparador (con histeresis por Rh) pone p = 1 cuando hay objeto."])
    # LED infrarrojo
    vr(s, "Rled", "270", -120, 240)
    fl(s, -120, 240, "v5")
    vd(s, "Dled", "DIR", -120, 320, sym="LED")
    fl(s, -120, 384, "0")
    s.text(-190, 410, "LED infrarrojo (~14 mA)", size=2)
    # entrada: capacitor de prueba y polarizacion de Q2
    hc(s, "Cac", "1u", 0, 80)                          # tin (0,80) -> b (64,80)
    fl(s, 0, 80, "tin*")
    s.wire((64, 80), (160, 80))
    vr(s, "R1", "47k", 96, 0)                          # (96,0)-(96,80)
    fl(s, 96, 0, "v5")
    vr(s, "R2", "10k", 96, 80)                         # (96,80)-(96,160)
    fl(s, 96, 160, "0")
    fl(s, 96, 80, "b*")
    npn(s, "Q2", "Q2N3904", 160, 32)                   # C (224,32) B (160,80) E (224,128)
    vr(s, "Rc", "680", 224, -48)                       # (224,-48)-(224,32)
    fl(s, 224, -48, "v5")
    vr(s, "RE", "150", 224, 128)
    fl(s, 224, 208, "0")
    s.wire((224, 32), (416, 32), (416, 48), (448, 48))   # c -> entrada - del comparador
    fl(s, 224, 32, "c")
    # divisor del umbral (trimpot)
    vr(s, "Ra", "10k", 400, 128)
    fl(s, 400, 128, "v5")
    trimpot(s, "Rp", "10k", 400, 208, "kir")           # cursor th en (400,288)
    vr(s, "Rb", "26.8k", 400, 368)
    fl(s, 400, 448, "0")
    s.wire((400, 288), (432, 288), (432, 80), (448, 80))
    fl(s, 400, 288, "th")
    cm = cmp_(s, "Xu1", "LM393", 480, 0)               # In+ (448,80) In- (448,48) V+ (480,32) V- (480,96) OUT (512,64)
    fl(s, 480, 32, "v5")
    fl(s, 480, 96, "0")
    s.wire((512, 64), (576, 64), (640, 64))
    fl(s, 640, 64, "p*")
    vr(s, "Rpu", "10k", 576, -16)                      # (576,-16)-(576,64)
    fl(s, 576, -16, "v5")
    vr(s, "Rh", "220k", 704, 64)                       # p -> th (realimentacion positiva)
    s.wire((640, 64), (704, 64))
    s.wire((704, 144), (704, 288), (432, 288))
    s.text(720, 90, "histeresis", size=2)
    s.text(590, 20, "pull-up", size=2)
    nota(s, -190, 480, ["Sin objeto: ~2 uA -> c queda en ~4.2 V (sobre el umbral) y p = 0.   Con objeto: ~50 uA -> c baja a ~2.9 V y p = 1.",
                        "Ganancia de Q2 = -Rc / (re + RE) = -680 / (14 + 150) = -4.  El trimpot mueve el umbral entre 2.9 V y 3.9 V."])
    return guardar(s, "BLOQUE_SENSOR_IR")


# ---------- Bloque 3: sobrecorriente ----------
def b_sobrecorriente():
    s = Schematic(1400, 900)
    titulo(s, -80, -190, "BLOQUE 3 - SOBRECORRIENTE", ["La caida en el shunt (0.5 ohm, nodo sh) la amplifica el LM358: ganancia 1 + Rf/Rg = 7.8.",
                                                        "D1 y Cpk guardan el pico; Rd y Cd retrasan ~0.1 s (ignora el arranque); el comparador baja setn si hay falla."])
    cmp_(s, "Xu2", "LM358", 200, 0)                    # In+ (168,80) In- (168,48) V+ (200,32) V- (200,96) OUT (232,64)
    fl(s, 168, 80, "sh*")
    fl(s, 200, 32, "vm*")
    fl(s, 200, 96, "0")
    s.wire((168, 48), (136, 48))
    vr(s, "Rg", "1k", 136, 48)                         # (136,48)-(136,128)
    fl(s, 136, 128, "0")
    s.wire((136, 48), (136, -24))
    hr(s, "Rf", "6.8k", 136, -24)                      # (136,-24)-(216,-24)
    s.wire((216, -24), (264, -24), (264, 64), (232, 64))
    hd(s, "D1", "D1N4148", 296, 64)                    # (296,64)-(360,64)
    s.wire((264, 64), (296, 64))
    vc(s, "Cpk", "100n", 360, 64)
    fl(s, 360, 128, "0")
    s.wire((360, 64), (424, 64))
    vr(s, "Rbl", "22k", 424, 64)
    fl(s, 424, 144, "0")
    s.wire((424, 64), (456, 64))
    hr(s, "Rd", "10k", 456, 64)                        # (456,64)-(536,64)
    vc(s, "Cd", "10u", 536, 64, pol=True)
    fl(s, 536, 128, "0")
    fl(s, 536, 64, "dl")
    s.wire((536, 64), (668, 64))
    cmp_(s, "Xu3", "LM393", 700, 16)                   # In+ (668,96) In- (668,64) V+ (700,48) V- (700,112) OUT (732,80)
    fl(s, 668, 96, "ref")
    fl(s, 700, 48, "v5")
    fl(s, 700, 112, "0")
    s.wire((732, 80), (800, 80))
    fl(s, 800, 80, "setn*")
    vr(s, "Ra", "10k", 700, 176)
    fl(s, 700, 176, "v5*")
    trimpot(s, "Rp", "10k", 700, 256, "koc")           # cursor ref en (700,336)
    fl(s, 700, 336, "ref")
    s.wire((700, 336), (640, 336), (640, 96), (668, 96))        # ref del trimpot al comparador
    vr(s, "Rb", "10k", 700, 416)
    fl(s, 700, 496, "0")
    nota(s, -80, 560, ["Corriente de disparo ~ (Vref + 0.6 V) / (0.5 ohm x 7.8). Con Vref = 2 V: ~0.67 A. El trimpot Rp ajusta Vref.",
                       "Cd = 10 uF con Rd = 10k da ~0.1 s de retardo: el arranque del motor (~30 ms) no dispara, una sobrecarga sostenida si."])
    return guardar(s, "BLOQUE_SOBRECORRIENTE")


# ---------- Bloque 4: temperatura ----------
def b_temperatura():
    s = Schematic(1000, 700)
    titulo(s, -80, -150, "BLOQUE 4 - SOBRETEMPERATURA", ["El NTC de 10k va entre v5 y tnode; Rfix completa el divisor, asi tnode sube al calentarse.",
                                                          "Si tnode supera el umbral (trimpot, 45 a 55 C) el comparador baja setn. Rh da ~2.6 C de histeresis."])
    vr(s, "Rfix", "10k", 0, 64)
    fl(s, 0, 64, "tnode*")
    fl(s, 0, 144, "0")
    s.text(-60, 30, "NTC 10k (externo): v5 -> tnode", size=2)
    vr(s, "Ra", "22k", 240, -48)
    fl(s, 240, -48, "v5*")
    trimpot(s, "Rp", "10k", 240, 32, "ktm")           # cursor ref en (240,112)
    fl(s, 240, 112, "ref")
    vr(s, "Rb", "68k", 240, 192)
    fl(s, 240, 272, "0")
    cmp_(s, "Xu4", "LM393", 520, 48)                   # In+ (488,128) In- (488,96) V+ (520,80) V- (520,144) OUT (552,112)
    fl(s, 488, 128, "ref")
    fl(s, 488, 96, "tnode")
    fl(s, 520, 80, "v5")
    fl(s, 520, 144, "0")
    s.wire((552, 112), (600, 112))
    fl(s, 600, 112, "setn*")
    vr(s, "Rh", "1Meg", 640, 112)
    s.wire((600, 112), (640, 112))
    fl(s, 640, 192, "ref")
    s.wire((0, 64), (0, -80), (440, -80), (440, 96), (488, 96))          # tnode al comparador
    s.wire((240, 112), (400, 112), (400, 128), (488, 128))               # ref al comparador
    s.wire((640, 192), (640, 232), (400, 232), (400, 128))               # Rh vuelve a ref
    nota(s, -80, 330, ["NTC a 50 C = 3.6k -> tnode = 3.7 V. El trimpot mueve Vref de 3.4 V (44 C) a 3.9 V (57 C)."])
    return guardar(s, "BLOQUE_TEMPERATURA")


# ---------- Bloque 5: logica ----------
def b_logica():
    s = Schematic(1700, 1000)
    titulo(s, -80, -170, "BLOQUE 5 - LOGICA COMBINACIONAL", ["Entradas: E (habilitar), G (cubierta cerrada), P (objeto), setn (falla de corriente o temperatura, activa en bajo) y el boton de reset.",
                                                           "Salidas: M = E.G.F'   N = M.P'   L = M.P   A = F.  F es un pestillo NAND: recuerda la falla hasta pulsar reset."])
    filas = [("e", "ein*", "ef", "Xi1", "Xi2", "ein_n", "e"), ("g", "gin*", "gf", "Xi3", "Xi4", "gin_n", "g"), ("r", "rin*", "rf", "Xi5", "Xi6", "rin_n", "rst")]
    for k, (pre, ent, f, i1, i2, mid, out) in enumerate(filas):
        y = k * 176
        vr(s, "Rp" + pre, "10k", 48, y)                # (48,y)-(48,y+80) a tierra
        fl(s, 48, y, ent)
        fl(s, 48, y + 80, "0")
        s.wire((48, y), (96, y))
        hr(s, "Rs" + pre, "10k", 96, y)                # (96,y)-(176,y)
        vc(s, "C" + f, "100n", 176, y)
        fl(s, 176, y + 64, "0")
        s.wire((176, y), (240, y))
        fl(s, 176, y, f)
        c1 = gate(s, "HC_SCHINV", i1, 272, y)
        fl(s, 272, y - 32, "v5")
        s.wire((304, y), (368, y))
        c2 = gate(s, "HC_SCHINV", i2, 400, y)
        fl(s, 400, y - 32, "v5")
        s.wire((432, y), (480, y))
        fl(s, 480, y, out)
    s.text(60, 520, "Rp: cable roto = 0 (seguro).  Rs + C: antirrebote (1 ms).  Dos inversores Schmitt (74HC14): senal limpia.", size=2)
    vc(s, "Cpor", "1u", 48, 592)
    fl(s, 48, 592, "v5")
    s.wire((48, 656), (112, 656))
    vr(s, "Rpor", "47k", 112, 656)
    fl(s, 112, 736, "0")
    s.wire((112, 656), (144, 656))
    hd(s, "Dpor", "D1N4148", 144, 656)
    fl(s, 208, 656, "rf")
    s.text(30, 560, "reset automatico al encender", size=2)
    # pestillo NAND (74HC00)
    G(s, "HC_NAND2", "Xg1", 720, 0, ["rst", "setn"], "reset_n")
    G(s, "HC_NAND2", "Xg2", 720, 144, ["setn", "fn"], "f*")
    G(s, "HC_NAND2", "Xg3", 720, 288, ["reset_n", "f"], "fn*")
    G(s, "HC_NAND2", "Xg4", 720, 432, ["p*", "p"], "pn")
    vr(s, "Rsn", "10k", 960, 0)
    fl(s, 960, 0, "v5*")
    fl(s, 960, 80, "setn*")
    s.text(690, -70, "pestillo (74HC00): setn = 0 pone F = 1", size=2)
    s.text(690, 470, "P' = NAND(P,P)", size=2)
    # decision (74HC08)
    G(s, "HC_AND2", "Xa1", 1200, 0, ["e", "g"], "m1")
    G(s, "HC_AND2", "Xa2", 1200, 144, ["m1", "fn"], "m*")
    G(s, "HC_AND2", "Xa3", 1200, 288, ["m", "pn"], "n*")
    G(s, "HC_AND2", "Xa4", 1200, 432, ["m", "p"], "l*")
    s.text(1170, -70, "decision (74HC08)", size=2)
    return guardar(s, "BLOQUE_LOGICA")


# ---------- Bloque 6: PWM ----------
def b_pwm():
    s = Schematic(1200, 700)
    titulo(s, -100, -150, "BLOQUE 6 - GENERADOR DE PWM", ["El NE555 oscila (~7 kHz): el nodo tri sube y baja entre 1.7 y 3.3 V (rampa).",
                                                          "El comparador pone pwm = 1 mientras vctrl > tri: a mayor vctrl, pulsos mas anchos."])
    c = s.add("Misc/NE555", "X5", "NE555", 296, 160)    # GND (184,64) TRIG (184,128) OUT (184,192) RST (184,256) CV (408,256) THR (408,192) DIS (408,128) VCC (408,64)
    fl(s, 184, 64, "0"); fl(s, 184, 128, "tri"); fl(s, 184, 192, "tri_o"); fl(s, 184, 256, "v5"); fl(s, 408, 64, "v5")
    vr(s, "Ra5", "1k", 500, 48)                         # (500,48)-(500,128)
    fl(s, 500, 48, "v5")
    s.wire((408, 128), (500, 128))
    vr(s, "Rb5", "10k", 500, 128)                       # (500,128)-(500,208)
    s.wire((408, 192), (444, 192), (444, 208), (500, 208))
    vc(s, "Ct", "10n", 500, 208)
    fl(s, 500, 272, "0")
    fl(s, 500, 208, "tri")
    s.wire((408, 256), (460, 256))
    vc(s, "Ccv", "10n", 460, 256)
    fl(s, 460, 320, "0")
    fl(s, 460, 256, "cv")
    cmp_(s, "Xu6", "LM393", 700, 160)                   # In+ (668,240) In- (668,208) V+ (700,192) V- (700,256) OUT (732,224)
    s.wire((500, 208), (560, 208))
    s.wire((560, 208), (668, 208))
    s.wire((184, 128), (140, 128), (140, 360), (560, 360), (560, 208))   # TRIG del 555 al nodo tri
    fl(s, 668, 240, "vctrl*")
    fl(s, 700, 192, "v5")
    fl(s, 700, 256, "0")
    s.wire((732, 224), (800, 224), (860, 224))
    fl(s, 860, 224, "pwm*")
    vr(s, "Rpu", "10k", 800, 144)
    fl(s, 800, 144, "v5")
    nota(s, -100, 420, ["f = 1.44 / ((Ra5 + 2 Rb5) Ct) = 1.44 / (21k x 10 nF) = 6.9 kHz.   Ciclo de trabajo = (vctrl - 1.7 V) / 1.7 V: vctrl = 2.5 V da ~50 %.",
                        "El pin 3 del 555 (tri_o) no se usa: la rampa se toma del condensador Ct."])
    return guardar(s, "BLOQUE_PWM_GEN")


# ---------- Bloque 7: potencia ----------
def b_potencia():
    s = Schematic(1200, 800)
    titulo(s, -80, -150, "BLOQUE 7 - SEGURIDAD, EXCITADOR Y MOSFET", ["La compuerta AND deja pasar el PWM solo si M = 1: la seguridad manda sobre el PWM.",
                                                                  "Q3 y Q4 (seguidor complementario) cargan y descargan la compuerta de M1. Dfw protege contra el pico del motor."])
    c = gate(s, "HC_AND2", "Xa5", 200, 96)              # a (168,80) b (168,112) y (232,96) vcc (200,64)
    fl(s, 200, 64, "v5")
    s.wire((168, 80), (128, 80)); fl(s, 128, 80, "pwm*")
    s.wire((168, 112), (128, 112)); fl(s, 128, 112, "m*")
    s.wire((232, 96), (368, 96))
    npn(s, "Q3", "Q2N3904", 368, 0)                     # C (432,0) B (368,48) E (432,96)
    fl(s, 432, 0, "v5")
    s.wire((368, 48), (368, 96), (368, 144))
    q4 = s.add("pnp", "Q4", "Q2N3906", 368, 192, "M180")  # E (432,96) B (368,144) C (432,192)
    fl(s, 432, 192, "0")
    s.wire((432, 96), (480, 96))
    hr(s, "Rg", "47", 480, 96)                          # (480,96)-(560,96)
    s.wire((560, 96), (640, 96))
    vr(s, "Rpd", "10k", 600, 96)
    fl(s, 600, 176, "0")
    fl(s, 600, 96, "gate")
    s.add("nmos", "M1", "IRFZ44N_P", 640, 16)             # D (688,16) G (640,96) S (688,112)
    fl(s, 688, 16, "dm*")
    fl(s, 688, 112, "sh*")
    s.wire((688, 16), (800, 16))
    vd_up(s, "Dfw", "D1N5819", 800, 16, sym="diode")     # catodo arriba (800,-48) anodo (800,16)
    fl(s, 800, -48, "vm*")
    vr(s, "Rsh", "0.5", 688, 112)
    fl(s, 688, 192, "0")
    nota(s, -80, 300, ["El motor va entre vm y dm. Con M1 encendido la corriente baja por el motor, M1 y el shunt Rsh (0.5 ohm, 5 W).",
                       "Al apagar M1 el motor sigue empujando corriente: pasa por Dfw (Schottky 1N5819) de dm a vm.",
                       "M1 = IRFZ44N: con 4.3 V en la compuerta conduce con ~0.07 ohm (con 10 V seria 0.02). Rg limita la corriente de la compuerta."])
    return guardar(s, "BLOQUE_POTENCIA")


# ---------- Bloque 8: encoder + F-V ----------
def b_encoder():
    s = Schematic(1700, 800)
    titulo(s, -180, -150, "BLOQUE 8 - ENCODER Y CONVERTIDOR FRECUENCIA-VOLTAJE", ["El fototransistor del optointerruptor (nodo enc, con pull-up Rpe) da pulsos al pasar las ranuras del disco. El comparador Xu7 los limpia.",
                                                                              "El 555 monoestable da un pulso fijo de 220 us por cada uno; el filtro RC doble lo vuelve voltaje: vspd = 1.1 mV por Hz."])
    vr(s, "Rled", "220", -120, 0)
    fl(s, -120, 0, "v5")
    vd(s, "Dled", "DIR", -120, 80, sym="LED")
    fl(s, -120, 144, "0")
    s.text(-190, 170, "LED del optointerruptor", size=2)
    vr(s, "Rpe", "10k", 0, 0)
    fl(s, 0, 0, "v5*")
    fl(s, 0, 80, "enc*")
    s.wire((0, 80), (48, 80), (48, 48), (288, 48))
    s.text(-60, 110, "fototransistor", size=2)
    cmp_(s, "Xu7", "LM393", 320, 0)                    # In+ (288,80) In- (288,48) V+ (320,32) V- (320,96) OUT (352,64)
    fl(s, 320, 32, "v5"); fl(s, 320, 96, "0")
    vr(s, "Ru1", "10k", 224, 112)
    fl(s, 224, 112, "v5")
    vr(s, "Ru2", "10k", 224, 192)
    fl(s, 224, 272, "0")
    s.wire((224, 192), (256, 192), (256, 80), (288, 80))
    fl(s, 224, 192, "eref")
    s.wire((352, 64), (416, 64), (480, 64))
    vr(s, "Rpq", "10k", 416, -16)
    fl(s, 416, -16, "v5")
    vr(s, "Rhe", "1Meg", 352, 128)
    fl(s, 352, 128, "eq"); fl(s, 352, 208, "eref")
    s.wire((352, 208), (352, 240), (256, 240), (256, 192))        # Rhe a eref
    fl(s, 416, 64, "eq")
    hc(s, "Cd", "1n", 480, 64)                         # (480,64)-(544,64)
    vr(s, "Rtg", "10k", 544, -16)
    fl(s, 544, -16, "v5")
    s.wire((544, 64), (608, 64))
    vd_up(s, "Dcl", "D1N4148", 608, 64)                # catodo (608,0) a v5, anodo (608,64) a tg
    fl(s, 608, 0, "v5")
    s.wire((608, 64), (640, 64), (640, 80), (688, 80))
    fl(s, 544, 64, "tg")
    c = s.add("Misc/NE555", "X7", "NE555", 800, 112)   # GND (688,16) TRIG (688,80) OUT (688,144) RST (688,208) CV (912,208) THR (912,144) DIS (912,80) VCC (912,16)
    fl(s, 688, 16, "0"); fl(s, 688, 144, "mono"); fl(s, 688, 208, "v5"); fl(s, 912, 16, "v5")
    s.wire((912, 80), (944, 80), (944, 144), (912, 144))
    s.wire((944, 80), (1008, 80))
    vr(s, "Rt7", "20k", 1008, 0)
    fl(s, 1008, 0, "v5")
    vc(s, "Ct7", "10n", 1008, 80)
    fl(s, 1008, 144, "0")
    fl(s, 1008, 80, "dis7")
    s.wire((912, 208), (960, 208))
    vc(s, "Ccvm", "10n", 960, 208)
    fl(s, 960, 272, "0")
    gate(s, "HC_BUF", "Xb1", 1200, 112)                # a (1168,112) y (1232,112) vcc (1200,80)
    s.wire((1168, 112), (1128, 112)); fl(s, 1128, 112, "mono"); fl(s, 1200, 80, "v5")
    s.wire((1232, 112), (1264, 112))
    hr(s, "Rfv", "10k", 1264, 112)                     # (1264,112)-(1344,112)
    vc(s, "Cfv", "1u", 1344, 112)
    fl(s, 1344, 176, "0")
    fl(s, 1344, 112, "vf1")
    s.wire((1344, 112), (1376, 112))
    hr(s, "Rfv2", "10k", 1376, 112)                    # (1376,112)-(1456,112)
    vc(s, "Cfv2", "1u", 1456, 112)
    fl(s, 1456, 176, "0")
    s.wire((1456, 112), (1520, 112))
    fl(s, 1520, 112, "vspd*")
    nota(s, -180, 380, ["tw = 1.1 x Rt7 x Ct7 = 1.1 x 20k x 10 nF = 220 us.  Vspd = 5 V x tw x f.  A 500 Hz: 0.55 V.",
                        "Dcl protege la entrada del 555 contra el pico positivo del derivador (Cd y Rtg dan un pulso corto en cada flanco de bajada)."])
    return guardar(s, "BLOQUE_ENCODER_FV")


# ---------- Bloque 9: referencia ----------
def b_refvel():
    s = Schematic(900, 600)
    titulo(s, -160, -130, "BLOQUE 9 - REFERENCIA DE VELOCIDAD", ["Rt y el trimpot Rp1 fijan la referencia normal (~0.53 V).",
                                                               "Si l = 1, Q5 conecta Rp2 y baja vref a la mitad (velocidad reducida)."])
    vr(s, "Rt", "68k", 0, -32)
    fl(s, 0, -32, "v5*")
    s.wire((0, 48), (96, 48), (160, 48), (220, 48))
    vr(s, "Rp1", "{10k*kvn}", 0, 48)
    fl(s, 0, 128, "0")
    fl(s, 220, 48, "vref*")
    vr(s, "Rp2", "{10k*kvr}", 96, 48)                  # (96,48)-(96,128) = cq
    npn(s, "Q5", "Q2N3904", 32, 128)                   # C (96,128) B (32,176) E (96,224)
    fl(s, 96, 224, "0")
    s.wire((16, 176), (32, 176))
    hr(s, "Rb5", "10k", -64, 176)                      # (-64,176)-(16,176)
    fl(s, -64, 176, "l*")
    vc(s, "Cr", "100n", 160, 48)
    fl(s, 160, 112, "0")
    nota(s, -160, 330, ["Rp1 y Rp2 son dos trimpots de 10k (normal y reducida): en la simulacion kvn y kvr indican la posicion del cursor.",
                        "Reducida = 50 % de la normal (el enunciado pide entre 40 % y 60 %)."])
    return guardar(s, "BLOQUE_REFVEL")


# ---------- Bloque 10: amplificador de error ----------
def b_error():
    s = Schematic(1500, 900)
    titulo(s, -220, -150, "BLOQUE 10 - AMPLIFICADOR DE ERROR (LAZO CERRADO)", ["Tres seguidores (Xbr, Xbs, Xbo) aislan vref, la velocidad medida y el nivel Voff. Xu2b resta y multiplica por Kerr = 10:",
                                                                         "vctrl = Kerr (vref - vspd) + Voff. Si la velocidad baja, vctrl sube y el PWM da mas potencia al motor."])
    ys = [("Xbr", "vref*", "vrb", 0), ("Xbs", "vspd*", "vsb", 208), ("Xbo", "voff", "vob", 416)]
    for ref, inn, out, y in ys:
        cmp_(s, ref, "LM358", 200, y)                  # In+ (168,y+80) In- (168,y+48) V+ (200,y+32) V- (200,y+96) OUT (232,y+64)
        fl(s, 168, y + 80, inn)
        fl(s, 200, y + 32, "vm" + ("*" if y == 0 else ""))
        fl(s, 200, y + 96, "0")
        s.wire((232, y + 64), (264, y + 64), (264, y + 128), (136, y + 128), (136, y + 48), (168, y + 48))
        fl(s, 264, y + 64, out)
    vr(s, "Rv1", "4.7k", 0, 400)
    fl(s, 0, 400, "v5*")
    vr(s, "Rv2", "5.1k", 0, 480)
    fl(s, 0, 560, "0")
    fl(s, 0, 480, "voff")
    s.wire((0, 480), (64, 480))
    s.wire((64, 480), (112, 480), (112, 496), (168, 496))          # voff a la entrada + de Xbo
    vc(s, "Cv", "100n", 64, 480)
    fl(s, 64, 544, "0")
    hr(s, "R1", "10k", 400, 256)                       # (400,256)-(480,256)
    fl(s, 400, 256, "vsb")
    s.wire((480, 256), (704, 256))
    s.wire((704, 256), (868, 256))
    hr(s, "R3", "10k", 400, 320)
    fl(s, 400, 320, "vrb")
    s.wire((480, 320), (704, 320))
    s.wire((704, 320), (784, 320))
    s.wire((784, 320), (836, 320), (836, 288), (868, 288))
    vr(s, "R4", "{Kerr*10k}", 704, 360)                # R4: pata 1 = vob (arriba), pata 2 = inp (sube por el cable de la derecha)
    fl(s, 704, 360, "vob")
    s.wire((704, 440), (784, 440), (784, 320))
    s.wire((704, 256), (704, 160))                     # realimentacion: Rf6 y Cf6 de oa a inn
    hr(s, "Rf6", "{Kerr*10k}", 704, 160)
    s.wire((784, 160), (960, 160))
    s.wire((704, 160), (704, 112))
    hc(s, "Cf6", "10n", 704, 112)
    s.wire((768, 112), (960, 112), (960, 160))
    s.wire((960, 160), (960, 272))
    cmp_(s, "Xu2b", "LM358", 900, 208)                 # In+ (868,288) In- (868,256) V+ (900,240) V- (900,304) OUT (932,272)
    fl(s, 900, 240, "vm"); fl(s, 900, 304, "0")
    s.wire((932, 272), (960, 272))
    s.wire((960, 272), (980, 272))
    fl(s, 940, 272, "oa")
    hr(s, "Ro", "1k", 980, 272)                        # (980,272)-(1060,272)
    vc(s, "Cvc", "100n", 1060, 272)
    fl(s, 1060, 336, "0")
    s.wire((1060, 272), (1120, 272))
    fl(s, 1120, 272, "vctrl*")
    nota(s, -220, 640, ["Kerr = 10: un error de 0.1 V mueve vctrl 1 V.  Voff = 2.6 V es el punto de partida (~55 % de PWM).",
                        "Un solo circuito integrado LM324 (cuatro amplificadores) contiene Xbr, Xbs, Xbo y Xu2b."])
    return guardar(s, "BLOQUE_ERROR_AMP")


# ---------- Bloque 11: alarma ----------
def b_alarma():
    s = Schematic(800, 500)
    titulo(s, -120, -110, "BLOQUE 11 - ALARMA", ["Cuando f = 1 (falla enclavada), Q6 conduce como interruptor y enciende el buzzer de 12 V",
                                                "(en la simulacion el buzzer se representa con Rbz de 400 ohm). El LED indica la falla con luz."])
    hr(s, "Rb", "1k", 0, 96)
    fl(s, 0, 96, "f*")
    npn(s, "Q6", "Q2N3904", 80, 48)                    # C (144,48) B (80,96) E (144,144)
    vr(s, "Rbz", "400", 144, -32)
    fl(s, 144, -32, "vm*")
    fl(s, 144, 144, "0")
    s.text(176, 0, "buzzer activo 12 V (~30 mA)", size=2)
    vr(s, "Rl", "470", -80, -32)                       # senal luminosa: f -> Rl -> LED -> tierra
    fl(s, -80, -32, "f")
    s.add("LED", "Dl", "DLED", -96, 48)                # anodo (-80,48) catodo (-80,112)
    fl(s, -80, 112, "0")
    s.text(-110, 150, "LED rojo (~8 mA)", size=2)
    nota(s, -120, 220, ["Ib = (4.9 - 0.7 V) / 1k = 4 mA.  Ic = 30 mA.  Ic/Ib = 7.5, menor que hFE: el transistor trabaja saturado, como interruptor."])
    return guardar(s, "BLOQUE_ALARMA")


BLOQUES = [b_reg5v, b_sensor, b_sobrecorriente, b_temperatura, b_logica, b_pwm, b_potencia, b_encoder, b_refvel, b_error, b_alarma]

if __name__ == "__main__":
    for f in BLOQUES:
        print(f.__name__, "->", os.path.basename(f()))
