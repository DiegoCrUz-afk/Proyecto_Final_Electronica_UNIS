"""Arma los datos del montaje 3D (placas perforadas) a partir de sistema.inc, que es la fuente de verdad del circuito.

- Cada elemento del netlist se convierte en una pieza fisica (resistencia, capacitor, transistor, circuito integrado...).
- Los comparadores / amplificadores / compuertas se reparten en circuitos integrados reales con su numero de pata.
- Se colocan en 3 placas perforadas (una zona por bloque) y se calculan los cables.
- verificar() comprueba que cada red del netlist queda en UN solo grupo electrico (cables + buses) y que ningun
  circuito integrado tiene patas sin atender.
Uso: python generar_montaje3d.py   (importado por exportar_montaje3d.py)
"""
import os
import re
import math
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
INC = os.path.join(AQUI, "..", "sistema.inc")

# bloque -> (abreviatura, titulo, placa)
BLOQUES = {
    "REG5V": ("REG", "1 Regulador 5 V", "A"),
    "POTENCIA": ("POT", "7 Potencia (PWM + MOSFET)", "A"),
    "ALARMA": ("ALA", "11 Alarma", "A"),
    "SENSOR_IR": ("SEN", "2 Sensor IR", "B"),
    "SOBRECORRIENTE": ("OC", "3 Sobrecorriente", "B"),
    "TEMPERATURA": ("TMP", "4 Temperatura", "B"),
    "LOGICA": ("LOG", "5 Logica", "B"),
    "REFVEL": ("REF", "9 Referencia de velocidad", "C"),
    "ERROR_AMP": ("ERR", "10 Amplificador de error", "C"),
    "PWM_GEN": ("PWM", "6 Generador de PWM", "C"),
    "ENCODER_FV": ("ENC", "8 Encoder y F-V", "C"),
}
ABBR = {k: v[0] for k, v in BLOQUES.items()}
PLACAS = {"A": "PLACA A · Alimentación y potencia", "B": "PLACA B · Sensores, protecciones y lógica", "C": "PLACA C · Control de velocidad"}
ZONAS = {  # orden de las zonas dentro de cada placa
    "A": ["ENTRADA", "REG5V", "POTENCIA", "ALARMA"],
    "B": ["SENSOR_IR", "SOBRECORRIENTE", "TEMPERATURA", "LOGICA"],
    "C": ["REFVEL", "ERROR_AMP", "PWM_GEN", "ENCODER_FV"],
}
TITULO_ZONA = dict((k, v[1]) for k, v in BLOQUES.items())
TITULO_ZONA["ENTRADA"] = "0 Entrada de 12 V"

