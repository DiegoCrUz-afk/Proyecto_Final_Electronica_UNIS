"""HTML 3D de los protoboards (guia de armado). Uso: python exportar_protoboard3d.py"""
import json
from collections import defaultdict
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(PROY, "montaje3d"))
sys.argv = sys.argv[:1] + [os.devnull]
import generar_protoboard as P          # noqa: E402
import exportar_montaje3d as E          # noqa: E402

OUT = os.path.join(AQUI, "Protoboards_3D_miniestacion_v3.html")
PITCH = 2.54


def asignar_alturas(W, offs):
    """Cada cable sube, avanza en filas (z), avanza en columnas (x) y baja. Se le da una altura (nivel) para que ningun
    tramo toque a otro tramo del mismo nivel. Los cortos van abajo y los largos arriba."""
    def pt(e, net, kind):
        gx = offs[e["board"]] + e["x"]
        gy = e["y"] + ((0 if net == "0" else 6 if net == "v5" else 12) / PITCH if kind == "bus" else 0)
        return gx, gy
    items = []
    for w in W:
        if w["kind"] == "ext":
            continue
        ax, ay = pt(w["a"], w["net"], w["kind"])
        bx, by = pt(w["b"], w["net"], w["kind"])
        s1 = ((ax, ay), (ax, by))        # tramo a lo largo de las filas, en la columna de A
        s2 = ((ax, by), (bx, by))        # tramo a lo largo de las columnas, en la fila de B
        items.append((abs(ax - bx) + abs(ay - by), w, [s1, s2]))
    items.sort(key=lambda t: t[0])

    def dist(s, t):
        # distancia minima entre dos segmentos alineados a los ejes
        (x1, y1), (x2, y2) = s
        (u1, v1), (u2, v2) = t
        ax0, ax1 = sorted((x1, x2)); ay0, ay1 = sorted((y1, y2))
        bx0, bx1 = sorted((u1, u2)); by0, by1 = sorted((v1, v2))
        dx = max(bx0 - ax1, ax0 - bx1, 0); dy = max(by0 - ay1, ay0 - by1, 0)
        return (dx * dx + dy * dy) ** .5
    HLV = [11 + 1.5 * k for k in range(40)]
    n = len(items)
    segs = [[sg for sg in it[2] if sg[0] != sg[1]] for it in items]
    ends = [[it[2][0][0], it[2][1][1]] for it in items]
    # A debe ir MAS ALTO que B si el tramo de A pasa por encima de una pata de B
    deps = [set() for _ in range(n)]       # deps[a] = cables que deben quedar mas abajo que a
    for a_ in range(n):
        for b_ in range(n):
            if a_ != b_ and any(dist(sg, (e, e)) <= .55 for sg in segs[a_] for e in ends[b_]):
                deps[a_].add(b_)
    nivel = [None] * n
    pend = set(range(n))
    while pend:
        listos = [i for i in pend if all(nivel[d] is not None for d in deps[i] if d in pend or nivel[d] is not None) and not any(d in pend for d in deps[i])]
        if not listos:       # ciclo: se rompe soltando las dependencias del cable mas corto
            i = min(pend, key=lambda q: items[q][0])
            deps[i] = {d for d in deps[i] if d not in pend}
            continue
        for i in sorted(listos, key=lambda q: items[q][0]):
            k = max([nivel[d] + 1 for d in deps[i]] + [0])
            while k < len(HLV) - 1 and any(nivel[o] == k and any(dist(s1, s2) <= .55 for s1 in segs[i] for s2 in segs[o]) for o in range(n) if nivel[o] is not None):
                k += 1
            nivel[i] = k
            pend.discard(i)
    mx = 0
    for i, (_, w, _) in enumerate(items):
        w["h"] = HLV[nivel[i]]
        mx = max(mx, nivel[i])
    j = 0
    for w in W:
        if w["kind"] == "ext":
            w["h"] = HLV[min(mx + 2 + (j % 6), len(HLV) - 1)] ; j += 1
    return mx + 1
