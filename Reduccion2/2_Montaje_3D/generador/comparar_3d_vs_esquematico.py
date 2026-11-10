"""Compara el 3D (datos_r2.json) con los netlists que LTspice saca de los esquematicos dibujados (1_LTspice\\BLOQUE_*.net).
Las redes con nombre automatico de LTspice (P001, N004...) se emparejan por estructura: cada red del esquematico debe corresponder a UNA red del 3D
(uno a uno) y cada pata de cada pieza debe caer en la red que le toca. Uso: py -3.13 comparar_3d_vs_esquematico.py"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
LT = os.path.join(AQUI, "..", "..", "1_LTspice")
sys.path.insert(0, AQUI)
import generar_montaje3d as g

D = json.load(open(os.path.join(AQUI, "datos_r2.json"), encoding="utf-8"))
parts = {p["ref"]: p for p in D["parts"]}
GLOB = {"0", "v5", "b", "p", "setn", "m", "n", "l", "f", "fn", "ein", "gin", "rin", "dm", "ds"}
HOJAS = {"BLOQUE_SENSOR_IR": "SEN", "BLOQUE_LOGICA": "LOG", "BLOQUE_POTENCIA_R2": "POT"}
RENOMBRAR = {"Rl": "ALA.Rl", "Dl": "ALA.Dl", "Cin": "ENT.Cin"}
SIM = {"R", "C", "RW", "CC", "CE"}          # piezas sin orden de patas (R, C) -> se prueban las 2 alineaciones


def nodo(n, hoja):
    return "0" if n == "0" else (n if n in GLOB else hoja + ":" + n)


esq = {}        # ref3d -> (tipo, [redes en orden de roles])
gates = []
for hoja, pre in HOJAS.items():
    for ln in open(os.path.join(LT, hoja + ".net"), encoding="latin1").read().splitlines():
        ln = ln.split(";")[0]
        t = ln.split()
        if not t or ln.startswith(("*", ".", "+")):
            continue
        nm = t[0]; c = nm[0].upper()
        mt = re.search(r"(X[a-z]+\d+)$", nm)
        if c == "X" and mt:
            gates.append((hoja, pre + "." + mt.group(1), t[-1], [nodo(x, hoja) for x in t[1:-1]])); continue
        if nm in ("Rp1", "Rp2") and pre == "SEN":
            esq["SEN." + nm] = ("TRIMP", [nodo(x, hoja) for x in t[1:3]]); continue
        ref = RENOMBRAR.get(nm, pre + "." + nm)
        if c == "D" and t[3] == "DIR":
            continue                       # LED infrarrojo: va dentro del TCRT5000
        if c == "M":
            esq[ref] = ("MOS", [nodo(x, hoja) for x in t[1:4]]); continue       # D G S
        if c == "Q":
            esq[ref] = ("Q", [nodo(x, hoja) for x in t[1:4]]); continue         # C B E
        if c == "D":
            esq[ref] = ("D", [nodo(x, hoja) for x in t[1:3]]); continue         # A K
        if c in "RC":
            esq[ref] = ("SIM", [nodo(x, hoja) for x in t[1:3]])

def red3d(ref, kind):
    p = parts[ref]; pins = {q["n"]: q["net"] for q in p["pins"]}
    if kind == "MOS": return [pins["D"], pins["G"], pins["S"]]
    if kind == "Q": return [pins["C"], pins["B"], pins["E"]]
    if kind == "D": return [pins["A"], pins["K"]]
    return [q["net"] for q in p["pins"]]

mapa = {n: n for n in GLOB}          # red del esquematico -> red del 3D
inv = {n: n for n in GLOB}
mal = 0
ok = 0


def consistente(a, b):
    return (a not in mapa or mapa[a] == b) and (b not in inv or inv[b] == a)


def fijar(a, b):
    mapa[a] = b; inv[b] = a


# piezas con orden (polares, transistores) y compuertas: alineacion directa
pend = []
for ref, (kind, redes) in esq.items():
    if ref not in parts and kind != "TRIMP":
        print("FALTA en el 3D:", ref); mal += 1; continue
    if kind == "TRIMP":
        continue
    r3 = red3d(ref, kind)
    if kind == "SIM":
        pend.append((ref, redes, r3)); continue
    for a, b in zip(redes, r3):
        if consistente(a, b): fijar(a, b)
        else: print("DIFERENTE", ref, "esquematico:", a, "3D:", b, "(ya emparejada con", mapa.get(a), ")"); mal += 1

ics = {p["ref"]: p for p in D["parts"] if p["kind"] == "IC"}
ASIGN = {"SEN.Xu1": ("U1", "A")}
ASIGN.update({"LOG.Xg%d" % i: ("U8", i) for i in range(1, 5)})
ASIGN.update({"LOG.Xa%d" % i: ("U9", i) for i in range(1, 5)})
ASIGN.update({"LOG.Xi%d" % i: ("U11", i) for i in range(1, 7)})
pares_ic = []
for hoja, key, tipo, N in gates:
    uid, sec = ASIGN[key]
    pins = {q["n"]: q["net"] for q in ics[uid]["pins"]}
    if tipo == "LM393":
        ip, im, out = g.OPAMP_SEC["LM393"][sec]; vc, ve = g.VCC_GND["LM393"]
        esperado = {ip: N[0], im: N[1], vc: N[2], ve: N[3], out: N[4]}
    elif tipo == "HC_SCHINV":
        ia, iy = g.INV_SEC[sec]; esperado = {ia: N[0], iy: N[1], 14: N[2]}
    else:
        ia, ib, iy = g.GATE_SEC[ics[uid]["val"]][sec]
        esperado = {ia: N[0], iy: N[1], 14: N[2]} if tipo == "HC_BUF" else {ia: N[0], ib: N[1], iy: N[2], 14: N[3]}
    for pin, a in esperado.items():
        pares_ic.append((uid, pin, a, pins[str(pin)]))
for uid, pin, a, b in pares_ic:
    if consistente(a, b): fijar(a, b)
    else: print("DIFERENTE", uid, "pata", pin, "esquematico:", a, "3D:", b); mal += 1
# R y C: probar las 2 alineaciones hasta que quede una sola posible
cambio = True
while pend and cambio:
    cambio = False
    for item in list(pend):
        ref, (a1, a2), (b1, b2) = item
        o1 = consistente(a1, b1) and consistente(a2, b2) and (a1 != a2 or b1 == b2)
        o2 = consistente(a1, b2) and consistente(a2, b1)
        if o1 and not o2: fijar(a1, b1); fijar(a2, b2); pend.remove(item); cambio = True
        elif o2 and not o1: fijar(a1, b2); fijar(a2, b1); pend.remove(item); cambio = True
        elif not o1 and not o2:
            print("DIFERENTE", ref, "esquematico:", (a1, a2), "3D:", (b1, b2)); mal += 1; pend.remove(item); cambio = True
        elif {mapa.get(a1), mapa.get(a2)} == {b1, b2} or (a1 in mapa and a2 in mapa):
            pend.remove(item); cambio = True
for ref, redes, r3 in pend:       # simetricas ambiguas: ambas alineaciones valen (por ejemplo dos redes nuevas iguales)
    print("ambigua (no decide):", ref)
# trimpot SEN.T1: Rp1 = patas 1-W, Rp2 = patas W-3
pn = {q["n"]: q["net"] for q in parts["SEN.T1"]["pins"]}
for ref, (kind, redes) in esq.items():
    if kind != "TRIMP": continue
    par = {"SEN.Rp1": ("1", "W"), "SEN.Rp2": ("W", "3")}[ref]
    a, b = redes; x, y = pn[par[0]], pn[par[1]]
    if {mapa.get(a), mapa.get(b)} == {x, y} or (a not in mapa and b not in mapa) :
        ok += 1
    else:
        print("DIFERENTE trimpot", ref, redes, "3D:", (x, y), "mapa:", mapa.get(a), mapa.get(b)); mal += 1
# verificacion final: todas las piezas, pata por pata, con el mapa ya fijo
for ref, (kind, redes) in esq.items():
    if kind in ("TRIMP",) or ref not in parts: continue
    r3 = red3d(ref, kind)
    got = [mapa.get(a) for a in redes]
    if kind == "SIM":
        good = sorted(got) == sorted(r3)
    else:
        good = got == r3
    if good: ok += 1
    else: print("DIFERENTE final", ref, "esquematico->3D:", got, "3D:", r3); mal += 1
for uid, pin, a, b in pares_ic:
    if mapa.get(a) == b: ok += 1
    else: print("DIFERENTE IC", uid, pin); mal += 1
# 3D sin esquematico (esperado: IC, conectores y el TCRT)
for ref, p in parts.items():
    if p["kind"] in ("IC", "TB", "TCRT", "TRIM"): continue
    if ref not in esq: print("SOLO en el 3D:", ref, p["kind"]); mal += 1
# redes del 3D que no se emparejaron con nadie (salvo NC y las de conectores/TCRT/ICs sin uso)
usadas = set(mapa.values())
extra = sorted({q["net"] for p in D["parts"] if p["kind"] not in ("IC", "TB", "TCRT") for q in p["pins"]} - usadas - {"NC"})
if extra: print("redes del 3D (piezas discretas) sin red en el esquematico:", extra); mal += len(extra)
print("piezas y patas comparadas OK:", ok, "| diferencias:", mal)
print("RESULTADO:", "TODO COINCIDE" if mal == 0 else "HAY DIFERENCIAS")