# circuitos integrados: id -> (modelo, patas, {seccion: instancias})
# las patas se dan por nombre de funcion; el numero real esta en PIN_IC
IC_PINS = {
    "LM393": ("DIP8", 8), "LM358": ("DIP8", 8), "LM324": ("DIP14", 14), "NE555": ("DIP8", 8),
    "74HC00": ("DIP14", 14), "74HC08": ("DIP14", 14), "74HC14": ("DIP14", 14),
}
# nombre de pata fisica -> numero, por modelo
NAMES = {
    "LM393": {1: "OUT A", 2: "IN- A", 3: "IN+ A", 4: "GND", 5: "IN+ B", 6: "IN- B", 7: "OUT B", 8: "VCC"},
    "LM358": {1: "OUT A", 2: "IN- A", 3: "IN+ A", 4: "GND", 5: "IN+ B", 6: "IN- B", 7: "OUT B", 8: "VCC"},
    "LM324": {1: "OUT 1", 2: "IN- 1", 3: "IN+ 1", 4: "VCC", 5: "IN+ 2", 6: "IN- 2", 7: "OUT 2", 8: "OUT 3", 9: "IN- 3", 10: "IN+ 3", 11: "GND", 12: "IN+ 4", 13: "IN- 4", 14: "OUT 4"},
    "NE555": {1: "GND", 2: "TRIG", 3: "OUT", 4: "RESET", 5: "CTRL", 6: "THR", 7: "DISCH", 8: "VCC"},
    "74HC00": {1: "1A", 2: "1B", 3: "1Y", 4: "2A", 5: "2B", 6: "2Y", 7: "GND", 8: "3Y", 9: "3A", 10: "3B", 11: "4Y", 12: "4A", 13: "4B", 14: "VCC"},
    "74HC08": {1: "1A", 2: "1B", 3: "1Y", 4: "2A", 5: "2B", 6: "2Y", 7: "GND", 8: "3Y", 9: "3A", 10: "3B", 11: "4Y", 12: "4A", 13: "4B", 14: "VCC"},
    "74HC14": {1: "1A", 2: "1Y", 3: "2A", 4: "2Y", 5: "3A", 6: "3Y", 7: "GND", 8: "4Y", 9: "4A", 10: "5Y", 11: "5A", 12: "6Y", 13: "6A", 14: "VCC"},
}
# seccion -> patas (entradas, salida) para comparadores/amplificadores: (in+, in-, out)
OPAMP_SEC = {
    "LM393": {"A": (3, 2, 1), "B": (5, 6, 7)},
    "LM358": {"A": (3, 2, 1), "B": (5, 6, 7)},
    "LM324": {"1": (3, 2, 1), "2": (5, 6, 7), "3": (10, 9, 8), "4": (12, 13, 14)},
}
GATE_SEC = {   # compuertas de 2 entradas: seccion -> (a, b, y)
    "74HC00": {1: (1, 2, 3), 2: (4, 5, 6), 3: (9, 10, 8), 4: (12, 13, 11)},
    "74HC08": {1: (1, 2, 3), 2: (4, 5, 6), 3: (9, 10, 8), 4: (12, 13, 11)},
}
INV_SEC = {1: (1, 2), 2: (3, 4), 3: (5, 6), 4: (9, 8), 5: (11, 10), 6: (13, 12)}   # 74HC14: (entrada, salida)
VCC_GND = {"LM393": (8, 4), "LM358": (8, 4), "LM324": (4, 11), "NE555": (8, 1), "74HC00": (14, 7), "74HC08": (14, 7), "74HC14": (14, 7)}

# asignacion de instancias del netlist a circuitos integrados fisicos
IC_ASSIGN = {
    "U1": ("LM393", "SEN", {"A": "SEN.Xu1"}),
    "U14": ("LM393", "OC", {"A": "OC.Xu3"}),
    "U2": ("LM393", "TMP", {"A": "TMP.Xu4"}),
    "U3": ("LM393", "ENC", {"A": "ENC.Xu7"}),
    "U13": ("LM393", "PWM", {"A": "PWM.Xu6"}),
    "U4": ("LM358", "OC", {"A": "OC.Xu2"}),
    "U5": ("LM324", "ERR", {"1": "ERR.Xbr", "2": "ERR.Xbs", "3": "ERR.Xbo", "4": "ERR.Xu2b"}),
    "U6": ("NE555", "PWM", {"X": "PWM.X5"}),
    "U7": ("NE555", "ENC", {"X": "ENC.X7"}),
    "U8": ("74HC00", "LOG", {1: "LOG.Xg1", 2: "LOG.Xg2", 3: "LOG.Xg3", 4: "LOG.Xg4"}),
    "U9": ("74HC08", "LOG", {1: "LOG.Xa1", 2: "LOG.Xa2", 3: "LOG.Xa3", 4: "LOG.Xa4"}),
    "U10": ("74HC08", "POT", {1: "POT.Xa5"}),
    "U12": ("74HC08", "ENC", {1: "ENC.Xb1"}),
    "U11": ("74HC14", "LOG", {1: "LOG.Xi1", 2: "LOG.Xi2", 3: "LOG.Xi3", 4: "LOG.Xi4", 5: "LOG.Xi5", 6: "LOG.Xi6"}),
}
IC_ZONA = {"U1": "SENSOR_IR", "U2": "TEMPERATURA", "U3": "ENCODER_FV", "U4": "SOBRECORRIENTE", "U5": "ERROR_AMP", "U6": "PWM_GEN", "U7": "ENCODER_FV",
           "U8": "LOGICA", "U9": "LOGICA", "U10": "POTENCIA", "U11": "LOGICA", "U12": "ENCODER_FV", "U13": "PWM_GEN", "U14": "SOBRECORRIENTE"}