BL = [b.name for b in P.boards]
offs = {b: P.offset(b) for b in BL}
dims = {b: dict(x0=offs[b] - 4.5, x1=offs[b] + 14.5, z1=64) for b in BL}
LET = {0: "J", 1: "I", 2: "H", 3: "G", 4: "F", 6: "E", 7: "D", 8: "C", 9: "B", 10: "A"}  # igual que lo impreso en el tablero (izq. a der.)
ROWS_N = 63
row_lbl = lambda y: ROWS_N - 1 - y  # fila 0 abajo


def hole(b, x, y):
    if x in LET:
        return "%s-%s%d" % (b, LET[x], row_lbl(y))
    nom = {"0": "GND", "v5": "+5 V", "vm": "+12 V"}[P.rails_of(b)[x]]
    return "%s-riel %s %s fila %d" % (b, nom, "izq" if x < 5 else "der", row_lbl(y))


def valor(v):
    """Valores como {Kerr*10k} salen calculados (100k), no como formula."""
    m = re.fullmatch(r"\{(\w+)\*(\d+(?:\.\d+)?)k\}", str(v))
    if not m:
        return v
    par = re.search(r"\.param.*\b" + m.group(1) + r"=([0-9.]+)", open(os.path.join(PROY, "sistema.inc"), encoding="utf-8").read())
    n = float(par.group(1)) * float(m.group(2))
    return ("%g" % n) + "k" if n < 1000 else ("%g" % (n / 1000)) + "M"


POLAR_1U = {"LOG.Cpor", "ENC.Cfv", "ENC.Cfv2"}      # + a la pata 1 (nodo de mayor voltaje)
parts = []
for d in P.parts:
    pins = []
    for q in d["pins"]:
        bn, side, col, row = P.pos[(d["ref"], q["n"])]
        pins.append(dict(n=q["n"], net=q["net"], x=col, y=row, **({"name": q["name"]} if "name" in q else {})))
    bn = P.pos[(d["ref"], d["pins"][0]["n"])][0]
    p = dict(d, val=valor(d["val"]), board=bn, pins=pins, short=d["ref"].split(".")[-1], x=min(q["x"] for q in pins), y=min(q["y"] for q in pins), blk=d["blk"])
    if d["ref"] in POLAR_1U:                      # electroliticos de 1 uF (lista de compras): misma posicion que antes, pero con polaridad + / -
        p["kind"] = "CE"
        for q in p["pins"]:
            q["n"] = {"1": "+", "2": "-"}[q["n"]]
    p["cells"] = sorted({tuple(c) for c in P.partinfo.get(d["ref"], {}).get("area", [])})
    parts.append(p)
by_ref = {p["ref"]: p for p in parts}
nets = E.nets
nets.setdefault("LOG.lo", dict(color="#ff9f43", label="LOG.lo"))
W = []
for w in P.wires:
    a, b = dict(w["a"]), dict(w["b"])
    for e in (a, b):
        e["hole"] = hole(e["board"], e["x"], e["y"])
    W.append(dict(i=len(W) + 1, net=w["net"], color=nets[w["net"]]["color"], kind="signal", a=a, b=b))
for p in parts:
    if p.get("ext") or p["kind"] in ("TCRT", "OPTO"):
        dev = p.get("ext") or ("TCRT" if p["kind"] == "TCRT" else "OPTO")
        for q in p["pins"]:
            W.append(dict(i=len(W) + 1, net=q["net"], color=nets[q["net"]]["color"] if q["net"] in nets else "#bbbbbb", kind="ext",
                          a=dict(board=p["board"], x=q["x"], y=q["y"], hole=hole(p["board"], q["x"], q["y"]), part=p["ref"], pin=q["n"]),
                          b=dict(ext=dev, term=q["n"], hole="dispositivo " + dev + " · " + q["n"])))
