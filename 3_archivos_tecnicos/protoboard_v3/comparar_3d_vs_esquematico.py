"""Compara las conexiones del 3D v3 con lo que LTspice lee de cada esquematico (.net generado con LTspice -netlist de cada BLOQUE_*.asc).
Para cada bloque: los grupos de patas que comparten un nodo en el esquematico deben ser EXACTAMENTE los mismos grupos que comparten una red en el 3D.
Uso: python comparar_3d_vs_esquematico.py [Protoboards_3D...v3.html]   (antes: python ../comprobar_esquematicos.py  para refrescar los .net)"""
import io
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.abspath(os.path.join(AQUI, ".."))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "Protoboards_3D_miniestacion_v3.html")
sys.argv = sys.argv[:1]
sys.path.insert(0, os.path.join(PROY, "montaje3d"))
import generar_montaje3d as g3   # noqa: E402

txt = open(SRC, encoding="utf-8").read()
D, _ = json.JSONDecoder().raw_decode(txt[txt.index("const DATA = ") + 13:])
parts = {p["ref"]: p for p in D["parts"]}
ASC = os.path.join(PROY, "..", "2_LTspice")
MAPA = {"REG5V": "BLOQUE_REG5V", "SENSOR_IR": "BLOQUE_SENSOR_IR", "SOBRECORRIENTE": "BLOQUE_SOBRECORRIENTE", "TEMPERATURA": "BLOQUE_TEMPERATURA", "LOGICA": "BLOQUE_LOGICA",
        "PWM_GEN": "BLOQUE_PWM_GEN", "POTENCIA": "BLOQUE_POTENCIA", "ENCODER_FV": "BLOQUE_ENCODER_FV", "REFVEL": "BLOQUE_REFVEL", "ERROR_AMP": "BLOQUE_ERROR_AMP", "ALARMA": "BLOQUE_ALARMA"}
ABBR = g3.ABBR


def leer_net(ruta):
    out = {}
    for l in open(ruta, encoding="latin1").read().splitlines():
        l = l.split(";")[0].strip()
        if not l or l[0] in "*.+" or l.startswith("Version"):
            continue
        t = l.split()
        out[t[0].lower()] = t[1:]
    return out


# patas de cada pieza discreta segun la letra (orden de nodos en la linea del netlist)
def patas_discreta(p, nodos):
    k, ref = p["kind"], p["ref"]
    n = {q["n"]: q for q in p["pins"]}
    if k in ("R", "RW", "CC"):
        return [("1", nodos[0]), ("2", nodos[1])]
    if k == "CE":
        return [("+", nodos[0]), ("-", nodos[1])]
    if k in ("D", "DZ", "LED"):
        return [("A", nodos[0]), ("K", nodos[1])]
    if k in ("Q92", "Q126"):
        return [("C", nodos[0]), ("B", nodos[1]), ("E", nodos[2])]
    if k == "MOS":
        return [("D", nodos[0]), ("G", nodos[1]), ("S", nodos[2])]
    if k == "BUZZER":
        return [("+", nodos[0]), ("-", nodos[1])]
    return []


def comparar(blk, arch):
    net = leer_net(os.path.join(ASC, arch + ".net"))
    pin_nodo = {}                                   # (ref, pata) -> nodo del esquematico
    ab = ABBR[blk]
    for ref, p in parts.items():
        if p["blk"] != blk or p["kind"] in ("IC", "TB", "TCRT", "OPTO", "TRIM"):
            continue
        nm = ref.split(".")[-1].lower()
        if nm not in net:
            continue
        for pata, nodo in patas_discreta(p, net[nm]):
            pin_nodo[(ref, pata)] = nodo.lower()
    # circuitos integrados: cada seccion es una instancia X del esquematico
    for uid, (modelo, abbr, sec) in g3.IC_ASSIGN.items():
        if abbr != ab:
            continue
        for s, inst in sec.items():
            nm = inst.split(".")[-1].lower()
            if nm not in net:
                continue
            nodos = [x.lower() for x in net[nm]]
            tipo = nodos[-1]
            nodos = nodos[:-1]
            if modelo in ("LM393", "LM358", "LM324"):
                ip, im, out = g3.OPAMP_SEC[modelo][s]
                vcc, gnd = g3.VCC_GND[modelo]
                inp, inm, vc, ve, o = nodos
                for pata, nd in ((ip, inp), (im, inm), (out, o), (vcc, vc), (gnd, ve)):
                    pin_nodo[(uid, str(pata))] = nd
            elif modelo == "NE555":
                for i, nd in enumerate(nodos[:8], 1):
                    if i == 3 and nd.endswith("tri_o"):
                        continue
                    pin_nodo[(uid, str(i))] = nd
            elif modelo in ("74HC00", "74HC08"):
                vcc, _g = g3.VCC_GND[modelo]
                if tipo.upper() == "HC_BUF":
                    a, y, vc = nodos
                    ia, ib, iy = g3.GATE_SEC[modelo][s]
                    for pata, nd in ((ia, a), (ib, a), (iy, y), (vcc, vc)):
                        pin_nodo[(uid, str(pata))] = nd
                else:
                    a, b, y, vc = nodos
                    ia, ib, iy = g3.GATE_SEC[modelo][s]
                    for pata, nd in ((ia, a), (ib, b), (iy, y), (vcc, vc)):
                        pin_nodo[(uid, str(pata))] = nd
            elif modelo == "74HC14":
                a, y, vc = nodos
                ia, iy = g3.INV_SEC[s]
                vcc, _g = g3.VCC_GND[modelo]
                for pata, nd in ((ia, a), (iy, y), (vcc, vc)):
                    pin_nodo[(uid, str(pata))] = nd
    # redes del 3D para esas mismas patas
    pin_red = {}
    for (ref, pata) in pin_nodo:
        q = next(x for x in parts[ref]["pins"] if x["n"] == pata)
        pin_red[(ref, pata)] = q["net"]
    # resistencias y capacitores sin polaridad: sus dos patas son iguales (da lo mismo cual se llama 1 o 2), asi que se cuentan sin numero
    simetrica = lambda ref, pata: parts[ref]["kind"] in ("R", "RW", "CC") and pata in ("1", "2")
    g_esq, g_3d = defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(int))
    for (ref, pata), nd in pin_nodo.items():
        lab = (ref, "-" if simetrica(ref, pata) else pata)
        g_esq[nd][lab] += 1
        g_3d[pin_red[(ref, pata)]][lab] += 1
    a = {frozenset(v.items()) for v in g_esq.values()}
    b = {frozenset(v.items()) for v in g_3d.values()}
    # el nodo 0 y los puertos de alimentacion se comparan igual: grupos de patas
    return len(pin_nodo), sorted([sorted(x) for x in a - b])[:6], sorted([sorted(x) for x in b - a])[:6]


todo_ok = True
total = 0
for blk, arch in MAPA.items():
    n, solo_esq, solo_3d = comparar(blk, arch)
    total += n
    ok = not solo_esq and not solo_3d
    todo_ok &= ok
    print("%-16s %3d patas comparadas  %s" % (blk, n, "COINCIDE" if ok else "DIFERENCIAS"))
    for x in solo_esq:
        print("    solo en el esquematico:", x)
    for x in solo_3d:
        print("    solo en el 3D:", x)
print("TOTAL: %d patas comparadas ->" % total, "TODO COINCIDE" if todo_ok else "HAY DIFERENCIAS")