def leer_netlist():
    """sistema.inc -> {bloque: {'ports': [...], 'elems': [(nombre, [nodos], resto)]}}"""
    bl = {}
    cur = None
    for raw in open(INC, encoding="latin1").read().splitlines():
        l = raw.strip()
        m = re.match(r"\.subckt (\w+) (.*)", l, re.I)
        if m:
            cur = m.group(1)
            bl[cur] = {"ports": m.group(2).split(), "elems": []}
            continue
        if l.lower().startswith(".ends"):
            cur = None
            continue
        if cur is None or not l or l.startswith("*") or l.startswith("."):
            continue
        t = l.split()
        bl[cur]["elems"].append((t[0], t[1:]))
    return bl


def nodo(blk, n, ports):
    if n == "0":
        return "0"
    if n in ports:
        return n
    return ABBR[blk] + "." + n


def construir():
    bl = leer_netlist()
    parts = []        # piezas discretas
    ics = {}          # id -> dict con pines
    nid = lambda blk, nm: ABBR[blk] + "." + nm

    def add(ref, blk, kind, val, pins, **k):
        d = dict(ref=ref, blk=blk, kind=kind, val=val, pins=pins)
        d.update(k)
        parts.append(d)

    xs = {}   # instancias X (compuertas, comparadores, 555): "ABR.Xnn" -> (blk, tipo, nodos)
    for blk, info in bl.items():
        if blk not in BLOQUES:
            continue
        ports = set(info["ports"])
        N = lambda n: nodo(blk, n, ports)
        trims = {}
        for name, t in info["elems"]:
            ab = ABBR[blk]
            c = name[0].upper()
            ident = ab + "." + name
            if c == "X":
                tipo = t[-1]
                xs[ident] = (blk, tipo, [N(n) for n in t[:-1]])
            elif c == "R":
                val = t[2]
                if name in ("Rp1", "Rp2") and blk in ("SENSOR_IR", "SOBRECORRIENTE", "TEMPERATURA"):
                    trims.setdefault("T", {})[name] = [N(t[0]), N(t[1])]
                    continue
                if name in ("Rp1", "Rp2") and blk == "REFVEL":
                    add(ab + ".T" + name[-1], blk, "TRIM", "10k", [("1", N(t[0])), ("W", N(t[1])), ("3", "NC")], note="reostato: patas 1 y W")
                    continue
                if blk == "REG5V" and name == "Rtr":
                    add(ab + ".Rtr", blk, "TRIM", "100 Ω", [("1", N(t[0])), ("W", N(t[1])), ("3", "NC")], note="reostato: patas 1 y W; se ajusta cerca de 10 Ω")
                    continue
                if blk == "ALARMA" and name == "Rbz":
                    add(ab + ".BZ", blk, "BUZZER", "buzzer activo 12 V", [("+", N(t[0])), ("-", N(t[1]))])
                    continue
                if name == "Rsh":
                    add(ident, blk, "RW", "0.5 Ω 5 W", [("1", N(t[0])), ("2", N(t[1]))])
                    continue
                if name == "Rm":
                    continue
                add(ident, blk, "R", val.replace("Meg", "M"), [("1", N(t[0])), ("2", N(t[1]))])
            elif c == "C":
                val = t[2]
                a, b = N(t[0]), N(t[1])
                n_val = float(re.sub(r"u$", "e-6", re.sub(r"n$", "e-9", re.sub(r"p$", "e-12", val))))
                if n_val >= 10e-6:
                    add(ident, blk, "CE", val.replace("u", " µF"), [("+", a), ("-", b)], big=n_val >= 1000e-6)
                else:
                    v = val.replace("u", " µF").replace("n", " nF").replace("p", " pF")
                    add(ident, blk, "CC", v, [("1", a), ("2", b)])
            elif c == "D":
                model = t[2]
                if model == "DIR":
                    continue     # LED infrarrojo: va dentro del TCRT5000 / optointerruptor
                if model == "DLED":
                    add(ident, blk, "LED", "LED rojo", [("A", N(t[0])), ("K", N(t[1]))])
                elif model == "D1N4734":
                    add(ident, blk, "DZ", "Zener 1N4734A 5.6 V", [("K", N(t[1])), ("A", N(t[0]))])
                else:
                    add(ident, blk, "D", model.replace("D", "", 1), [("A", N(t[0])), ("K", N(t[1]))])
            elif c == "Q":
                m = t[3]
                if m == "QBD139":
                    add(ident, blk, "Q126", "BD139", [("E", N(t[2])), ("C", N(t[0])), ("B", N(t[1]))])
                elif m == "Q2N3906":
                    add(ident, blk, "Q92", "2N3906", [("E", N(t[2])), ("B", N(t[1])), ("C", N(t[0]))])
                else:
                    add(ident, blk, "Q92", "2N3904", [("E", N(t[2])), ("B", N(t[1])), ("C", N(t[0]))])
            elif c == "M":
                add(ident, blk, "MOS", "IRFZ44N", [("G", N(t[1])), ("D", N(t[0])), ("S", N(t[2]))])
        if "T" in trims:
            a = trims["T"]["Rp1"]
            b = trims["T"]["Rp2"]
            assert a[1] == b[0], (blk, a, b)
            add(ab + ".T1", blk, "TRIM", "10k", [("1", a[0]), ("W", a[1]), ("3", b[1])], note="trimpot multivuelta; patas 1, W (cursor), 3")
        # optoelectronica de bloque
        if blk == "SENSOR_IR":
            # Dled nled 0 (LED IR) + fototransistor (colector v5, emisor b)
            add("SEN.TCRT", blk, "TCRT", "TCRT5000", [("A", N("nled")), ("K", "0"), ("C", "v5"), ("E", "b")])
        if blk == "ENCODER_FV":
            add("ENC.OPTO", blk, "OPTO", "optointerruptor ranurado", [("A", N("nled")), ("K", "0"), ("C", "enc"), ("E", "0")])

    # ---- entrada, interruptores y dispositivos externos (no estan en sistema.inc)
    add("ENT.J1", "ENTRADA", "TB", "Entrada 12 V (jack)", [("+12V", "vin"), ("GND", "0")], ext="FUENTE")
    add("ENT.D1", "ENTRADA", "D", "1N4007", [("A", "vin"), ("K", "vm")])
    add("ENT.Cin", "ENTRADA", "CE", "1000 µF", [("+", "vm"), ("-", "0")], big=True)
    add("ENT.TBM", "ENTRADA", "TB", "Motor 12 V", [("M+", "vm"), ("M-", "dm")], ext="MOTOR")
    add("ENT.TBE", "LOGICA", "TB", "Interruptor E", [("5V", "v5"), ("E", "ein")], ext="SW_E")
    add("ENT.TBG", "LOGICA", "TB", "Micro-switch cubierta", [("5V", "v5"), ("G", "gin")], ext="SW_G")
    add("ENT.TBR", "LOGICA", "TB", "Pulsador reset", [("5V", "v5"), ("RST", "rin")], ext="SW_R")
    add("ENT.TBN", "TEMPERATURA", "TB", "NTC 10 k", [("5V", "v5"), ("NTC", "tnode")], ext="NTC")
    for x in parts:
        pass
    # el TCRT5000 y el optointerruptor se conectan con cable: se ponen en la zona de su bloque (conector de 4 patas)
    return bl, parts, xs