# puentes entre rieles (GND, 5 V, 12 V): los calcula generar_protoboard
for w in P.bus:
    a, b = dict(w["a"]), dict(w["b"])
    for e in (a, b):
        e["hole"] = hole(e["board"], e["x"], e["y"])
    W.append(dict(i=len(W) + 1, net=w["net"], color=nets[w["net"]]["color"], kind="bus", a=a, b=b))
import ruteo_plano as ruteo_bajo
NIV = ruteo_bajo.rutear(W, parts, offs)
print("niveles de altura usados:", NIV)
gnd = {b: dict(x=-2, y=3) for b in BL}
titles = {b: ("BX-4135 · protoboard %d (placa %s)" % (BL.index(b) + 1, b) if b in P.BX else "PROTOBOARD %s · 830 puntos" % b) for b in BL}
zones = []
blocks = {}
for b in P.boards:
    for z, (r0, r1) in b.blocks.items():
        zones.append(dict(id=z, title=P.TITULOS[z], board=b.name, x=0, y=r0 - 2, w=11, h=r1 - r0 + 3))
for z in P.ORDEN:
    refs = [p["ref"] for p in parts if p["blk"] == z]
    blocks[z] = dict(title=P.TITULOS[z], boards=sorted({by_ref[r]["board"] for r in refs}), refs=refs)
rails = {b: {str(c): n for c, n in P.rails_of(b).items()} for b in BL}
# mediciones nuevas: alimentacion de cada chip y LED de objeto
GV = "Alimentación de cada chip"
for p_ in parts:
    if p_["kind"] == "IC":
        v_ = next(q for q in p_["pins"] if q.get("name") == "VCC")
        g_ = next(q for q in p_["pins"] if q.get("name") == "GND")
        E.m("m_vcc_" + p_["ref"], GV, "%s %s: entre VCC (pata %s) y GND (pata %s)" % (p_["ref"].split(".")[-1], p_["val"], v_["n"], g_["n"]), [p_["ref"], v_["n"]],
            "5.0 V (entre 4.75 y 5.25 V)" if v_["net"] == "v5" else "11.1 a 11.3 V (los 12 V después de D1)",
            "0 V: falta el cable de alimentación del chip o su GND. Si mide menos de 4.75 V, revisa el regulador de 5 V.", black=[p_["ref"], g_["n"]])
E.m("m_led", "LED de objeto", "LED de objeto: ánodo (pata A)", ["LOG.Dlo", "A"], "≈ 2.0 V con objeto (el LED enciende, unos 4.4 mA con la resistencia de 680 Ω); 5 V sin objeto (apagado)",
    "Nunca enciende: LED al revés (la pata larga es A) o Rlo (680 Ω) abierta.")
# pruebas de cada bloque: las mediciones guiadas (E.MEAS) cuya punta roja cae en una pieza del bloque
tests = defaultdict(list)
for m_ in E.MEAS:
    pr = by_ref.get(m_["red"][0])
    if pr:
        tests[pr["blk"]].append(m_["id"])
tests = dict(tests)
data = dict(parts=parts, wires=W, tracks=[], zones=zones, nets=nets, meas=E.MEAS, offs=offs, dims=dims, gnd=gnd, cu={b: "" for b in BL}, power=E.POWER, cell=1.27, pitch=2.54, w_trace=.8, w_wide=1.6,
            sim=E.datos_sim(), titles=titles, boards_list=BL, blocks=blocks, rails=rails, bx=P.BX, tests=tests)
tpl = open(os.path.join(AQUI, "plantilla_proto3d_v3.html"), encoding="utf-8").read()
three = open(os.path.join(PROY, "montaje3d", "lib3d", "three.min.js"), encoding="utf-8").read()
orbit = open(os.path.join(PROY, "montaje3d", "lib3d", "OrbitControls.js"), encoding="utf-8").read()
html = tpl.replace("/*__THREE__*/", three).replace("/*__ORBIT__*/", orbit).replace("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
open(OUT, "w", encoding="utf-8").write(html)
print("ok:", len(BL), "protoboards,", len(parts), "piezas,", len(W), "cables ->", OUT)
