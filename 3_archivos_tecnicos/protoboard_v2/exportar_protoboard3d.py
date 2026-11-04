"""HTML 3D de los protoboards (guia de armado). Uso: python exportar_protoboard3d.py"""
import json
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

OUT = os.path.join(AQUI, "..", "..", "6_Montaje_3D", "Protoboards_3D_miniestacion_v2.html")
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
offs = {b: i * 22 for i, b in enumerate(BL)}
dims = {b: dict(x0=offs[b] - 4.5, x1=offs[b] + 14.5, z1=64) for b in BL}
LET = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 6: "F", 7: "G", 8: "H", 9: "I", 10: "J"}


def hole(b, x, y):
    if x in LET:
        return "%s-%s%d" % (b, LET[x], y + 1)
    return "%s-riel %s fila %d" % (b, {-3: "+5 V izq", -2: "GND izq", 12: "GND der", 13: "+12 V der"}.get(x, "?"), y + 1)


parts = []
for d in P.parts:
    pins = []
    for q in d["pins"]:
        bn, side, col, row = P.pos[(d["ref"], q["n"])]
        pins.append(dict(n=q["n"], net=q["net"], x=col, y=row, **({"name": q["name"]} if "name" in q else {})))
    bn = P.pos[(d["ref"], d["pins"][0]["n"])][0]
    p = dict(d, board=bn, pins=pins, short=d["ref"].split(".")[-1], x=min(q["x"] for q in pins), y=min(q["y"] for q in pins), blk=d["blk"])
    parts.append(p)
by_ref = {p["ref"]: p for p in parts}
nets = E.nets
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
# cables entre rieles de protoboards (GND, 5 V, 12 V)
for n, xs in (("0", (-2, -2)), ("v5", (-3, -3)), ("vm", (13, 13))):
    for i in range(1, len(BL)):
        ya, yb = P.rail_y(BL[0], xs[0], 1 + 2 * i), P.rail_y(BL[i], xs[1], 1 + 2 * i)
        W.append(dict(i=len(W) + 1, net=n, color=nets[n]["color"], kind="bus", a=dict(board=BL[0], x=xs[0], y=ya, hole=hole(BL[0], xs[0], ya)),
                      b=dict(board=BL[i], x=xs[1], y=yb, hole=hole(BL[i], xs[1], yb))))
import ruteo_bajo
NIV = ruteo_bajo.rutear(W, parts, offs)
print("niveles de altura usados:", NIV)
gnd = {b: dict(x=-2, y=3) for b in BL}
titles = {b: "PROTOBOARD %s · 830 puntos" % b for b in BL}
data = dict(parts=parts, wires=W, tracks=[], zones=[], nets=nets, meas=E.MEAS, offs=offs, dims=dims, gnd=gnd, cu={b: "" for b in BL}, power=E.POWER, cell=1.27, pitch=2.54, w_trace=.8, w_wide=1.6,
            sim=E.datos_sim(), titles=titles, boards_list=BL, blocks={})
tpl = open(os.path.join(AQUI, "plantilla_proto3d.html"), encoding="utf-8").read()
three = open(os.path.join(PROY, "montaje3d", "lib3d", "three.min.js"), encoding="utf-8").read()
orbit = open(os.path.join(PROY, "montaje3d", "lib3d", "OrbitControls.js"), encoding="utf-8").read()
html = tpl.replace("/*__THREE__*/", three).replace("/*__ORBIT__*/", orbit).replace("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
open(OUT, "w", encoding="utf-8").write(html)
print("ok:", len(BL), "protoboards,", len(parts), "piezas,", len(W), "cables ->", OUT)