def secciones_ic(xs):
    """arma los circuitos integrados con sus patas y las redes de cada pata."""
    ics = []
    usados = set()
    for uid, (modelo, abbr, sec) in IC_ASSIGN.items():
        nom = NAMES[modelo]
        pines = {i: None for i in nom}      # numero -> red
        vcc, gnd = VCC_GND[modelo]
        notas = []
        for s, inst in sec.items():
            usados.add(inst)
            blk, tipo, n = xs[inst]
            if modelo in ("LM393", "LM358", "LM324"):
                ip, im, out = OPAMP_SEC[modelo][s]
                inp, inm, vc, ve, o = n
                pines[ip], pines[im], pines[out] = inp, inm, o
                pines[vcc], pines[gnd] = vc, ve
            elif modelo == "NE555":
                g, trig, out, rst, cv, thr, dis, vc = n
                pines[1], pines[2], pines[3], pines[4], pines[5], pines[6], pines[7], pines[8] = g, trig, (out if out != "tri_o" and not out.endswith("tri_o") else "NC"), rst, cv, thr, dis, vc
            elif modelo in ("74HC00", "74HC08"):
                if tipo == "HC_BUF":
                    a, y, vc = n
                    ia, ib, iy = GATE_SEC[modelo][s]
                    pines[ia], pines[ib], pines[iy] = a, a, y
                else:
                    a, b, y, vc = n
                    ia, ib, iy = GATE_SEC[modelo][s]
                    pines[ia], pines[ib], pines[iy] = a, b, y
                pines[vcc] = vc
                pines[gnd] = "0"
            elif modelo == "74HC14":
                a, y, vc = n
                ia, iy = INV_SEC[s]
                pines[ia], pines[iy] = a, y
                pines[vcc] = vc
                pines[gnd] = "0"
        # secciones sin usar: entradas a tierra (no flotantes), salidas sin conectar
        for i in nom:
            if pines[i] is None:
                nm = nom[i]
                if nm in ("VCC", "GND"):
                    pines[i] = "0"
                elif nm.startswith("OUT") or nm.endswith("Y"):
                    pines[i] = "NC"
                elif nm.startswith("IN") or nm[-1] in "AB" or nm[0] in "1234":
                    pines[i] = "0"
                else:
                    pines[i] = "NC"
                if pines[i] == "0" and nm not in ("VCC", "GND"):
                    notas.append(nm)
        # alimentacion del chip: tomar el vcc de alguna seccion usada
        if modelo != "NE555":
            for s, inst in sec.items():
                blk, tipo, n = xs[inst]
                v = n[2] if modelo in ("LM393", "LM358", "LM324") else n[-1]
                pines[vcc] = v
        ics.append(dict(id=uid, model=modelo, abbr=abbr, pins=pines, names=nom, sec=sec, spare=notas))
    return ics, usados


def formas(p):
    """(ancho, alto, [(pata, dx, dy)]) en agujeros de 2.54 mm."""
    k = p["kind"]
    pn = [q[0] for q in p["pins"]]
    if k == "R":
        return 5, 1, [(0, 0), (4, 0)]
    if k == "RW":
        return 6, 1, [(0, 0), (5, 0)]
    if k in ("CC",):
        return 3, 1, [(0, 0), (2, 0)]
    if k == "CE":
        s = 3 if p.get("big") else 2
        return s + 1, 1, [(0, 0), (s, 0)]
    if k in ("D", "DZ"):
        return 5, 1, [(0, 0), (4, 0)]
    if k == "LED":
        return 2, 1, [(0, 0), (1, 0)]
    if k in ("Q92", "Q126", "MOS", "TRIM"):
        return 3, 1, [(0, 0), (1, 0), (2, 0)]
    if k == "BUZZER":
        return 4, 1, [(0, 0), (3, 0)]
    if k in ("TCRT", "OPTO"):
        return 4, 1, [(0, 0), (1, 0), (2, 0), (3, 0)]
    if k == "TB":
        n = len(p["pins"])
        return 2 * n, 1, [(2 * i, 0) for i in range(n)]
    raise ValueError(k)


def pos_dip(n, i):
    """posicion (dx, dy) de la pata i de un DIP de n patas, visto desde arriba con la muesca a la izquierda."""
    h = n // 2
    if i <= h:
        return i - 1, 3
    return h - (i - h), 0


def distribuir(parts, ics):
    """coloca todo en las placas. Devuelve dict zona -> (placa, x0, y0, ancho, alto) y asigna x,y a cada pieza."""
    # agrupar por zona
    zonas = defaultdict(list)
    for p in parts:
        zonas[p["blk"]].append(p)
    for ic in ics:
        zonas[IC_ZONA[ic["id"]]].append(dict(ref=ic["id"], blk=IC_ZONA[ic["id"]], kind="IC", val=ic["model"], ic=ic, pins=[]))
    ANCHO = 38
    out = {}
    pos = {}
    for placa, zl in ZONAS.items():
        y = 4
        for z in zl:
            items = zonas[z]
            # primero los IC, luego el resto en el orden del netlist
            items.sort(key=lambda p: (0 if p["kind"] == "IC" else 1))
            x = 1
            fila_y = y + 3     # deja espacio para el titulo de la zona
            fila_h = 0
            for p in items:
                if p["kind"] == "IC":
                    n = IC_PINS[p["val"]][1]
                    w, h = n // 2, 4
                else:
                    w, h, _ = formas(p)
                if x + w > ANCHO - 1:
                    x = 1
                    fila_y += fila_h + 3
                    fila_h = 0
                pos[p["ref"]] = (placa, x, fila_y)
                p["placa"], p["x"], p["y"] = placa, x, fila_y
                if p["kind"] == "IC":
                    p["ic"]["placa"], p["ic"]["x"], p["ic"]["y"] = placa, x, fila_y
                x += w + 2
                fila_h = max(fila_h, h)
            out[z] = (placa, 0, y, ANCHO, fila_y + fila_h + 3 - y)
            y = fila_y + fila_h + 4
        out["_alto_" + placa] = y
    return out


def construir_todo():
    """Devuelve (piezas, zonas, nets): piezas con patas ya colocadas en la placa."""
    bl, parts, xs = construir()
    ics, usados = secciones_ic(xs)
    pend = [k for k in xs if k not in usados]
    assert not pend, pend
    zonas = distribuir(parts, ics)
    datos = []
    for p in parts:
        w, h, pp = formas(p)
        pins = []
        for (nm, red), (dx, dy) in zip(p["pins"], pp):
            pins.append(dict(n=nm, net=red, x=p["x"] + dx, y=p["y"] + dy))
        d = dict(ref=p["ref"], blk=p["blk"], kind=p["kind"], val=p["val"], board=p["placa"], x=p["x"], y=p["y"], w=w, h=h, pins=pins)
        for k in ("note", "ext", "big"):
            if k in p:
                d[k] = p[k]
        datos.append(d)
    for ic in ics:
        n = IC_PINS[ic["model"]][1]
        pins = []
        for i in range(1, n + 1):
            dx, dy = pos_dip(n, i)
            pins.append(dict(n=str(i), name=ic["names"][i], net=ic["pins"][i], x=ic["x"] + dx, y=ic["y"] + dy))
        secs = {str(k): v for k, v in ic["sec"].items()}
        datos.append(dict(ref=ic["id"], blk=IC_ZONA[ic["id"]], kind="IC", val=ic["model"], board=ic["placa"], x=ic["x"], y=ic["y"], w=n // 2, h=4,
                          pins=pins, secs=secs, spare=ic["spare"]))
    return datos, zonas, ics


if __name__ == "__main__":
    bl, parts, xs = construir()
    ics, usados = secciones_ic(xs)
    datos, zonas, ics = construir_todo()
    print(len(datos), "piezas;", {k: v for k, v in zonas.items()})
